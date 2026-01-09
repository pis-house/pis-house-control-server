# タスクイベント名一覧
SEND_ESP32_DEVICE_TOGGLE = "send-esp32-device-toggle"
UPDATE_FIREBASE_DEVICE_TOGGLE = "update-firebase-device-toggle"
FIREBASE_NOTICE_JUDLE_AND_CREATE = "firebase-notice-judle-and-create"


class TaskEvent:
    def __init__(self, ip: str, name: str):
        self.ip = ip
        self.name = name
