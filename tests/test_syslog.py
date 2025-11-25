import unittest
from unittest.mock import patch, MagicMock
from app import create_app, db
from app.models import NetworkDevice
from syslog_listener import process_syslog_message

class TestSyslogListener(unittest.TestCase):
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

    @patch('syslog_listener.backup_device_config')
    def test_process_syslog_message_trigger(self, mock_backup_task):
        # Create device
        device = NetworkDevice(
            hostname='Router1',
            ip_address='192.168.1.1',
            vendor='cisco_ios',
            protocol='ssh'
        )
        db.session.add(device)
        db.session.commit()

        # Simulate syslog message
        message = "<189>29: %SYS-5-CONFIG_I: Configured from console by console"
        source_ip = '192.168.1.1'

        triggered = process_syslog_message(message, source_ip, self.app)

        self.assertTrue(triggered)
        mock_backup_task.delay.assert_called_with(device.id)

    @patch('syslog_listener.backup_device_config')
    def test_process_syslog_message_no_trigger(self, mock_backup_task):
        message = "Just a normal log message"
        source_ip = '192.168.1.1'
        
        triggered = process_syslog_message(message, source_ip, self.app)
        
        self.assertFalse(triggered)
        mock_backup_task.delay.assert_not_called()

if __name__ == '__main__':
    unittest.main()
