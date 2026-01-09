# Ubiquiti Device Setup Guide

This guide provides detailed instructions for configuring Ubiquiti UniFi Controllers and EdgeOS devices for use with the Paessler NCM module.

## Table of Contents
- [UniFi Controller Setup](#unifi-controller-setup)
- [EdgeOS Device Setup](#edgeos-device-setup)
- [Troubleshooting](#troubleshooting)

---

## UniFi Controller Setup

### Prerequisites
- UniFi Controller (Legacy Software Controller, UDM, or UDM-Pro)
- Network access to the Controller on port 8443 (HTTPS)
- Administrative access to create a read-only user

### Creating a Read-Only Administrator Account

The NCM script requires a dedicated read-only administrator account to access the UniFi Controller API without making changes to your network configuration.

#### Steps:

1. **Log in to your UniFi Controller** web interface.

2. **Navigate to Settings → Admins** (or Users & Roles in newer versions).

3. **Add a new Admin**:
   - **Name**: `ncm-backup` (or your preferred name)
   - **Role**: Select **Read Only** or create a custom role with read-only permissions
   - **Email**: (optional)
   - **Password**: Create a strong password

4. **Save the account** and note the credentials.

### Adding UniFi Controller to NCM

When adding the UniFi Controller device to the NCM inventory:

- **Hostname**: Friendly name (e.g., "Main-UniFi-Controller")
- **IP Address**: Controller IP or hostname (e.g., `192.168.1.10` or `unifi.local`)
- **Vendor**: `ubiquiti_unifi` or `unifi`
- **Protocol**: `ssh` (not used for API, but required field)
- **Username**: The read-only admin username (e.g., `ncm-backup`)
- **Password**: The read-only admin password
- **Enable Secret/Site ID**: (Optional) UniFi Site ID - defaults to `default` if not specified

### Understanding Site IDs

UniFi Controllers can manage multiple sites. The Site ID is used in API calls to specify which site to back up.

- **Default site**: Use `default` or leave blank
- **Custom sites**: Find the Site ID in the Controller URL when viewing that site
  - Example: `https://192.168.1.10:8443/manage/site/office-branch`
  - Site ID: `office-branch`

### API Differences: UDM/UDM-Pro vs. Legacy Controller

#### Legacy UniFi Controller (v5.x - v7.x)
- Runs on dedicated hardware or Cloud Key
- API endpoint: `https://<controller-ip>:8443/api/`
- Self-signed certificates are common

#### UDM/UDM-Pro (UniOS)
- Integrated controller on Dream Machine devices
- API endpoint: `https://<udm-ip>/proxy/network/api/`
- May require different authentication flow in future updates

**Note**: The current driver supports Legacy Controllers. UDM/UDM-Pro support may require minor adjustments to the API endpoints if issues arise.

---

## EdgeOS Device Setup

### Supported Devices
- EdgeRouter (ER-4, ER-6P, ER-X, etc.)
- EdgeSwitch (ES-24, ES-48, etc.)

### Prerequisites
- SSH access enabled on the device
- User account with admin privileges

### Disabling Terminal Paging

EdgeOS devices may use terminal paging, which displays "More" prompts during long command outputs. This can interfere with automated backups.

#### Method 1: Disable Paging Per-Session (Automatic)
The NCM driver automatically sends `terminal length 0` to disable paging for the session.

#### Method 2: Disable Paging Permanently (Recommended for EdgeSwitches)

1. **SSH into the device**:
   ```bash
   ssh admin@192.168.1.1
   ```

2. **Enter configuration mode**:
   ```bash
   configure
   ```

3. **Set terminal length for the user**:
   ```bash
   set system login user admin level admin
   commit
   save
   exit
   ```

### Adding EdgeOS Devices to NCM

When adding an EdgeRouter or EdgeSwitch to the NCM inventory:

- **Hostname**: Friendly name (e.g., "Office-EdgeRouter")
- **IP Address**: Device IP address
- **Vendor**: `ubiquiti_edgeos`, `edgerouter`, or `edgeswitch`
- **Protocol**: `ssh` (recommended) or `telnet` (if SSH is unavailable)
- **Username**: Admin username
- **Password**: Admin password
- **Enable Secret**: (Leave blank - not used for EdgeOS)

### Configuration Backup Format

EdgeOS configuration backups use the **set-command format**, which displays the configuration as a series of `set` commands:

```bash
set interfaces ethernet eth0 address '192.168.1.1/24'
set interfaces ethernet eth0 description 'WAN'
set system host-name 'EdgeRouter'
set system ntp server 0.ubnt.pool.ntp.org
...
```

This format is ideal for version control and change detection.

---

## Troubleshooting

### UniFi Controller Issues

#### Problem: "Connection refused" or "Timeout"
- **Solution**: Verify the Controller IP address and ensure port 8443 is accessible.
- Check firewall rules on the Controller and NCM server.

#### Problem: "401 Unauthorized"
- **Solution**: Verify the username and password are correct.
- Ensure the account has at least read-only permissions.

#### Problem: "Invalid Site ID"
- **Solution**: Check the Site ID in the Controller URL or use `default` for the main site.

#### Problem: SSL Certificate Errors
- **Solution**: The driver disables SSL verification for self-signed certificates. This is normal for UniFi Controllers.

### EdgeOS Issues

#### Problem: "More" prompts appearing in backup
- **Solution**: Ensure `terminal length 0` is being sent, or configure the user account as described in [Method 2](#method-2-disable-paging-permanently-recommended-for-edgeswitches).

#### Problem: SSH connection fails
- **Solution**: Verify SSH is enabled on the device:
  ```bash
  show service ssh
  ```
- If disabled, enable it:
  ```bash
  configure
  set service ssh port 22
  commit
  save
  ```

#### Problem: "Permission denied"
- **Solution**: Ensure the user account has admin-level privileges.

### General Tips

- **Test connectivity**: Use `ping` and `ssh` from the NCM server to the device before adding it to the inventory.
- **Check logs**: Review the Celery worker logs for detailed error messages.
- **Verify credentials**: Double-check usernames, passwords, and IP addresses.

---

## Additional Resources

- [Ubiquiti UniFi API Documentation](https://ubntwiki.com/products/software/unifi-controller/api)
- [EdgeOS Command Reference](https://help.ui.com/hc/en-us/articles/204960094-EdgeRouter-Command-Line-Interface-CLI-Basics)
- [Netmiko Supported Devices](https://github.com/ktbyers/netmiko#supports)

---

**Need Help?** Open an issue on the [GitHub repository](https://github.com/jkowall/PRTG-NCM/issues) with details about your setup and error messages.
