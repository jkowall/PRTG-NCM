from app import create_app, db
from app.models import NetworkDevice, ConfigurationBackup
from datetime import datetime, timedelta

def seed_data():
    app = create_app()
    with app.app_context():
        # Ensure device exists
        device = NetworkDevice.query.filter_by(hostname="VerifyRouter").first()
        if not device:
            print("Creating device VerifyRouter...")
            device = NetworkDevice(
                hostname="VerifyRouter",
                ip_address="127.0.0.1",
                vendor="mock",
                protocol="ssh",
                username="admin",
                password_encrypted="password"
            )
            db.session.add(device)
            db.session.commit()
        
        print(f"Seeding data for device: {device.hostname}")

        # Config 1 (Older)
        config_v1 = """! Version 1
hostname VerifyRouter
!
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 description Uplink to Core
!
ip route 0.0.0.0 0.0.0.0 192.168.1.254
!
end"""

        # Config 2 (Newer - with changes)
        config_v2 = """! Version 2
hostname VerifyRouter
!
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 description Uplink to Core
!
interface GigabitEthernet0/1
 description Guest Wi-Fi Network
 ip address 10.0.0.1 255.255.255.0
!
ip route 0.0.0.0 0.0.0.0 192.168.1.254
!
end"""

        # Add Backup 1 (1 hour ago)
        backup1 = ConfigurationBackup(
            device_id=device.id,
            content=config_v1,
            timestamp=datetime.utcnow() - timedelta(hours=1)
        )
        
        # Add Backup 2 (Now)
        backup2 = ConfigurationBackup(
            device_id=device.id,
            content=config_v2,
            timestamp=datetime.utcnow()
        )

        db.session.add(backup1)
        db.session.add(backup2)
        db.session.commit()
        
        print("Successfully added 2 sample configurations.")

if __name__ == "__main__":
    seed_data()
