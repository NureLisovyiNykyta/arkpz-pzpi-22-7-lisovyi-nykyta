from app import db
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID
import uuid
from flask import jsonify
from app.models.subscription_model import Subscription
from app.utils import ErrorHandler

class Sensor(db.Model):
    __tablename__ = 'sensor'

    sensor_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    home_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('home.home_id', ondelete='CASCADE'),
        nullable=False
    )
    user_id = db.Column(db.UUID(as_uuid=True), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    is_closed = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=False)
    is_security_breached = db.Column(db.Boolean, default=False)
    is_archived = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    home = db.relationship('Home', back_populates='sensors')

    @classmethod
    def get_all_sensors(cls, home_id):
        try:
            sensors = cls.query.filter_by(home_id=home_id).all()
            sensors_list = [
                {
                    "sensor_id": str(sensor.sensor_id),
                    "name": sensor.name,
                    "type": sensor.type,
                    "is_closed": sensor.is_closed,
                    "is_active": sensor.is_active,
                    "is_security_breached": sensor.is_security_breached,
                    "created_at": sensor.created_at.isoformat(),
                    "is_archived": sensor.is_archived
                }
                for sensor in sensors
            ]

            return jsonify({"sensors": sensors_list}), 200

        except Exception as e:
            return ErrorHandler.handle_error(
                e,
                message="Database error while retrieving sensors",
                status_code=500
            )

    @classmethod
    def add_sensor(cls, user_id, data):
        try:
            home_id = data.get('home_id')
            name = data.get('name')
            type = data.get('type')

            if not home_id or not name or not type:
                raise ValueError("Home id, name and type are required.")

            home = cls.query.filter_by(home_id=home_id, user_id=user_id, is_archived=False).first()
            if not home:
                raise ValueError("Active home not found for the user.")

            current_subscription = Subscription.get_current_subscription(user_id)
            if not current_subscription:
                raise ValueError("User does not have an active subscription.")

            current_sensors_count = cls.query.filter_by(user_id=user_id).count()
            if current_sensors_count >= current_subscription.plan.max_sensors:
                raise ValueError("You have reached the maximum number of sensors allowed by your subscription.")

            new_sensor = cls(
                home_id=home_id,
                user_id=user_id,
                name=name,
                type=type,
            )
            db.session.add(new_sensor)
            db.session.commit()

            return jsonify({"message": "Sensor added successfully."}), 201

        except ValueError as ve:
            return ErrorHandler.handle_validation_error(str(ve))
        except Exception as e:
            db.session.rollback()
            return ErrorHandler.handle_error(
                e,
                message="Database error while adding sensor",
                status_code=500
            )

    @classmethod
    def set_sensor_activity(cls, user_id, data):
        try:
            sensor_id = data.get('sensor_id')
            new_activity = data.get('new_activity')

            if not sensor_id or not new_activity:
                raise ValueError("Sensor id, new activity are required.")

            if not isinstance(new_activity, bool):
                raise ValueError("New activity must be a boolean value.")

            sensor = cls.query.filter_by(user_id=user_id, sensor_id=sensor_id).first()
            if not sensor:
                raise ValueError("Sensor not found for the specified user.")

            sensor.is_active = new_activity
            db.session.commit()

            return jsonify({"message": f"Sensor activity was set as {new_activity}."}), 200

        except ValueError as ve:
            return ErrorHandler.handle_validation_error(str(ve))
        except Exception as e:
            db.session.rollback()
            return ErrorHandler.handle_error(
                e,
                message="Database error while setting sensor activity",
                status_code=500
            )

    @classmethod
    def unarchive_sensor(cls, user_id, sensor_id):
        try:
            sensor = cls.query.filter_by(sensor_id=sensor_id, user_id=user_id, is_archived=True).first()
            if not sensor:
                raise ValueError("Archived sensor not found for the user.")

            current_subscription = Subscription.get_current_subscription(user_id)
            if not current_subscription:
                raise ValueError("User does not have an active subscription.")

            current_sensors_count = cls.query.filter_by(user_id=user_id).count()
            if current_sensors_count >= current_subscription.plan.max_sensors:
                raise ValueError("You have reached the maximum number of sensors allowed by your subscription.")

            sensor.is_archived = False
            db.session.commit()

            return jsonify({"message": "Sensor unarchived successfully."}), 200

        except ValueError as ve:
            return ErrorHandler.handle_validation_error(str(ve))
        except Exception as e:
            db.session.rollback()
            return ErrorHandler.handle_error(
                e,
                message="Database error while unarchiving sensor",
                status_code=500
            )

    @classmethod
    def archive_sensor(cls, user_id, sensor_id):
        try:
            sensor = cls.query.filter_by(sensor_id=sensor_id, user_id=user_id, is_archived=False).first()
            if not sensor:
                raise ValueError("Active sensor not found for the user.")

            sensor.is_archived = True
            sensor.is_closed = False
            sensor.is_active = False
            sensor.is_security_breached = False

            db.session.commit()

            return jsonify({"message": "Sensor archived successfully."}), 200

        except ValueError as ve:
            return ErrorHandler.handle_validation_error(str(ve))
        except Exception as e:
            db.session.rollback()
            return ErrorHandler.handle_error(
                e,
                message="Database error while archiving sensor",
                status_code=500
            )
