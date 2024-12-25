from app import db
from datetime import datetime, timezone, timedelta
from app.models import SubscriptionPlan, Subscription
from app.utils import ErrorHandler

def check_subscription_ending(app):
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

            for subscription in subscriptions_ending:

                if subscription.plan_id == basic_plan.plan_id:
                    subscription.end_date = datetime.now(timezone.utc) + timedelta(days=subscription.plan.duration_days)

                else:
                    subscription.is_active = False
                    subscription.end_date = datetime.now(timezone.utc)

                    new_subscription = Subscription(
                        user_id=subscription.user_id,
                        plan_id=basic_plan.plan_id,
                        start_date=datetime.now(timezone.utc),
                        end_date=datetime.now(timezone.utc) + timedelta(days=basic_plan.duration_days),
                        is_active=True
                    )
                    db.session.add(new_subscription)

            db.session.commit()

    except Exception as e:
        with app.app_context():
            db.session.rollback()
        return ErrorHandler.handle_error(
            e,
            message="Internal server error while checking subscription ending.",
            status_code=500
        )
