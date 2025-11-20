
class ShareData:
    def __init__(self, aircon_temperature: float, is_active: bool, light_brightness_percent: int, rssi: float):
        self.aircon_temperature = aircon_temperature
        self.is_active = is_active
        self.light_brightness_percent = light_brightness_percent
        self.rssi = rssi