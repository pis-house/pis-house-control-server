class ShareData:
    def __init__(
        self,
        aircon_temperature: float,
        id: str,
        is_active: bool,
        light_brightness_percent: int,
        rssi: float,
    ):
        self.id = id
        self.aircon_temperature = aircon_temperature
        self.id = id
        self.is_active = is_active
        self.light_brightness_percent = light_brightness_percent
        self.rssi = rssi
