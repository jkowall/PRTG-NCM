# Paessler NCM Module (MVP)

A unified Network Configuration and Change Management (NCCM) tool designed to integrate with Paessler PRTG. This module provides automated configuration backups, change detection, and compliance auditing for network devices.

## Features

- **Device Inventory**: Manage network devices with support for multiple vendors.
- **Automated Backups**: Scheduled configuration backups using Celery and Valkey.
- **Diff Engine**: Visual line-by-line comparison of configuration changes.
- **Real-Time Detection**: Syslog listener to trigger backups instantly upon config changes.
- **Multi-Vendor Support**:
    - Cisco IOS / IOS-XE
    - Huawei VRP
    - Fortinet FortiGate
    - (Extensible via Driver Factory)
- **Web Interface**: Clean, responsive UI with PRTG-inspired branding.

## Prerequisites

- Python 3.11+
- [Valkey](https://valkey.io/) (Redis fork)
- macOS / Linux environment

## Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd PRTG-NCM
    ```

2.  **Set up Virtual Environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Initialize Database**:
    ```bash
    python init_db.py
    ```

## Usage

### Starting Services

1.  **Start Valkey**:
    ```bash
    brew services start valkey
    ```

2.  **Start Celery Worker** (Background Tasks):
    ```bash
    celery -A celery_worker.celery worker --loglevel=info
    ```

3.  **Start Syslog Listener** (Real-time Detection):
    ```bash
    # Port 5140 is used for non-root access. Use 514 for production (requires sudo).
    python syslog_listener.py 5140
    ```

4.  **Start Web Server**:
    ```bash
    flask run --port 5001
    ```

Access the web interface at: `http://127.0.0.1:5001`

### Adding Devices

1.  Navigate to "Add Device".
2.  Enter the Hostname, IP, Vendor, and Credentials.
3.  The device will be added to the inventory.

### Viewing Diffs

1.  Go to the Device Detail page.
2.  Click "Run Backup Now" to create a new backup.
3.  Once multiple backups exist, click "View Diff" to see changes.

## Testing

Run the automated test suite:
```bash
PYTHONPATH=. python tests/test_backup.py
PYTHONPATH=. python tests/test_syslog.py
```

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
