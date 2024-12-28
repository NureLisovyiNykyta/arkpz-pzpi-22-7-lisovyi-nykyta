from app import db
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

    @classmethod
    def create_subscription_plan(cls, data):
        try:
            required_fields = ['name', 'max_homes', 'max_sensors', 'price', 'duration_days']
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"'{field}' is a required field.")

            if not isinstance(data['max_homes'], int) or data['max_homes'] <= 0:
                raise ValueError("'max_homes' must be a positive integer.")

            if not isinstance(data['max_sensors'], int) or data['max_sensors'] <= 0:
                raise ValueError("'max_sensors' must be a positive integer.")

            if not isinstance(data['price'], (float, int)) or data['price'] <= 0:
                raise ValueError("'price' must be a positive number.")

            if not isinstance(data['duration_days'], int) or data['duration_days'] <= 0:
                raise ValueError("'duration_days' must be a positive integer.")

            new_plan = cls(
                name=data['name'],
                max_homes=data['max_homes'],
                max_sensors=data['max_sensors'],
                price=float(data['price']),
                duration_days=data['duration_days']
            )
            db.session.add(new_plan)
            db.session.commit()

            return jsonify({"message": "Subscription plan created successfully."}), 201

        except ValueError as ve:
            return ErrorHandler.handle_validation_error(str(ve))
        except Exception as e:
            db.session.rollback()
            return ErrorHandler.handle_error(
                e,
                message="Database error while creating subscription plan",
                status_code=500
            )
