from app.utils import ErrorHandler
from firebase_admin import messaging
from app.models.security_user_notification import SecurityUserNotification
from app.models import MobileDevice

def send_security_mode_change_notification(user_id, home, new_mode):
    try:
        devices = MobileDevice.query.filter_by(user_id=user_id).all()
        device_tokens = [device.get_device_token() for device in devices if device.get_device_token()]

        if not device_tokens:
            raise ValueError("No device tokens found for the user.")

        title = "Security Mode Change Notice"
        body = f"Your home '{home.name}' security mode has been changed to {new_mode.name}."
        data = {
            'title': title,
            'new_mode_name': f'{new_mode.name}',
            'home_id': f'{home.id}',
            'home_name': f'{home.name}',
        }

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


        SecurityUserNotification.create_notification(
            home_id=home.home_id,
            title=title,
            body=body,
            importance="medium",
            type="security_mode_change",
            data={
                "new_mode_name": new_mode.name
            },
        )

    except Exception as e:
        return ErrorHandler.handle_error(
            e,
            message="Internal server error while sending security mode change notification.",
            status_code=500
        )


def send_sensor_activity_change_notification(user_id, sensor, new_activity):
    try:
        devices = MobileDevice.query.filter_by(user_id=user_id).all()
        device_tokens = [device.get_device_token() for device in devices if device.get_device_token()]

        if not device_tokens:
            raise ValueError("No device tokens found for the user.")

        title = "Sensor Activity Change Notice"
        body = f"The activity of your sensor '{sensor.name}'in home '{sensor.home.name}' has been changed to {new_activity}."
        data = {
            'title': title,
            'sensor_id': f'{sensor.id}',
            'sensor_name': f'{sensor.name}',
            'home_id': f'{sensor.home_id}',
            'home_name': f'{sensor.home.name}',
            'new_activity': f'{new_activity}'
        }

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

        SecurityUserNotification.create_notification(
            home_id=sensor.home_id,
            title=title,
            body=body,
            importance="medium",
            type="sensor_activity_change",
            sensor_id=sensor.sensor_id,
            data={
                "new_activity": new_activity
            },
        )

    except Exception as e:
        return ErrorHandler.handle_error(
            e,
            message="Internal server error while sending sensor activity change notification.",
            status_code=500
        )
