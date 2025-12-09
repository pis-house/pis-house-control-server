class InfraredData:
    def __init__(self, address: str, command: str, protocol: str):
        self.address = address
        self.command = command
        self.protocol = protocol


class ShareData:
    def __init__(
        self,
        aircon_temperature: float,
        device_type: str,
        id: str,
        is_active: bool,
        light_brightness_percent: int,
        rssi: float,
        infrared: dict[str, InfraredData],
    ):
        self.id = id
        self.aircon_temperature = aircon_temperature
        self.device_type = device_type
        self.id = id
        self.is_active = is_active
        self.light_brightness_percent = light_brightness_percent
        self.rssi = rssi
        self.infrared = infrared
