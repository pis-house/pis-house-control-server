import threading
from udp_server import UdpServer
from udp_client import UdpClient
from share_data import ShareData
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import os
from network_config_info import NetworkConfigInfo
import queue
import task_event
from firebase_receiver import FirebaseReceiver
import message_format
from app_data import AppData
import infrared_pattern
import device_type
import ulid
import datetime

if __name__ == "__main__":
    try:
        load_dotenv()
        cred = credentials.Certificate(os.getenv("FIREBASE_ADMIN_SDK_PATH"))
        app_uuid_text_path = os.getenv("APP_UUID_TEXT_PATH")
        firebase_admin.initialize_app(cred)

        with open(app_uuid_text_path, "r", encoding="utf-8") as f:
            content = f.read()
            AppData.APP_UUID = content.strip()

        ip_to_share_data: dict[str, ShareData] = {}
        lock = threading.Lock()
        event_queue: queue.Queue[task_event.TaskEvent] = queue.Queue()
        set_share_data_done = threading.Event()

        network_config_info = NetworkConfigInfo()
        if not network_config_info.set_config():
            raise Exception("ネットワーク情報が取得できませんでした。")

        firebase_receiver = FirebaseReceiver(
            event_queue=event_queue,
            lock=lock,
            ip_to_share_data=ip_to_share_data,
            set_share_data_done=set_share_data_done,
        )
        firebase_receiver.start()

        # 最初にfirebaseから値がセットされるまで待機
        set_share_data_done.wait()

        upd_server = UdpServer(
            ip=network_config_info.ip,
            port=9000,
            event_queue=event_queue,
            lock=lock,
            ip_to_share_data=ip_to_share_data,
        )
        upd_server.start()

        # 複数のESP32でビーコンが検知されているかのステータスを保持する
        is_latest_multiple_ble_presence = True

        while True:
            task = event_queue.get()
            print(f"Event detected [host: {task.ip}, event_name: {task.name}]")

            if task.name == task_event.SEND_ESP32_DEVICE_TOGGLE:
                target_device = ip_to_share_data[task.ip]
                infrared_on = target_device.infrared[
                    infrared_pattern.LIGHT_ON
                    if device_type.LIGHT == target_device.device_type
                    else infrared_pattern.AIRCON_HEAT
                ]

                infrared_off = target_device.infrared[
                    infrared_pattern.LIGHT_OFF
                    if device_type.LIGHT == target_device.device_type
                    else infrared_pattern.AIRCON_STOP
                ]

                infrared = infrared_on if target_device.is_active else infrared_off

                UdpClient.send(
                    target_ip=task.ip,
                    target_port=9000,
                    format_sender=message_format.InfraredFormatSender(
                        address=infrared.address,
                        command=infrared.command,
                        protocol=infrared.protocol,
                        custom_process=infrared.custom_process,
                    ),
                )
            elif task.name == task_event.UPDATE_FIREBASE_DEVICE_TOGGLE:
                (
                    firestore.client()
                    .collection("setup")
                    .document(AppData.APP_UUID)
                    .collection("devices")
                    .document(ip_to_share_data[task.ip].id)
                    .update({"is_active": ip_to_share_data[task.ip].is_active})
                )
            elif task.name == task_event.FIREBASE_NOTICE_JUDLE_AND_CREATE:
                is_multiple_ble_presence = any(
                    item.is_ble_presence for item in ip_to_share_data.values()
                )

                print("ああああああああああああああああ")
                print(is_multiple_ble_presence, is_latest_multiple_ble_presence)
                if is_multiple_ble_presence != is_latest_multiple_ble_presence:
                    is_latest_multiple_ble_presence = is_multiple_ble_presence

                    id = str(ulid.new())
                    firestore.client().collection("tenants").document(
                        AppData.APP_UUID
                    ).collection("notifications").document(id).set(
                        {
                            "id": id,
                            "title": "麻生が帰宅しました",
                            "type": "going_home"
                            if is_multiple_ble_presence
                            else "going_out",
                            "created_at": datetime.datetime.now().isoformat(),
                        }
                    )
            else:
                print("An unexpected event occurred.")

    except Exception as e:
        print(f"エラー: {e}")
