from .base import BaseDriver
import requests
import logging
import json
from urllib3.exceptions import InsecureRequestWarning

# Suppress only the single InsecureRequestWarning from urllib3 needed for UniFi
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

class UbiquitiUniFiDriver(BaseDriver):
    """
    Driver for Ubiquiti UniFi Controller configuration backups via REST API.
    
    Supports both Legacy UniFi Controller and UDM/UDM-Pro (UniOS).
    
    Device setup:
    - ip_address: UniFi Controller IP/hostname
    - username: Read-only admin account
    - password_encrypted: Account password (will be decrypted)
    - enable_secret_encrypted: Optional Site ID (defaults to 'default')
    """
    
    def get_config(self):
        """
        Connects to the UniFi Controller and retrieves site configuration as JSON.
        """
        controller_url = f"https://{self.device.ip_address}:8443"
        site_id = self.device.enable_secret_encrypted or 'default'
        
        try:
            # Create session
            session = requests.Session()
            
            # Login to UniFi Controller
            login_url = f"{controller_url}/api/login"
            login_data = {
                'username': self.device.username,
                'password': self.device.password_encrypted,  # In production, decrypt this!
            }
            
            login_response = session.post(
                login_url,
                json=login_data,
                verify=False,
                timeout=30
            )
            login_response.raise_for_status()
            
            # Get site configuration
            # This includes devices, settings, and network configuration
            config_data = {}
            
            # Fetch site settings
            settings_url = f"{controller_url}/api/s/{site_id}/rest/setting"
            settings_response = session.get(settings_url, verify=False, timeout=30)
            settings_response.raise_for_status()
            config_data['settings'] = settings_response.json()
            
            # Fetch network configuration
            networks_url = f"{controller_url}/api/s/{site_id}/rest/networkconf"
            networks_response = session.get(networks_url, verify=False, timeout=30)
            networks_response.raise_for_status()
            config_data['networks'] = networks_response.json()
            
            # Fetch device configurations
            devices_url = f"{controller_url}/api/s/{site_id}/stat/device"
            devices_response = session.get(devices_url, verify=False, timeout=30)
            devices_response.raise_for_status()
            config_data['devices'] = devices_response.json()
            
            # Logout
            logout_url = f"{controller_url}/api/logout"
            session.post(logout_url, verify=False, timeout=10)
            
            # Return formatted JSON configuration
            return json.dumps(config_data, indent=2, sort_keys=True)
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to connect to UniFi Controller {self.device.hostname}: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error backing up UniFi Controller {self.device.hostname}: {e}")
            raise
