import requests
import time
import socket
from app import create_app, db
from app.models import NetworkDevice, ConfigurationBackup

def verify_flow():
    base_url = "http://127.0.0.1:5001"
    
    # 1. Add Device
    print("1. Adding Device...")
    device_data = {
        "hostname": "VerifyRouter",
        "ip_address": "127.0.0.1",
        "vendor": "mock",
        "protocol": "ssh",
        "username": "admin",
        "password": "password",
        "secret": "secret"
    }
    # Flask form uses POST with data, not JSON
    response = requests.post(f"{base_url}/add_device", data=device_data)
    if response.status_code == 200:
        print("   Device added successfully.")
    else:
        print(f"   Failed to add device. Status: {response.status_code}")
        return

    # 2. Send Syslog Trigger
    print("2. Sending Syslog Trigger...")
    msg = "<189>29: %SYS-5-CONFIG_I: Configured from console by console"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(msg.encode('utf-8'), ("127.0.0.1", 5140))
    print("   Syslog message sent.")

    # 3. Wait for Celery
    print("3. Waiting for backup task (5s)...")
    time.sleep(5)

    # 4. Verify Backup in DB
    print("4. Verifying Backup...")
    app = create_app()
    with app.app_context():
        device = NetworkDevice.query.filter_by(hostname="VerifyRouter").first()
        if not device:
            print("   Error: Device not found in DB.")
            return
        
        backups = ConfigurationBackup.query.filter_by(device_id=device.id).all()
        if backups:
            print(f"   Success! Found {len(backups)} backup(s) for {device.hostname}.")
            print(f"   Latest backup timestamp: {backups[0].timestamp}")
        else:
            print("   Failure: No backups found. Check Celery logs.")

if __name__ == "__main__":
    # Wait for services to fully start
    time.sleep(3)
    try:
        verify_flow()
    except Exception as e:
        print(f"Verification failed: {e}")
