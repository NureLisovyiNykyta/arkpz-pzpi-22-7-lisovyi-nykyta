from app import db
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID
import uuid
from flask import jsonify
from app.utils import ErrorHandler


class Role(db.Model):
    __tablename__ = 'role'

    role_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)

    users = db.relationship(
        'User',
        back_populates='role',
        cascade="all, delete-orphan"
    )
