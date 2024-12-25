from app import db
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.utils import ErrorHandler
from flask import jsonify


class SecurityUserNotification(db.Model):
    __tablename__ = 'security_user_notifications'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    home_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('home.home_id', ondelete='CASCADE'), nullable=False)
    sensor_id = db.Column(db.UUID(as_uuid=True), nullable=True)  # Просто поле, без внешнего ключа
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    importance = db.Column(db.Enum('low', 'medium', 'high', name='importance_enum'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    type = db.Column(db.String(50), nullable=False)
    data = db.Column(db.JSON, nullable=True)

    home = db.relationship('Home', backref=db.backref('security_notifications', lazy=True))

    @classmethod
    def create_notification(cls, home_id, title, body, importance, type, sensor_id=None, data=None):
        new_notification = cls(
            home_id=home_id,
            title=title,
            body=body,
            importance=importance,
            type=type,
            sensor_id=sensor_id,
            data=data
        )
        db.session.add(new_notification)
        db.session.commit()
        return new_notification

    @classmethod
    def get_notifications_by_home(cls, home_id):
        try:
            notifications = cls.query.filter_by(home_id=home_id).order_by(cls.created_at.desc()).all()

            notifications_list = [
                {
                    "id": str(notification.id),
                    "home_id": str(notification.home_id),
                    "sensor_id": str(notification.sensor_id) if notification.sensor_id else None,
                    "title": notification.title,
                    "body": notification.body,
                    "importance": notification.importance,
                    "created_at": notification.created_at.isoformat(),
                    "type": notification.type,
                    "data": notification.data
                } for notification in notifications
            ]

            return jsonify({"notifications": notifications_list}), 200

        except Exception as e:
            return ErrorHandler.handle_error(
                e,
                message="Database error while retrieving notifications",
                status_code=500
            )
