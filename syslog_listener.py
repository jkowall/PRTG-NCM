import socket
import re
import logging
from app import create_app
from app.models import NetworkDevice
from app.tasks import backup_device_config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Regex for Cisco config change
# Example: %SYS-5-CONFIG_I: Configured from console by console
CONFIG_CHANGE_PATTERN = re.compile(r'%SYS-5-CONFIG_I')

def process_syslog_message(message, source_ip, app):
    """
    Process a single syslog message. Returns True if a backup was triggered.
    """
    if CONFIG_CHANGE_PATTERN.search(message):
        logging.info(f"Config change detected from {source_ip}")
        
        with app.app_context():
            device = NetworkDevice.query.filter_by(ip_address=source_ip).first()
            if device:
                logging.info(f"Triggering backup for device {device.hostname} ({device.ip_address})")
                backup_device_config.delay(device.id)
                return True
            else:
                logging.warning(f"Device with IP {source_ip} not found in inventory.")
    return False

def start_syslog_listener(host='0.0.0.0', port=514):
    app = create_app()
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind((host, port))
    except PermissionError:
        logging.error(f"Permission denied to bind to port {port}. Try running with sudo or use a port > 1024.")
        return

    logging.info(f"Syslog listener started on {host}:{port}")

    while True:
        try:
            data, addr = sock.recvfrom(1024)
            message = data.decode('utf-8', errors='ignore')
            source_ip = addr[0]
            
            process_syslog_message(message, source_ip, app)

        except Exception as e:
            logging.error(f"Error processing message: {e}")

if __name__ == "__main__":
    # Allow port to be configured via env var or arg, but default to 514
    # Note: Binding to 514 requires root on most systems.
    import sys
    port = 514
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    start_syslog_listener(port=port)
