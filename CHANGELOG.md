# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-11-25

### Added
- **Core**: Initial MVP release of Paessler NCM Module.
- **Inventory**: Database schema for `NetworkDevice` and `ConfigurationBackup`.
- **Drivers**: Support for Cisco IOS, Huawei VRP, and Fortinet FortiGate.
- **Backup**: Automated configuration backup using Celery and Valkey.
- **Diff**: Visual diff engine for comparing configuration versions.
- **Syslog**: Real-time change detection via UDP port 514 listener.
- **UI**: Flask-based web interface with PRTG-inspired branding (Blue/Green theme).
- **Docs**: Added README, License, and Changelog.
