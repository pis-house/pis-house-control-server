import socket
import message_format
from message_format import RssiFormatReader, StatusValueFormatReader
import threading
from share_data import ShareData
from threading import Lock



class UdpServer(threading.Thread):
    BUFFER_SIZE = 1024
    
    def __init__(self, ip: str, port: int, lock: Lock, ip_to_share_data: dict[str, ShareData]):
        self.ip = ip
        self.port = port
        self.lock = lock
        self.ip_to_share_data = ip_to_share_data
    
    def run(self):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind((self.ip, self.port))
        try:
            while True:
                data, address = udp_socket.recvfrom(self.BUFFER_SIZE)
                message = data.decode('utf-8')
                ip = address[0]
                format_reader = message_format.parse_format_reader(message)
                
                if isinstance(format_reader, RssiFormatReader):
                    with self.lock:
                        share_data = self.ip_to_share_data.get(ip)
                        share_data.rssi = format_reader.rssi
                
                if isinstance(format_reader, StatusValueFormatReader):
                    with self.lock:
                        share_data = self.ip_to_share_data.get(ip)
                        share_data.is_active = bool(format_reader.status_value)
                

        except socket.timeout:
            pass
        except Exception as e:
            print(f"受信エラー: {e}")
        finally:
            udp_socket.close()