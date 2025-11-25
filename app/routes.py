from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import NetworkDevice, ConfigurationBackup
from app.tasks import backup_device_config
from ncm.diff_engine import compare_configs

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    devices = NetworkDevice.query.all()
    return render_template('index.html', devices=devices)

@bp.route('/add_device', methods=['GET', 'POST'])
def add_device():
    if request.method == 'POST':
        hostname = request.form['hostname']
        ip_address = request.form['ip_address']
        vendor = request.form['vendor']
        protocol = request.form['protocol']
        username = request.form['username']
        password = request.form['password'] # Encrypt this in real app
        secret = request.form.get('secret', '') # Encrypt this in real app
        
        device = NetworkDevice(
            hostname=hostname,
            ip_address=ip_address,
            vendor=vendor,
            protocol=protocol,
            username=username,
            password_encrypted=password,
            enable_secret_encrypted=secret
        )
        db.session.add(device)
        db.session.commit()
        flash('Device added successfully!')
        return redirect(url_for('main.index'))
    return render_template('add_device.html')

@bp.route('/device/<int:device_id>')
def device_detail(device_id):
    device = NetworkDevice.query.get_or_404(device_id)
    backups = device.backups.order_by(ConfigurationBackup.timestamp.desc()).all()
    return render_template('device_detail.html', device=device, backups=backups)

@bp.route('/backup/<int:device_id>', methods=['POST'])
def trigger_backup(device_id):
    backup_device_config.delay(device_id)
    flash('Backup task started!')
    return redirect(url_for('main.device_detail', device_id=device_id))

@bp.route('/diff/<int:backup_id>')
def view_diff(backup_id):
    backup = ConfigurationBackup.query.get_or_404(backup_id)
    # Find previous backup
    prev_backup = ConfigurationBackup.query.filter(
        ConfigurationBackup.device_id == backup.device_id,
        ConfigurationBackup.timestamp < backup.timestamp
    ).order_by(ConfigurationBackup.timestamp.desc()).first()
    
    prev_content = prev_backup.content if prev_backup else ""
    diff_html = compare_configs(prev_content, backup.content)
    
    return render_template('diff_view.html', backup=backup, diff_html=diff_html)
