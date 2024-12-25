from app.utils import ErrorHandler
from firebase_admin import messaging
from app.models import GeneralUserNotification


def send_subscription_expiration_notification(device_token, user, subscription, days_left):
    try:
        formatted_end_date = subscription.end_date.strftime('%A, %d %B %Y')
        title = "Subscription Expiration Notice"
        body=(f"Your {subscription.plan.name} subscription expires on {formatted_end_date}."
              f"Renew within {days_left} days to avoid cancellation.")

        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            data={
                'title': 'Subscription Expiration Notice',
                'subscription_id': f'{subscription.subscription_id}',
                'subscription_name': f'{subscription.plan.name}',
                'end_date': f'{subscription.end_date}',
                'cancel_in_days': f'{days_left}',
                'user_name': f'{user.name}',
            },
            token=device_token
        )

        response = messaging.send(message)
        print('Successfully sent message:', response)

        data = {
            "subscription_id": subscription.subscription_id,
            "subscription_plan": subscription.plan.name,
            "end_date": subscription.end_date,
            "days_left": days_left
        }
        GeneralUserNotification.create_notification(
            user_id=user.user_id,
            title=title,
            body=body,
            importance="medium",
            type="subscription_expiration",
            data=data,
        )

    except Exception as e:
        return ErrorHandler.handle_error(
            e,
            message="Internal server error while sending subscription expiration notification.",
            status_code=500
        )


def send_subscription_cancelled_notification(device_token, user, subscription):
    try:
        formatted_end_date = subscription.end_date.strftime('%A, %d %B %Y')
        title = "Subscription Cancellation Notice"
        body = (f"Your {subscription.plan.name} subscription has been canceled. "
                f"Your subscription was set to expire on {formatted_end_date}. "
                f"Your account is now on a basic plan.")

        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            data={
                'title': title,
                'subscription_id': f'{subscription.subscription_id}',
                'subscription_name': subscription.plan.name,
                'end_date': str(subscription.end_date),
                'user_name': user.name,
                'status': 'canceled',
            },
            token=device_token
        )

        response = messaging.send(message)
        print('Successfully sent notification:', response)

        data = {
            "subscription_id": subscription.subscription_id,
            "subscription_plan": subscription.plan.name,
            "end_date": subscription.end_date,
            "status": 'canceled',
        }
        GeneralUserNotification.create_notification(
            user_id=user.user_id,
            title=title,
            body=body,
            importance="medium",
            type="subscription_canceled",
            data=data
        )

    except Exception as e:
        return ErrorHandler.handle_error(
            e,
            message="Internal server error while sending subscription cancellation notification.",
            status_code=500
        )
