from .base import BaseDriver
from netmiko import ConnectHandler
import logging

class UbiquitiEdgeOSDriver(BaseDriver):
    """
    Driver for Ubiquiti EdgeSwitch/EdgeRouter configuration backups via SSH.
    
    EdgeOS is based on Vyatta/VyOS and uses a similar command structure.
    
    Note: If terminal paging causes issues with "More" prompts on EdgeSwitches,
    disable it with: 'terminal length 0' or configure 'set system login user <name> level admin'
    """
    
    def get_config(self):
        """
        Connects to the EdgeSwitch/EdgeRouter device and retrieves the running configuration.
        """
        device_params = {
            'device_type': 'ubiquiti_edgerouter',
            'host': self.device.ip_address,
            'username': self.device.username,
            'password': self.device.password_encrypted,  # In real app, decrypt this!
        }
        
        # Handle SSH vs Telnet
        if self.device.protocol.lower() == 'telnet':
            device_params['device_type'] = 'ubiquiti_edgerouter_telnet'
        
        try:
            with ConnectHandler(**device_params) as net_connect:
                # Disable paging to avoid "More" prompts
                net_connect.send_command("terminal length 0")
                
                # Retrieve running configuration
                # EdgeOS uses 'show configuration' or 'show configuration commands'
                # 'show configuration commands' provides output in set-command format
                running_config = net_connect.send_command("show configuration commands")
                
                return running_config
        except Exception as e:
            logging.error(f"Failed to connect to {self.device.hostname}: {e}")
            raise
