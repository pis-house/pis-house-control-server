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

        # 最初にfirebaseから値をセット
        set_share_data_done.wait()

        upd_server = UdpServer(
            ip=network_config_info.ip,
            port=9000,
            event_queue=event_queue,
            lock=lock,
            ip_to_share_data=ip_to_share_data,
        )
        upd_server.start()

        while True:
            task = event_queue.get()
            print(f"Event detected [host: {task.ip}, event_name: {task.name}]")

            if task.name == task_event.SEND_ESP32_DEVICE_TOGGLE:
                UdpClient.send(
                    # todo: addressとcommandは後で実際の値を入れる
                    target_ip=task.ip,
                    target_port=9000,
                    format_sender=message_format.InfraredFormatSender(
                        address="", command=""
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
            else:
                print("An unexpected event occurred.")

    except Exception as e:
        print(f"エラー: {e}")
