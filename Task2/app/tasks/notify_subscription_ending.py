from app import db
from datetime import datetime, timezone, timedelta
from app.models import Subscription, User
from app.utils import ErrorHandler


def notify_subscription_ending(app):
    try:
        with app.app_context():
            notification_days = [5, 3, 1]
            now = datetime.now(timezone.utc)

            subscriptions = Subscription.query.filter(
                Subscription.is_active == True,
                Subscription.end_date > now
            ).all()

            for subscription in subscriptions:
                days_left = (subscription.end_date - now).days

                if days_left in notification_days:
                    user = User.query.filter_by(user_id=subscription.user_id).first()

                    if user:
                        message = f"Your subscription is ending in {days_left} day(s). Please renew to continue enjoying the service."

            db.session.commit()

    except Exception as e:
        return ErrorHandler.handle_error(
            e,
            message="Internal server error while sending subscription ending notifications.",
            status_code=500
        )
