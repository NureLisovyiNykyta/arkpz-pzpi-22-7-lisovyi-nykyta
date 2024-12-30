from firebase_admin import messaging
from app.models.mobile_device_model import MobileDevice

def send_notification(user_id, title, body, data):
    devices = MobileDevice.query.filter_by(user_id=user_id).all()
    device_tokens = [device.get_device_token() for device in devices if device.get_device_token()]

    if not device_tokens:
        raise ValueError("No device tokens found for the user.")

    for token in device_tokens:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            data=data,
            token=token
        )

        response = messaging.send(message)
        print('Successfully sent message:', response)
