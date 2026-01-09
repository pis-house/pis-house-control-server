# タスクイベント名一覧
SEND_ESP32_DEVICE_TOGGLE = "send-esp32-device-toggle"
UPDATE_FIREBASE_DEVICE_TOGGLE = "update-firebase-device-toggle"
CREATE_FIREBASE_GOING_HOME_NOTICE = "create-firebase-going-home-notice"
CREATE_FIREBASE_GOING_OUT_NOTICE = "create-firebase-going-out-notice"


class TaskEvent:
    def __init__(self, ip: str, name: str):
        self.ip = ip
        self.name = name
