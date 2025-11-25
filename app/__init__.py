from flask import Flask
from celery import Celery
from config import Config
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    celery.conf.update(app.config)

    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    @app.context_processor
    def inject_cache_buster():
        import time
        return {'cache_buster': int(time.time())}

    return app
