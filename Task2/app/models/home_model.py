from app import db
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID
import uuid
from flask import jsonify
from app.models.default_security_mode_model import DefaultSecurityMode
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
            homes = cls.query.filter_by(user_id=user_id, is_archived=False).all()
            homes_list = [
                {
                    "home_id": str(home.home_id),
                    "name": home.name,
                    "address": home.address,
                    "created_at": home.created_at.isoformat(),
                    "default_mode_id": str(home.default_mode_id),
                    "default_mode_name": home.default_mode.mode_name
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

            default_mode = DefaultSecurityMode.query.filter_by(mode_name="safety").first()

            new_home = cls(
                user_id=user_id,
                name=name,
                address=address,
                default_mode_id=default_mode.default_mode_id
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
    def archive_home(cls, user_id, home_id):
        try:
            home = cls.query.filter_by(user_id=user_id, home_id=home_id, is_archived=False).first()
            if not home:
                raise ValueError("Active home not found for the user.")

            home.is_archived = True

            for sensor in home.sensors:
                sensor.is_archived = True

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
    def change_default_security_mode(cls, user_id, home_id, new_mode_name):
        try:
            home = cls.query.filter_by(user_id=user_id, home_id=home_id, is_archived=False).first()
            if not home:
                raise ValueError("Active home not found for the user.")

            new_mode = DefaultSecurityMode.query.filter_by(mode_name=new_mode_name).first()
            if not new_mode:
                raise ValueError("Invalid security mode.")

            home.default_mode_id = new_mode.mode_id

            # Update sensor activity based on the new mode
            if new_mode_name == "security":
                for sensor in home.sensors:
                    if not sensor.is_archived:
                        sensor.is_active = True
            elif new_mode_name == "safety":
                for sensor in home.sensors:
                    if not sensor.is_archived:
                        sensor.is_active = False

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

