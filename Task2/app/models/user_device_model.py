from app import db
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID
import uuid
from flask import jsonify
from cryptography.fernet import Fernet
from app.utils import ErrorHandler
import os


cipher = Fernet(os.getenv('SECRET_KEY_Fernet'))


class UserDevice(db.Model):
    __tablename__ = 'user_device'

    user_device_id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('user.user_id', ondelete='CASCADE'),
        nullable=False
    )
    device_token = db.Column(db.Text, nullable=False)
    device_info = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    user = db.relationship('User', back_populates='devices')

    def set_device_token(self, device_token):
        self.device_token = cipher.encrypt(device_token.encode()).decode()

    def get_device_token(self):
        if self.device_token:
            return cipher.decrypt(self.device_token.encode()).decode()
        else:
            return None

    @classmethod
    def get_user_devices(cls, user_id):
        try:
            # Retrieve all devices for a user
            user_devices = cls.query.filter_by(user_id=user_id).all()
            devices = []
            for device in user_devices:
                devices.append({
                    "user_device_id": str(device.user_device_id),
                    "device_info": device.device_info,
                    "created_at": device.created_at.isoformat()
                })

            return jsonify({'devices': devices}), 200

        except Exception as e:
            return ErrorHandler.handle_error(
                e,
                message="Database error while retrieving devices",
                status_code=500
            )

    @classmethod
    def add_user_device(cls, user_id, data):
        try:
            device_token = data.get('device_token')
            device_info = data.get('device_info')

            if not device_token:
                raise ValueError("Device token is required.")

            # Check if the device already exists for this user
            existing_device = cls.query.filter_by(user_id=user_id, device_info=device_info).first()
            if existing_device:
                raise ValueError("This device is already registered for the user.")

            # Create a new user device
            new_device = cls(user_id=user_id, device_info=device_info)
            new_device.set_device_token(device_token)

            db.session.add(new_device)
            db.session.commit()

            return jsonify({'message': "Device was successfully added to the user.", 'device_id': str(new_device.user_device_id)}), 201

        except ValueError as ve:
            return ErrorHandler.handle_validation_error(str(ve))
        except Exception as e:
            db.session.rollback()
            return ErrorHandler.handle_error(
                e,
                message="Database error while adding device to user",
                status_code=500
            )

    @classmethod
    def delete_device_by_id(cls, user_id, user_device_id):
        try:
            # Find the device by its ID
            user_device = cls.query.filter_by(user_id=user_id, user_device_id=user_device_id).first()
            if not user_device:
                raise ValueError("Device not found for the specified ID.")

            db.session.delete(user_device)
            db.session.commit()

            return jsonify({'message': "Device was successfully removed by ID."}), 200

        except ValueError as ve:
            return ErrorHandler.handle_validation_error(str(ve))
        except Exception as e:
            db.session.rollback()
            return ErrorHandler.handle_error(
                e,
                message="Database error while deleting device by ID",
                status_code=500
            )

    @classmethod
    def delete_device_by_token_and_user(cls, user_id, device_token):
        try:
            encrypted_token = cipher.encrypt(device_token.encode()).decode()

            # Find the device by user_id and token
            user_device = cls.query.filter_by(user_id=user_id, device_token=encrypted_token).first()
            if not user_device:
                raise ValueError("Device not found for the specified user and token.")

            db.session.delete(user_device)
            db.session.commit()

            return jsonify({'message': "Device was successfully removed for the user."}), 200

        except ValueError as ve:
            return ErrorHandler.handle_validation_error(str(ve))
        except Exception as e:
            db.session.rollback()
            return ErrorHandler.handle_error(
                e,
                message="Database error while deleting device by token and user",
                status_code=500
            )

    @classmethod
    def delete_device_by_token(cls, device_token):
        try:
            encrypted_token = cipher.encrypt(device_token.encode()).decode()

            # Find the device by token only
            user_device = cls.query.filter_by(device_token=encrypted_token).first()
            if not user_device:
                raise ValueError("Device not found for the specified token.")

            db.session.delete(user_device)
            db.session.commit()

            return jsonify({'message': "Device was successfully removed by token."}), 200

        except ValueError as ve:
            return ErrorHandler.handle_validation_error(str(ve))
        except Exception as e:
            db.session.rollback()
            return ErrorHandler.handle_error(
                e,
                message="Database error while deleting device by token",
                status_code=500
            )
