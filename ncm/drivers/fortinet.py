from .base import BaseDriver
from netmiko import ConnectHandler
import logging

class FortinetDriver(BaseDriver):
    def get_config(self):
        device_params = {
            'device_type': 'fortinet',
            'host': self.device.ip_address,
            'username': self.device.username,
            'password': self.device.password_encrypted,
        }
        
        try:
            with ConnectHandler(**device_params) as net_connect:
                # Fortinet uses 'show full-configuration' or 'show'
                running_config = net_connect.send_command("show full-configuration")
                return running_config
        except Exception as e:
            logging.error(f"Failed to connect to {self.device.hostname}: {e}")
            raise
