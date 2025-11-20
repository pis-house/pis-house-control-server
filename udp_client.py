import socket
from message_format import IFormatSender

class UdpClient:    
    @staticmethod
    def send(target_ip: str, target_port: int, format_sender: IFormatSender):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        try:
            sock.sendto(format_sender.to_string().encode('utf-8'), (target_ip, target_port))
        except Exception as e:
            print(f"エラーが発生しました: {e}")
        finally:
            sock.close()