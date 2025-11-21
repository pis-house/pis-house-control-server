import threading
from udp_server import UdpServer
from udp_client import UdpClient
from share_data import ShareData
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import os
from network_config_info import NetworkConfigInfo
from google.cloud.firestore import DocumentSnapshot
import queue
from task_event import TaskEvent
from firebase_receiver import FirebaseReceiver

if __name__ == '__main__':
    try:
        load_dotenv()
        cred = credentials.Certificate(os.getenv("FIREBASE_ADMIN_SDK_PATH"))
        firebase_admin.initialize_app(cred)
        
        ip_to_share_data: dict[str, ShareData] = {}
        lock = threading.Lock()
        event_queue: queue.Queue[TaskEvent] = queue.Queue()
        set_share_data_done = threading.Event()

        network_config_info = NetworkConfigInfo()
        # if(not network_config_info.set_config()):
        #     raise Exception("ネットワーク情報が取得できませんでした。")
        
        network_config_info.ip = '172.16.201.37'
        firebase_receiver = FirebaseReceiver(event_queue=event_queue, lock=lock, ip_to_share_data=ip_to_share_data, set_share_data_done=set_share_data_done)
        firebase_receiver.start()
        
        # 最初にfirebaseから値をセット
        set_share_data_done.wait()
        
        upd_server = UdpServer(ip=network_config_info.ip, port=9000, event_queue=event_queue, lock=lock, ip_to_share_data=ip_to_share_data)
        upd_server.start()
        
        while True:
            task_event = event_queue.get()
            print(f"Event detected [host: {task_event.ip}, event_name: {task_event.name}]")
    
    except Exception as e:
        print(f"エラー: {e}")