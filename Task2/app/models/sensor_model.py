from app import db
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID
import uuid
from flask import jsonify
from app.models.home_model import Home
from app.utils import ErrorHandler

class Sensor(db.Model):
    __tablename__ = 'sensor'

    sensor_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    home_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('home.home_id', ondelete='CASCADE'),
        nullable=False
    )
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
            sensors = cls.query.filter_by(home_id=home_id, is_archived=False).all()
            sensors_list = [
                {
                    "sensor_id": str(sensor.sensor_id),
                    "name": sensor.name,
                    "type": sensor.type,
                    "is_closed": sensor.is_closed,
                    "is_active": sensor.is_active,
                    "is_security_breached": sensor.is_security_breached,
                    "created_at": sensor.created_at.isoformat()
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
    def add_sensor(cls, user_id, home_id, data):
        try:
            name = data.get('name')
            type = data.get('type')

            if not name or not type:
                raise ValueError("Name and type are required.")

            home = cls.query.filter_by(home_id=home_id, user_id=user_id, is_archived=False).first()
            if not home:
                raise ValueError("Active home not found for the user.")

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
    def delete_sensor(cls, user_id, sensor_id):
        try:
            sensor = cls.query.filter_by(user_id=user_id, sensor_id=sensor_id).first()
            if not sensor:
                raise ValueError("Sensor not found for the specified user.")

            db.session.delete(sensor)
            db.session.commit()

            return jsonify({"message": "Sensor was deleted successfully."}), 200

        except ValueError as ve:
            return ErrorHandler.handle_validation_error(str(ve))
        except Exception as e:
            db.session.rollback()
            return ErrorHandler.handle_error(
                e,
                message="Database error while deleting sensor",
                status_code=500
            )
