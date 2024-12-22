from app import db
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID
import uuid
from flask import jsonify
from app.utils import ErrorHandler
import os

class UserHome(db.Model):
    __tablename__ = 'home'

    home_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.user_id'), nullable=False)
    user = db.relationship('User', back_populates='homes')

    sensors = db.relationship(
        'Sensor',
        back_populates='home',
        cascade="all, delete-orphan"
    )



