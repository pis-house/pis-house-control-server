from abc import ABC, abstractmethod


class IFormatSender(ABC):
    @abstractmethod
    def to_string(self) -> str:
        pass


class InfraredFormatSender(IFormatSender):
    TYPE = "infrared"

    def __init__(self, address: str, command: str, custom_process: str, protocol: str):
        self.address = address
        self.command = command
        self.custom_process = custom_process
        self.protocol = protocol

    def to_string(self) -> str:
        return f"{self.TYPE},{self.address},{self.command},{self.custom_process},{self.protocol}"


class IFormatReader(ABC):
    @classmethod
    @abstractmethod
    def from_list(cls, raw_list: list[str]):
        pass


class RssiFormatReader(IFormatReader):
    TYPE = "rssi"

    def __init__(self, rssi: float):
        self.rssi = rssi

    @classmethod
    def from_list(cls, raw_list: list[str]):
        return cls(rssi=float(raw_list[1]))


class BlePresenceFormatReader(IFormatReader):
    TYPE = "ble-presence"

    def __init__(self, ble_presence: bool):
        self.ble_presence = ble_presence

    @classmethod
    def from_list(cls, raw_list: list[str]):
        return cls(ble_presence=bool(int(raw_list[1])))


def parse_format_reader(message: str) -> IFormatReader:
    message_list = message.split(",")
    if message_list[0] == "rssi":
        return RssiFormatReader.from_list(message_list)

    if message_list[0] == "ble-presence":
        return BlePresenceFormatReader.from_list(message_list)
