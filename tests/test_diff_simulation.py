import unittest
from app import create_app, db
from app.models import NetworkDevice, ConfigurationBackup
from ncm.diff_engine import compare_configs

class TestDiffSimulation(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_simulate_device_change(self):
        """
        Simulate a device configuration change and verify the diff output.
        """
        print("\n--- Starting Diff Simulation ---")

        # 1. Create a Mock Device
        device = NetworkDevice(
            hostname='SimulatedRouter',
            ip_address='10.0.0.1',
            vendor='cisco_ios',
            protocol='ssh',
            username='admin',
            password_encrypted='secret'
        )
        db.session.add(device)
        db.session.commit()
        print(f"Created device: {device.hostname}")

        # 2. Create Initial Configuration
        config_v1 = """! Initial Configuration
hostname SimulatedRouter
!
interface GigabitEthernet0/0
 ip address 10.0.0.1 255.255.255.0
!
end
"""
        backup_v1 = ConfigurationBackup(
            device_id=device.id,
            content=config_v1
        )
        db.session.add(backup_v1)
        db.session.commit()
        print("Created initial configuration backup.")

        # 3. Create Changed Configuration
        config_v2 = """! Changed Configuration
hostname SimulatedRouter
!
interface GigabitEthernet0/0
 ip address 10.0.0.1 255.255.255.0
 description Uplink to Core
!
interface Loopback0
 ip address 1.1.1.1 255.255.255.255
!
end
"""
        backup_v2 = ConfigurationBackup(
            device_id=device.id,
            content=config_v2
        )
        db.session.add(backup_v2)
        db.session.commit()
        print("Created changed configuration backup.")

        # 4. Generate Diff
        print("Generating diff...")
        diff_html = compare_configs(backup_v1.content, backup_v2.content)

        # 5. Verify Diff Content
        # Note: difflib.HtmlDiff replaces spaces with &nbsp;
        self.assertIn('description&nbsp;Uplink&nbsp;to&nbsp;Core', diff_html)
        self.assertIn('interface&nbsp;Loopback0', diff_html)
        self.assertIn('class="diff_add"', diff_html) # Check for HTML class indicating addition
        
        print("Diff generated successfully.")
        print("Simulation complete.")

if __name__ == '__main__':
    unittest.main()
