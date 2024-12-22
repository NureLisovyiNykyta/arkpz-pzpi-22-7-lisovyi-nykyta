from flask_mail import Message
from app import mail, db
from datetime import date
from app.models import UserScheduledWeatherNotification, UserDevice
from flask import jsonify
from app.utils import ErrorHandler
import requests
import os

def send_scheduled_notifications(app):
    try:
        with app.app_context():
            today = date.today()

            notifications = UserScheduledWeatherNotification.query.filter_by(sending_date=today).all()

            for notification in notifications:
                user = notification.user

                if user.email_confirmed:
                    send_email_notification(user.email, notification.city_id, notification.notification_date)

                devices = UserDevice.query.filter_by(user_id=user.user_id).all()
                for device in devices:
                    device_token = device.get_device_token()
                    if device_token:
                        send_push_notification(device_token, notification.city_id, notification.notification_date)

                db.session.delete(notification)

            db.session.commit()

    except Exception as e:
        db.session.rollback()
        return ErrorHandler.handle_error(
            e,
            message="Internal server error while sending scheduled notifications.",
            status_code=500
        )

def send_email_notification(email, city_id, notification_date):
    subject = f"Напоминание о погоде на {notification_date}"
    body = f"Привет! Напоминаем, что завтра ({notification_date}) у вас запланирован прогноз погоды для города с ID {city_id}."

    msg = Message(subject=subject, recipients=[email], body=body)
    mail.send(msg)

def send_push_notification(device_token, city_id, notification_date):
    fcm_url = "https://fcm.googleapis.com/fcm/send"
    fcm_server_key = os.getenv('FCM_SERVER_KEY')

    headers = {
        "Authorization": f"key={fcm_server_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "to": device_token,
        "notification": {
            "title": f"Напоминание о погоде на {notification_date}",
            "body": f"Прогноз погоды для города с ID {city_id} доступен.",
            "sound": "default"
        },
        "data": {
            "city_id": city_id,
            "notification_date": str(notification_date)
        }
    }

    try:
        response = requests.post(fcm_url, json=payload, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        ErrorHandler.handle_error(
            e,
            message="Failed to send push notification.",
            status_code=500
        )
