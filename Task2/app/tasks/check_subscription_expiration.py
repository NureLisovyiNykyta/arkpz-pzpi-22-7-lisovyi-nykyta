from app import db
from datetime import datetime, timezone, timedelta
from app.models import SubscriptionPlan, Subscription, MobileDevice, Home, DefaultSecurityMode
from app.services.email_subscription_notifications_service import send_subscription_canceled_email
from app.services.mobile_subscription_notifications_service import send_subscription_cancelled_notification
from app.utils import ErrorHandler

def check_subscription_expiration(app):
    try:
        with app.app_context():
            subscriptions_ending = Subscription.query.filter(
                Subscription.is_active == True,
                Subscription.end_date <= datetime.now(timezone.utc)
            ).all()

            basic_plan = SubscriptionPlan.query.filter_by(plan_name="basic").first()
            if not basic_plan:
                return ErrorHandler.handle_error(
                    None,
                    message="Basic plan not found.",
                    status_code=404
                )
            default_mode = DefaultSecurityMode.query.filter_by(mode_name="safety").first()
            if not default_mode:
                return ErrorHandler.handle_error(
                    None,
                    message="Default mode not found.",
                    status_code=404
                )

            for subscription in subscriptions_ending:

                if subscription.plan_id == basic_plan.plan_id:
                    subscription.end_date = datetime.now(timezone.utc) + timedelta(days=subscription.plan.duration_days)

                else:
                    # Cancel expired subscription
                    subscription.is_active = False
                    subscription.end_date = datetime.now(timezone.utc)

                    # Create basic plan subscription
                    new_subscription = Subscription(
                        user_id=subscription.user_id,
                        plan_id=basic_plan.plan_id,
                        start_date=datetime.now(timezone.utc),
                        end_date=datetime.now(timezone.utc) + timedelta(days=basic_plan.duration_days),
                        is_active=True
                    )
                    db.session.add(new_subscription)

                    #Home and sensors archiving
                    user_homes = Home.query.filter(
                        Home.user_id == subscription.user_id,
                    ).all()

                    for home in user_homes:
                        if not home.is_archived:
                            home.is_archived = True
                            home.default_mode_id = default_mode.mode_id
                            for sensor in home.sensors:
                                if not sensor.is_archived:
                                    sensor.is_archived = True
                                    sensor.is_closed = False
                                    sensor.is_active = False
                                    sensor.is_security_breached = False

                    # Send subscription canceled email and notification
                    user = subscription.user

                    if user.email_confirmed:
                        send_subscription_canceled_email(user, subscription)

                    devices = MobileDevice.query.filter_by(user_id=user.user_id).all()
                    for device in devices:
                        device_token = device.get_device_token()
                        if device_token:
                            send_subscription_cancelled_notification(device_token, user, subscription)

            db.session.commit()

    except Exception as e:
        with app.app_context():
            db.session.rollback()
        return ErrorHandler.handle_error(
            e,
            message="Internal server error while checking subscription ending.",
            status_code=500
        )
