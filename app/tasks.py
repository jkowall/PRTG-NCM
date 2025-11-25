from app import celery, db
from app.models import NetworkDevice, ConfigurationBackup
from ncm.drivers.factory import get_driver
import logging
from datetime import datetime

@celery.task
def backup_device_config(device_id):
    """
    Background task to backup configuration for a specific device.
    """
    logging.info(f"Starting backup for device_id: {device_id}")
    device = NetworkDevice.query.get(device_id)
    if not device:
        logging.error(f"Device with id {device_id} not found.")
        return "Device not found"

    try:
        driver = get_driver(device)
        config_content = driver.get_config()
        
        # Sanitize config (basic example)
        # In a real app, use regex to remove secrets/timestamps
        
        backup = ConfigurationBackup(
            device_id=device.id,
            content=config_content,
            timestamp=datetime.utcnow()
        )
        db.session.add(backup)
        db.session.commit()
        logging.info(f"Backup completed for {device.hostname}")
        return "Backup successful"
    except Exception as e:
        logging.error(f"Backup failed for {device.hostname}: {e}")
        return f"Backup failed: {str(e)}"
