from app import create_app, db
from app.models import NetworkDevice, ConfigurationBackup

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'NetworkDevice': NetworkDevice, 'ConfigurationBackup': ConfigurationBackup}

if __name__ == '__main__':
    app.run(debug=True)
