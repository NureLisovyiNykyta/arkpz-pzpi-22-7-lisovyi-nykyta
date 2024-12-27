from datetime import datetime, timezone, timedelta
from app.models import Subscription, User, MobileDevice
from app.services.email_subscription_notifications_service import send_subscription_expiration_email
from app.services.mobile_subscription_notifications_service import send_subscription_expiration_notification
from app.utils import ErrorHandler


def notify_subscription_expiration(app):
    try:
        with app.app_context():
            notification_days = [5, 3, 1]
            now = datetime.now()

            subscriptions = Subscription.query.filter(
                Subscription.is_active == True,
                Subscription.end_date > now
            ).all()

            for subscription in subscriptions:
                days_left = (subscription.end_date - now).days

                if days_left in notification_days:
                    user = subscription.user

                    if user.email_confirmed:
                        send_subscription_expiration_email(user, subscription)

                    send_subscription_expiration_notification(user, subscription, days_left)

    except Exception as e:
        with app.app_context():
            return ErrorHandler.handle_error(
                e,
                message="Internal server error while sending subscription ending notifications.",
                status_code=500
            )
