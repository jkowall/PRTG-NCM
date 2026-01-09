import unittest
from unittest.mock import patch, MagicMock, Mock
from app import create_app, db
from app.models import NetworkDevice, ConfigurationBackup
from app.tasks import backup_device_config
import json

class TestUbiquitiBackup(unittest.TestCase):
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

    @patch('ncm.drivers.ubiquiti_unifi.requests.Session')
    def test_backup_unifi(self, mock_session_class):
        # Setup mock session
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Mock login response
        mock_login_response = Mock()
        mock_login_response.raise_for_status = Mock()
        mock_session.post.return_value = mock_login_response
        
        # Mock API responses
        mock_settings_response = Mock()
        mock_settings_response.raise_for_status = Mock()
        mock_settings_response.json.return_value = {
            'data': [{'key': 'mgmt', 'auto_upgrade': False}]
        }
        
        mock_networks_response = Mock()
        mock_networks_response.raise_for_status = Mock()
        mock_networks_response.json.return_value = {
            'data': [{'name': 'Corporate', 'vlan': 10}]
        }
        
        mock_devices_response = Mock()
        mock_devices_response.raise_for_status = Mock()
        mock_devices_response.json.return_value = {
            'data': [{'name': 'Switch-01', 'mac': 'aa:bb:cc:dd:ee:ff'}]
        }
        
        # Configure mock session.get to return different responses
        mock_session.get.side_effect = [
            mock_settings_response,
            mock_networks_response,
            mock_devices_response
        ]

        # Create UniFi device
        device = NetworkDevice(
            hostname='UniFi-Controller',
            ip_address='192.168.1.10',
            vendor='ubiquiti_unifi',
            protocol='ssh',  # Not used for API
            username='ncm-backup',
            password_encrypted='secret',
            enable_secret_encrypted='default'
        )
        db.session.add(device)
        db.session.commit()

        # Run backup task (synchronously for test)
        result = backup_device_config(device.id)

        # Verify
        self.assertEqual(result, "Backup successful")
        backup = ConfigurationBackup.query.filter_by(device_id=device.id).first()
        self.assertIsNotNone(backup)
        
        # Verify JSON structure
        config = json.loads(backup.content)
        self.assertIn('settings', config)
        self.assertIn('networks', config)
        self.assertIn('devices', config)

    @patch('ncm.drivers.ubiquiti_edgeos.ConnectHandler')
    def test_backup_edgeos(self, mock_connect_handler):
        # Setup mock
        mock_ssh = MagicMock()
        mock_ssh.send_command.side_effect = [
            "",  # Response to 'terminal length 0'
            "set interfaces ethernet eth0 address '192.168.1.1/24'\nset system host-name 'EdgeRouter'"
        ]
        mock_connect_handler.return_value.__enter__.return_value = mock_ssh

        # Create EdgeOS device
        device = NetworkDevice(
            hostname='EdgeRouter-01',
            ip_address='192.168.1.1',
            vendor='ubiquiti_edgeos',
            protocol='ssh',
            username='admin',
            password_encrypted='secret'
        )
        db.session.add(device)
        db.session.commit()

        # Run backup task (synchronously for test)
        result = backup_device_config(device.id)

        # Verify
        self.assertEqual(result, "Backup successful")
        backup = ConfigurationBackup.query.filter_by(device_id=device.id).first()
        self.assertIsNotNone(backup)
        self.assertIn("set interfaces ethernet eth0", backup.content)
        self.assertIn("set system host-name 'EdgeRouter'", backup.content)

    @patch('ncm.drivers.ubiquiti_edgeos.ConnectHandler')
    def test_backup_edgeswitch(self, mock_connect_handler):
        # Setup mock
        mock_ssh = MagicMock()
        mock_ssh.send_command.side_effect = [
            "",  # Response to 'terminal length 0'
            "set system host-name 'EdgeSwitch-01'\nset interfaces switch switch0 address '192.168.1.2/24'"
        ]
        mock_connect_handler.return_value.__enter__.return_value = mock_ssh

        # Create EdgeSwitch device
        device = NetworkDevice(
            hostname='EdgeSwitch-01',
            ip_address='192.168.1.2',
            vendor='edgeswitch',
            protocol='ssh',
            username='admin',
            password_encrypted='secret'
        )
        db.session.add(device)
        db.session.commit()

        # Run backup task (synchronously for test)
        result = backup_device_config(device.id)

        # Verify
        self.assertEqual(result, "Backup successful")
        backup = ConfigurationBackup.query.filter_by(device_id=device.id).first()
        self.assertIsNotNone(backup)
        self.assertIn("set system host-name 'EdgeSwitch-01'", backup.content)

if __name__ == '__main__':
    unittest.main()
