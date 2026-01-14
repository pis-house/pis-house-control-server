import socket
import message_format
from message_format import RssiFormatReader, BlePresenceFormatReader
import threading
from share_data import ShareData
from threading import Lock
import queue
import task_event


class UdpServer(threading.Thread):
    BUFFER_SIZE = 1024

    def __init__(
        self,
        ip: str,
        port: int,
        event_queue: queue.Queue[task_event.TaskEvent],
        lock: Lock,
        ip_to_share_data: dict[str, ShareData],
    ):
        super().__init__()
        self.ip = ip
        self.port = port
        self.event_queue = event_queue
        self.lock = lock
        self.ip_to_share_data = ip_to_share_data
        self.daemon = True
        self.rssi_buffer: list[float] = []

    def run(self):
        print("Started UdpServer monitoring")
        print("ip: ", self.ip)
        print("port: ", self.port)
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind((self.ip, self.port))
        try:
            while True:
                data, address = udp_socket.recvfrom(self.BUFFER_SIZE)
                message = data.decode("utf-8")
                ip = address[0]
                format_reader = message_format.parse_format_reader(message)

                if isinstance(format_reader, RssiFormatReader):
                    with self.lock:
                        # print(f"Received data [host: {ip}, rssi: {format_reader.rssi}]")
                        share_data = self.ip_to_share_data.get(ip)

                        if share_data.rssi != format_reader.rssi:
                            # print(
                            #     f"Updating ip_to_share_data [key: {ip}, target_value: rssi, old: {share_data.rssi}, new: {format_reader.rssi}]"
                            # )
                            share_data.rssi = format_reader.rssi

                        self.rssi_buffer.append(format_reader.rssi)
                        if len(self.rssi_buffer) == 10:
                            print(share_data.device_name, self.rssi_buffer)
                            sorted_buffer = sorted(self.rssi_buffer)
                            trimmed_buffer = sorted_buffer[1:-1]
                            avg_rssi = sum(trimmed_buffer) / len(trimmed_buffer)
                            self.rssi_buffer = []
                            new_is_active = False
                            if avg_rssi <= 60:
                                new_is_active = True
                            if new_is_active != share_data.is_active:
                                share_data.is_active = new_is_active

                                self.event_queue.put(
                                    task_event.TaskEvent(
                                        ip=ip,
                                        name=task_event.UPDATE_FIREBASE_DEVICE_TOGGLE,
                                    )
                                )

                                self.event_queue.put(
                                    task_event.TaskEvent(
                                        ip=ip,
                                        name=task_event.SEND_ESP32_DEVICE_TOGGLE,
                                    )
                                )

                if isinstance(format_reader, BlePresenceFormatReader):
                    with self.lock:
                        print(
                            f"Received data [host: {ip}, ble_presence: {format_reader.ble_presence}]"
                        )
                        share_data = self.ip_to_share_data.get(ip)

                        if share_data.is_ble_presence != format_reader.ble_presence:
                            print(
                                f"Updating ip_to_share_data [key: {ip}, target_value: is_ble_presence, old: {share_data.is_ble_presence}, new: {format_reader.ble_presence}]"
                            )
                            share_data.is_ble_presence = format_reader.ble_presence

                            self.event_queue.put(
                                task_event.TaskEvent(
                                    ip=ip,
                                    name=task_event.FIREBASE_NOTICE_JUDLE_AND_CREATE,
                                )
                            )

        except socket.timeout:
            pass
        except Exception as e:
            print(f"受信エラー: {e}")
        finally:
            udp_socket.close()
