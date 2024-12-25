from app import db
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID
import uuid
from flask import jsonify
from app.utils import ErrorHandler


class SubscriptionPlan(db.Model):
    __tablename__ = 'subscription_plan'

    plan_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False)
    max_homes = db.Column(db.Integer, nullable=False)
    max_sensors = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)

    subscriptions = db.relationship('Subscription', back_populates='plan')

    @classmethod
    def get_all_subscription_plans(cls):
        try:
            subscription_plans = cls.query.filter_by().all()
            subscription_plans_list = [
                {
                    "plan_id": str(plan.plan_id),
                    "name": plan.name,
                    "max_homes": plan.max_homes,
                    "max_sensors": plan.max_sensors,
                    "price": plan.price,
                    "description": plan.duration_days,
                } for plan in subscription_plans
            ]
            return jsonify({"subscription_plans": subscription_plans_list}), 200
        except Exception as e:
            return ErrorHandler.handle_error(
                e,
                message="Database error while retrieving subscription plans",
                status_code=500
            )


