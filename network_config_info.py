import netifaces # type: ignore

class NetworkConfigInfo:
    def __init__(self):
        self.ip = None
        self.subnet = None
        self.gateway = None
    
    def set_config(self, ifname='wlan0'):
        if ifname in netifaces.interfaces():
            addresses = netifaces.ifaddresses(ifname)
            if netifaces.AF_INET in addresses:
                ipv4_info = addresses[netifaces.AF_INET][0]
                self.ip = ipv4_info.get('addr')
                self.subnet = ipv4_info.get('netmask')
     
                gws = netifaces.gateways()
                if 'default' in gws and netifaces.AF_INET in gws['default']:
                    gateway_info = gws['default'][netifaces.AF_INET]
                    if gateway_info[1] == ifname:
                        self.gateway = gateway_info[0]
                        
                        return True
        
        return False