from app.utils import ErrorHandler
from firebase_admin import messaging
from app.models import GeneralUserNotification, MobileDevice


def send_subscription_expiration_notification(user, subscription, days_left):
    try:
        devices = MobileDevice.query.filter_by(user_id=user.user_id).all()
        device_tokens = [device.get_device_token() for device in devices if device.get_device_token()]

        if not device_tokens:
            raise ValueError("No device tokens found for the user.")

        formatted_end_date = subscription.end_date.strftime('%A, %d %B %Y')
        title = "Subscription Expiration Notice"
        body=(f"Your {subscription.plan.name} subscription expires on {formatted_end_date}."
              f"Renew within {days_left} days to avoid cancellation.")
        data={
            'title': 'Subscription Expiration Notice',
            'subscription_id': f'{subscription.subscription_id}',
            'subscription_name': f'{subscription.plan.name}',
            'end_date': f'{subscription.end_date}',
            'cancel_in_days': f'{days_left}',
            'user_name': f'{user.name}',
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

        GeneralUserNotification.create_notification(
            user_id=user.user_id,
            title=title,
            body=body,
            importance="medium",
            type="subscription_expiration",
            data={
                "subscription_id": subscription.subscription_id,
                "subscription_plan": subscription.plan.name,
                "end_date": subscription.end_date,
                "days_left": days_left
            },
        )

    except Exception as e:
        return ErrorHandler.handle_error(
            e,
            message="Internal server error while sending subscription expiration notification.",
            status_code=500
        )


def send_subscription_cancelled_notification(user, subscription):
    try:
        devices = MobileDevice.query.filter_by(user_id=user.user_id).all()
        device_tokens = [device.get_device_token() for device in devices if device.get_device_token()]

        if not device_tokens:
            raise ValueError("No device tokens found for the user.")

        formatted_end_date = subscription.end_date.strftime('%A, %d %B %Y')
        title = "Subscription Cancellation Notice"
        body = (f"Your {subscription.plan.name} subscription has been canceled. "
                f"Your subscription was set to expire on {formatted_end_date}. "
                f"Your account is now on a basic plan.")
        data = {
            'title': title,
            'subscription_id': f'{subscription.subscription_id}',
            'subscription_name': f'{subscription.plan.name}',
            'end_date': f'{str(subscription.end_date)}',
            'user_name': f'{user.name}',
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
            print('Successfully sent notification:', response)

        GeneralUserNotification.create_notification(
            user_id=user.user_id,
            title=title,
            body=body,
            importance="medium",
            type="subscription_canceled",
            data={
                "subscription_id": subscription.subscription_id,
                "subscription_plan": subscription.plan.name,
                "end_date": subscription.end_date,
            }
        )

    except Exception as e:
        return ErrorHandler.handle_error(
            e,
            message="Internal server error while sending subscription cancellation notification.",
            status_code=500
        )
