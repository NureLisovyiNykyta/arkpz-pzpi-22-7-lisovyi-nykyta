from app.config import Config
from flask import Flask
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_cors import CORS
import stripe
from flask_apscheduler import APScheduler
import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate('google-services.json')
db = SQLAlchemy()
login_manager = LoginManager()
oauth = OAuth()
mail = Mail()
scheduler = APScheduler()

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    CORS(app,
         origins=app.config['CORS_ALLOW_ORIGINS'],
         methods=app.config['CORS_ALLOW_METHODS'],
         supports_credentials=app.config['CORS_SUPPORTS_CREDENTIALS'],
         allow_headers=app.config['CORS_ALLOW_HEADERS'],
         max_age=app.config['CORS_MAX_AGE'])

    db.init_app(app)
    login_manager.init_app(app)
    oauth.init_app(app)
    mail.init_app(app)
    scheduler.init_app(app)

    stripe.api_key = app.config["STRIPE_SECRET_KEY"]

    with app.app_context():
        db.create_all()

    from app.routes import auth_bp, user_profile_bp, security_bp, mobile_device_bp
    from app.routes import subscription_bp, payments_bp, notification_bp, admin_bp, iot_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_profile_bp)
    app.register_blueprint(security_bp)
    app.register_blueprint(mobile_device_bp)
    app.register_blueprint(subscription_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(iot_bp, url_prefix='/iot')
    app.register_blueprint(payments_bp,  url_prefix='/payments')

    firebase_admin.initialize_app(cred)

    from app.tasks import notify_subscription_expiration, check_subscription_expiration
    scheduler.add_job(
        id='check_subscription_ending',
        func=lambda: check_subscription_expiration(app),
        trigger='interval',
        seconds=20,
        max_instances=1
    )
    scheduler.add_job(
        id='notify_subscription_ending',
        func=lambda: notify_subscription_expiration(app),
        trigger='cron',
        hour=12,
        minute=0,
        max_instances=1
    )

    scheduler.start()

    return app
