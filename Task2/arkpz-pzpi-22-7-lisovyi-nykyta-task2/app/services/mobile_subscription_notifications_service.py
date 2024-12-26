from app.utils import ErrorHandler
from app.models import GeneralUserNotification
from app.utils import send_notification


def send_subscription_expiration_notification(user, subscription, days_left):
    try:
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

        send_notification(user.user_id, title, body, data)


    except ValueError as ve:
        print(ErrorHandler.handle_validation_error(str(ve)))
    except Exception as e:
        return ErrorHandler.handle_error(
            e,
            message="Internal server error while sending subscription expiration notification.",
            status_code=500
        )


def send_subscription_cancelled_notification(user, subscription):
    try:
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

        send_notification(user.user_id, title, body, data)

    except ValueError as ve:
        print (ErrorHandler.handle_validation_error(str(ve)))
    except Exception as e:
        return ErrorHandler.handle_error(
            e,
            message="Internal server error while sending subscription cancellation notification.",
            status_code=500
        )
