from .base import BaseDriver
from netmiko import ConnectHandler
import logging

class CiscoIOSDriver(BaseDriver):
    def get_config(self):
        """
        Connects to the Cisco IOS device and retrieves the running configuration.
        """
        device_params = {
            'device_type': 'cisco_ios',
            'host': self.device.ip_address,
            'username': self.device.username,
            'password': self.device.password_encrypted, # In real app, decrypt this!
            'secret': self.device.enable_secret_encrypted, # In real app, decrypt this!
        }
        
        # Handle SSH vs Telnet
        if self.device.protocol.lower() == 'telnet':
            device_params['device_type'] = 'cisco_ios_telnet'

        try:
            with ConnectHandler(**device_params) as net_connect:
                net_connect.enable()
                # Retrieve running config
                running_config = net_connect.send_command("show running-config")
                return running_config
        except Exception as e:
            logging.error(f"Failed to connect to {self.device.hostname}: {e}")
            raise
