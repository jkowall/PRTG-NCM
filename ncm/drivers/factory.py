from .cisco_ios import CiscoIOSDriver
from .huawei_vrp import HuaweiVRPDriver
from .fortinet import FortinetDriver
from .mock_driver import MockDriver
from .ubiquiti_unifi import UbiquitiUniFiDriver
from .ubiquiti_edgeos import UbiquitiEdgeOSDriver

def get_driver(device):
    """
    Factory function to return the appropriate driver instance based on the device vendor.
    """
    vendor = device.vendor.lower()
    
    if 'cisco' in vendor:
        return CiscoIOSDriver(device)
    elif 'huawei' in vendor:
        return HuaweiVRPDriver(device)
    elif 'fortinet' in vendor:
        return FortinetDriver(device)
    elif 'ubiquiti_unifi' in vendor or 'unifi' in vendor:
        return UbiquitiUniFiDriver(device)
    elif 'ubiquiti_edgeos' in vendor or 'edgerouter' in vendor or 'edgeswitch' in vendor:
        return UbiquitiEdgeOSDriver(device)
    elif 'mock' in vendor:
        return MockDriver(device)
    else:
        raise ValueError(f"Unsupported vendor: {device.vendor}")
