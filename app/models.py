from app import db
from datetime import datetime

class NetworkDevice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(64), index=True, unique=True)
    ip_address = db.Column(db.String(64), index=True)
    vendor = db.Column(db.String(64))
    protocol = db.Column(db.String(10))
    username = db.Column(db.String(64))
    password_encrypted = db.Column(db.String(128))
    enable_secret_encrypted = db.Column(db.String(128))
    backups = db.relationship('ConfigurationBackup', backref='device', lazy='dynamic')

    def __repr__(self):
        return f'<NetworkDevice {self.hostname}>'

class ConfigurationBackup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('network_device.id'))
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return f'<ConfigurationBackup {self.id} for Device {self.device_id}>'
