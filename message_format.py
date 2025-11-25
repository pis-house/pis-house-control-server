from abc import ABC, abstractmethod


class IFormatSender(ABC):
    @abstractmethod
    def to_string(self) -> str:
        pass


class InfraredFormatSender(IFormatSender):
    TYPE = "infrared"

    def __init__(self, address: str, command: str):
        self.address = address
        self.command = command

    def to_string(self) -> str:
        return f"{self.TYPE},{self.address},{self.command}"


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


class StatusValueFormatReader(IFormatReader):
    TYPE = "status-value"

    def __init__(self, status_value: int):
        self.status_value = status_value

    @classmethod
    def from_list(cls, raw_list: list[str]):
        return cls(status_value=int(raw_list[1]))


def parse_format_reader(message: str) -> IFormatReader:
    message_list = message.split(",")
    if message_list[0] == "rssi":
        return RssiFormatReader.from_list(message_list)

    if message_list[0] == "status-value":
        return StatusValueFormatReader.from_list(message_list)
