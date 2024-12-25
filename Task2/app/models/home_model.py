from app import db
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID
import uuid
from flask import jsonify
from app.models.default_security_mode_model import DefaultSecurityMode
from app.models.subscription_model import Subscription
from app.utils import ErrorHandler


class Home(db.Model):
    __tablename__ = 'home'

    home_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)
    default_mode_id = db.Column(UUID(as_uuid=True), db.ForeignKey('default_security_mode.mode_id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    is_archived = db.Column(db.Boolean, default=False)

    user = db.relationship('User', back_populates='homes')
    default_mode = db.relationship('DefaultSecurityMode', back_populates='homes')

    sensors = db.relationship(
        'Sensor',
        back_populates='home',
        cascade="all, delete-orphan"
    )

    @classmethod
    def get_all_homes(cls, user_id):
        try:
            homes = cls.query.filter_by(user_id=user_id).all()
            homes_list = [
                {
                    "home_id": str(home.home_id),
                    "name": home.name,
                    "address": home.address,
                    "created_at": home.created_at.isoformat(),
                    "default_mode_id": str(home.default_mode_id),
                    "default_mode_name": home.default_mode.mode_name,
                     "is_archived": home.is_archived
                } for home in homes
            ]
            return jsonify({"homes": homes_list}), 200

        except Exception as e:
            return ErrorHandler.handle_error(
                e,
                message="Database error while retrieving homes",
                status_code=500
            )

    @classmethod
    def add_home(cls, user_id, data):
        try:
            name = data.get('name')
            address = data.get('address')

            if not name and not address:
                raise ValueError("Name and address are required.")

            current_subscription = Subscription.get_current_subscription(user_id)
            if not current_subscription:
                raise ValueError("User does not have an active subscription.")

            current_homes_count = cls.query.filter_by(user_id=user_id).count()
            if current_homes_count >= current_subscription.plan.max_homes:
                raise ValueError("You have reached the maximum number of homes allowed by your subscription.")

            default_mode = DefaultSecurityMode.query.filter_by(mode_name="safety").first()

            new_home = cls(
                user_id=user_id,
                name=name,
                address=address,
                default_mode_id=default_mode.mode_id
            )
            db.session.add(new_home)
            db.session.commit()

            return jsonify({"message": "Home added successfully."}), 201

        except ValueError as ve:
            return ErrorHandler.handle_validation_error(str(ve))
        except Exception as e:
            db.session.rollback()
            return ErrorHandler.handle_error(
                e,
                message="Database error while adding home",
                status_code=500
            )

    @classmethod
    def delete_home(cls, user_id, home_id):
        try:
            home = cls.query.filter_by(user_id = user_id, home_id = home_id).first()
            if not home:
                raise ValueError("Home not found for the user.")

            db.session.delete(home)
            db.session.commit()

            return jsonify({"message": "Home was deleted successfully."}), 200

        except ValueError as ve:
            return ErrorHandler.handle_validation_error(str(ve))
        except Exception as e:
            db.session.rollback()
            return ErrorHandler.handle_error(
                e,
                message="Database error while deleting home",
                status_code=500
            )

    @classmethod
    def unarchive_home(cls, user_id, home_id):
        try:
            home = cls.query.filter_by(home_id=home_id, user_id=user_id, is_archived=True).first()
            if not home:
                raise ValueError("Archived home not found for the user.")

            current_subscription = Subscription.get_current_subscription(user_id)
            if not current_subscription:
                raise ValueError("User does not have an active subscription.")

            current_homes_count = cls.query.filter_by(user_id=user_id).count()
            if current_homes_count >= current_subscription.plan.max_homes:
                raise ValueError("You have reached the maximum number of homes allowed by your subscription.")

            home.is_archived = False

            db.session.commit()

            return jsonify({"message": "Home unarchived successfully."}), 200

        except ValueError as ve:
            return ErrorHandler.handle_validation_error(str(ve))
        except Exception as e:
            db.session.rollback()
            return ErrorHandler.handle_error(
                e,
                message="Database error while unarchiving home",
                status_code=500
            )

    @classmethod
    def archive_home_sensors(cls, user_id, home_id):
        try:
            home = cls.query.filter_by(user_id=user_id, home_id=home_id, is_archived=False).first()
            if not home:
                raise ValueError("Active home not found for the user.")

            default_mode = DefaultSecurityMode.query.filter_by(mode_name="safety").first()

            home.default_mode_id = default_mode.mode_id
            home.is_archived = True

            for sensor in home.sensors:
                sensor.is_archived = True
                sensor.is_closed = False
                sensor.is_active = False
                sensor.is_security_breached = False

            db.session.commit()
            return jsonify({"message": "Home and its sensors archived successfully."}), 200

        except ValueError as ve:
            return ErrorHandler.handle_validation_error(str(ve))
        except Exception as e:
            db.session.rollback()
            return ErrorHandler.handle_error(
                e,
                message="Database error while archiving home and sensors",
                status_code=500
            )

    @classmethod
    def set_default_security_mode(cls, user_id, data):
        try:
            home_id = data.get('home_id')
            new_mode_name = data.get('new_mode_name')

            if not home_id or not new_mode_name:
                raise ValueError("Home ID and new mode name are required.")

            home = cls.query.filter_by(user_id=user_id, home_id=home_id, is_archived=False).first()
            if not home:
                raise ValueError("Active home not found for the user.")

            new_mode = DefaultSecurityMode.query.filter_by(mode_name=new_mode_name).first()
            if not new_mode:
                raise ValueError("Invalid security mode.")

            if new_mode_name == "security":
                if any(not sensor.is_closed and not sensor.is_archived for sensor in home.sensors):
                    cls._set_sensors_to_safety(home)
                    safety_mode = DefaultSecurityMode.query.filter_by(mode_name="safety").first()
                    home.default_mode_id = safety_mode.mode_id
                    db.session.commit()
                    return jsonify({"message": "Security mode cannot be set! Safety mode was set."}), 200

                cls._activate_sensors(home)

            elif new_mode_name == "safety":
                cls._set_sensors_to_safety(home)

            home.default_mode_id = new_mode.mode_id
            db.session.commit()

            return jsonify({"message": f"Default security mode changed to '{new_mode_name}' and sensors updated."}), 200

        except ValueError as ve:
            return ErrorHandler.handle_validation_error(str(ve))
        except Exception as e:
            db.session.rollback()
            return ErrorHandler.handle_error(
                e,
                message="Database error while changing default security mode",
                status_code=500
            )

    @staticmethod
    def _activate_sensors(home):
        for sensor in home.sensors:
            if not sensor.is_archived:
                sensor.is_active = True

    @staticmethod
    def _set_sensors_to_safety(home):
        for sensor in home.sensors:
            if not sensor.is_archived:
                sensor.is_active = False
                sensor.is_closed = False
                sensor.is_security_breached = False
