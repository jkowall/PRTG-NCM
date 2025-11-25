import unittest
from unittest.mock import patch, MagicMock
from app import create_app, db
from app.models import NetworkDevice, ConfigurationBackup
from app.tasks import backup_device_config

class TestBackup(unittest.TestCase):
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

    @patch('ncm.drivers.cisco_ios.ConnectHandler')
    def test_backup_cisco(self, mock_connect_handler):
        # Setup mock
        mock_ssh = MagicMock()
        mock_ssh.send_command.return_value = "hostname Router1\ninterface GigabitEthernet0/0"
        mock_connect_handler.return_value.__enter__.return_value = mock_ssh

        # Create device
        device = NetworkDevice(
            hostname='Router1',
            ip_address='192.168.1.1',
            vendor='cisco_ios',
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
        self.assertIn("hostname Router1", backup.content)

if __name__ == '__main__':
    unittest.main()
