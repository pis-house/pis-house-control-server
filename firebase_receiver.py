from share_data import ShareData, InfraredData
from threading import Lock
from firebase_admin import firestore
import queue
import task_event
import threading
from app_data import AppData


class FirebaseReceiver:
    def __init__(
        self,
        event_queue: queue.Queue[task_event.TaskEvent],
        lock: Lock,
        ip_to_share_data: dict[str, ShareData],
        set_share_data_done: threading.Event,
    ):
        self.set_share_data_done = set_share_data_done
        self.event_queue = event_queue
        self.lock = lock
        self.ip_to_share_data = ip_to_share_data

    def start(self):
        print("Started FirebaseReceiver monitoring")
        doc_ref = (
            firestore.client()
            .collection("setup")
            .document(AppData.APP_UUID)
            .collection("devices")
        )
        doc_ref.on_snapshot(self._on_snapshot)

    def _on_snapshot(self, doc_snapshot, _changes, _read_time):
        if len(self.ip_to_share_data) == 0:
            for doc in doc_snapshot:
                data = doc.to_dict()
                infrared_collection = (
                    firestore.client()
                    .collection("setup")
                    .document(AppData.APP_UUID)
                    .collection("devices")
                    .document(data["id"])
                    .collection("infrared")
                ).get()

                infrared_dict: dict[str, InfraredData] = {}
                for doc in infrared_collection:
                    data = doc.to_dict()
                    infrared_dict[doc.id] = InfraredData(
                        data["command"], data["address"]
                    )

                try:
                    self.ip_to_share_data[data["ip"]] = ShareData(
                        aircon_temperature=data["aircon_temperature"],
                        id=doc.id,
                        is_active=data["is_active"],
                        light_brightness_percent=data["light_brightness_percent"],
                        rssi=0,
                        infrared=infrared_dict,
                    )
                except:
                    print(doc.id)

            for data in self.ip_to_share_data:
                for key in data.infrared:
                    value = data.infrared[key]
                    print(key, value.address, value.command)

            self.set_share_data_done.set()
            print(
                f"IP addresses from initial data {list(self.ip_to_share_data.keys())}"
            )

        for doc in doc_snapshot:
            device = doc.to_dict()
            share_data = self.ip_to_share_data.get(device["ip"])
            print(f"Received data [host: firebase, is_active: {device['is_active']}]")
            if share_data is not None:
                if share_data.is_active != device["is_active"]:
                    with self.lock:
                        print(
                            f"Updating ip_to_share_data [key: {device['ip']}, target_value: is_active, old: {share_data.is_active}, new: {device['is_active']}]"
                        )
                        share_data.is_active = device["is_active"]
                        self.event_queue.put(
                            task_event.TaskEvent(
                                ip=device["ip"],
                                name=task_event.SEND_ESP32_DEVICE_TOGGLE,
                            )
                        )
