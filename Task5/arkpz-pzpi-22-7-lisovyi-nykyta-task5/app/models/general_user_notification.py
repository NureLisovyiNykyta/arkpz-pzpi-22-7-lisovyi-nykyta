from app import db
from datetime import datetime, timezone
import uuid
from app.utils import ErrorHandler
from flask import jsonify

class GeneralUserNotification(db.Model):
    __tablename__ = 'general_user_notifications'

    id = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.UUID(as_uuid=True), db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    importance = db.Column(db.Enum('low', 'medium', 'high', name='importance_enum'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    type = db.Column(db.String(50), nullable=False)
    data = db.Column(db.JSON, nullable=True)

    user = db.relationship('User', back_populates='general_notifications')

    @classmethod
    def create_notification(cls, user_id, title, body, importance, type, data=None):
        new_notification = cls(
            user_id=user_id,
            title=title,
            body=body,
            importance=importance,
            type=type,
            data=data
        )
        try:
            db.session.add(new_notification)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return ErrorHandler.handle_error(
                e,
                message="Database error while creating notification",
                status_code=500
            )

    @classmethod
    def get_notifications_by_user(cls, user_id):
        try:
            notifications = cls.query.filter_by(user_id=user_id).order_by(cls.created_at.desc()).all()

            notifications_list = [
                {
                    "id": str(notification.id),
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
