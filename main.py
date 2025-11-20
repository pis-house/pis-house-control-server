import threading
from udp_server import UdpServer
from udp_client import UdpClient
from share_data import ShareData
import firebase_admin
from firebase_admin import credentials
from dotenv import load_dotenv
import os

if __name__ == '__main__':
    load_dotenv()
    cred = credentials.Certificate(os.getenv("FIREBASE_ADMIN_SDK_PATH"))
    firebase_admin.initialize_app(cred)
    
    ip_to_share_data: dict[str, ShareData] = {}
    lock = threading.Lock()
    
    
    