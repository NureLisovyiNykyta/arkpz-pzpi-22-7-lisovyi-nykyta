from app import db
from datetime import datetime, timezone, timedelta
from sqlalchemy.dialects.postgresql import UUID
import uuid
from flask import jsonify
from app.models.subscription_plan_model import SubscriptionPlan
from app.utils import ErrorHandler


class Subscription(db.Model):
    __tablename__ = 'subscription'

    subscription_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)
    plan_id = db.Column(UUID(as_uuid=True), db.ForeignKey('subscription_plan.plan_id', ondelete='CASCADE'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    end_date = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    user = db.relationship('User', back_populates='subscriptions')
    plan = db.relationship('SubscriptionPlan', back_populates='subscriptions')

    @classmethod
    def create_basic_subscription(cls, user_id):
        try:
            existing_subscription = cls.query.filter_by(user_id=user_id, is_active=True).first()
            if existing_subscription:
                raise ValueError("User already has an active subscription.")

            plan = SubscriptionPlan.query.filter_by(name='basic').first()
            if not plan:
                raise ValueError("Subscription plan not found.")

            new_subscription = cls(
                user_id=user_id,
                plan_id=plan.plan_id,
                end_date=datetime.now(timezone.utc) + timedelta(days=plan.duration_days),
                is_active=True,
            )

            db.session.add(new_subscription)
            db.session.commit()

            return jsonify({"message": "Basic subscription created successfully."}), 200

        except ValueError as ve:
            return ErrorHandler.handle_validation_error(str(ve))
        except Exception as e:
            db.session.rollback()
            return ErrorHandler.handle_error(
                e,
                message="Database error while creating basic subscription",
                status_code=500
            )

    @classmethod
    def purchase_paid_subscription(cls, user_id, plan_id):
        try:
            plan = SubscriptionPlan.query.filter_by(plan_id=plan_id).first()
            if not plan:
                raise ValueError("Subscription plan not found.")

            if plan.name == 'basic':
                raise ValueError("Cannot purchase a basic plan as a paid subscription.")

            existing_subscription = cls.query.filter_by(user_id=user_id, is_active=True).first()
            if existing_subscription:
                raise ValueError("User already has an active subscription.")

            new_subscription = cls(
                user_id=user_id,
                plan_id=plan_id,
                end_date = datetime.now(timezone.utc) + timedelta(days=plan.duration_days),
                is_active=True
            )

            db.session.add(new_subscription)
            db.session.commit()

            return jsonify({"message": "Paid subscription purchased successfully."}), 200

        except ValueError as ve:
            return ErrorHandler.handle_validation_error(str(ve))
        except Exception as e:
            db.session.rollback()
            return ErrorHandler.handle_error(
                e,
                message="Database error while purchasing paid subscription",
                status_code=500
            )

    @classmethod
    def extend_subscription(cls, user_id):
        try:
            active_subscription = cls.query.filter_by(user_id=user_id, is_active=True).first()
            if not active_subscription:
                raise ValueError("User does not have an active subscription.")

            if active_subscription.end_date < datetime.now(timezone.utc):
                active_subscription.end_date += timedelta(days=30)
            else:
                raise ValueError("Current subscription has no end date.")

            db.session.commit()

            return jsonify({"message": "Subscription extended successfully."}), 200

        except ValueError as ve:
            return ErrorHandler.handle_validation_error(str(ve))
        except Exception as e:
            db.session.rollback()
            return ErrorHandler.handle_error(
                e,
                message="Database error while extending subscription",
                status_code=500
            )


