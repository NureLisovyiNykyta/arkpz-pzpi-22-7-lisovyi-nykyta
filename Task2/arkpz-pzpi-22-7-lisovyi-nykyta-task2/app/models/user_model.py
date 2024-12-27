from app import db
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID
import uuid
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
from app.models.role_model import Role
from app.utils import ErrorHandler
import os

cipher = Fernet(os.getenv('SECRET_KEY_Fernet'))


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    user_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_id = db.Column(UUID(as_uuid=True), db.ForeignKey('role.role_id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    birthday = db.Column(db.Date)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256))
    google_id = db.Column(db.String(128))
    google_refresh_token = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    email_confirmed = db.Column(db.Boolean, default=False)

    role = db.relationship('Role', back_populates='users')

    subscriptions = db.relationship('Subscription', back_populates='user')

    general_notifications = db.relationship(
        'GeneralUserNotification',
        back_populates='user',
        cascade="all, delete-orphan"
    )

    devices = db.relationship(
        'MobileDevice',
        back_populates='user',
        cascade="all, delete-orphan"
    )

    homes = db.relationship(
        'Home',
        back_populates='user',
        cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        if self.password is None:
            return False
        return check_password_hash(self.password, password)

    def get_id(self):
        return self.user_id

    def set_refresh_token(self, refresh_token):
        self.google_refresh_token = cipher.encrypt(refresh_token.encode()).decode()

    def get_refresh_token(self):
        if self.google_refresh_token:
            return cipher.decrypt(self.google_refresh_token.encode()).decode()
        else:
            return None

    @staticmethod
    def get_user_by_email(email):
        user = User.query.filter_by(email=email).first()
        return user

    @classmethod
    def register_user(cls, data):
        try:
            name = data.get('name')
            email = data.get('email')
            password = data.get('password')

            if not name or not email:
                raise ValueError("Name and email are required for registration.")

            role = Role.query.filter_by(role_name="user").first()

            user = cls(name=name, email=email, role_id = role.role_id)

            if password:
                user.set_password(password)

            db.session.add(user)
            db.session.commit()
            return user

        except ValueError as ve:
            return ErrorHandler.handle_validation_error(str(ve))
        except Exception as e:
            db.session.rollback()
            raise RuntimeError("Database error while user register") from e

    def add_user_data(self, data):
        name = data.get('name')
        birthday = data.get('birthday')
        password = data.get('password')

        if name:
            self.name = name
        if birthday:
            self.birthday = birthday
        if password:
            self.set_password(password)

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError("Database error while user updating") from e

    @classmethod
    def google_register_user(cls, data):
        try:
            name = data.get('name')
            email = data.get('email')
            birthday = data.get('birthday')
            google_id = data.get('google_id')
            refresh_token = data.get('refresh_token')

            if not name or not email:
                raise ValueError("Name and email are required for Google registration.")

            user = cls(
                name=name,
                email=email,
                birthday=birthday,
                google_id=google_id
            )
            db.session.add(user)
            db.session.commit()

            if refresh_token:
                user.set_refresh_token(refresh_token)
                db.session.commit()
            return user

        except ValueError as ve:
            return ErrorHandler.handle_validation_error(str(ve))
        except Exception as e:
            db.session.rollback()
            raise RuntimeError("Database error while user google register") from e

    def add_google_data(self, google_id, refresh_token):
        try:
            self.google_id = google_id
            db.session.commit()

            if refresh_token:
                self.set_refresh_token(refresh_token)
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise Exception("Database error while adding google data") from e

    def verify_email(self):
        self.email_confirmed = True
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError("Database error while verifying email") from e

    def drop_email_verification(self):
        self.email_confirmed = False
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError("Database error while dropping email verification") from e

    def update_profile(self, data):
        name = data.get('name')
        birthday = data.get('birthday')

        if name:
            self.name = name
        if birthday:
            self.birthday = birthday

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError("Database error while dropping email verification") from e

    def update_password(self, data):
        old_password = data.get('old_password')
        new_password = data.get('new_password')

        if self.check_password(old_password):
            if new_password:
                self.set_password(new_password)
            else:
                raise ValueError("New password is required.")
        else:
            raise ValueError("Invalid old password.")

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise RuntimeError("Database error while updating password") from e

    def get_profile_data(self):
        return {
            "name": self.name,
            "email": self.email,
            "birthday": self.birthday,
            "email_confirmed": self.email_confirmed,
            "created_at": self.created_at,
        }
