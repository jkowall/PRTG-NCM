from .base import BaseDriver
import logging

class MockDriver(BaseDriver):
    def get_config(self):
        logging.info(f"MockDriver: Retrieving config for {self.device.hostname}")
        return f"""! Mock Configuration for {self.device.hostname}
hostname {self.device.hostname}
!
interface GigabitEthernet0/0
 ip address {self.device.ip_address} 255.255.255.0
!
end
"""
