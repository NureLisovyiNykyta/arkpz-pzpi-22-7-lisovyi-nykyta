from app import db
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID
import uuid
from flask import jsonify
from app.utils import ErrorHandler
import os


class Sensor(db.Model):
    __tablename__ = 'sensor'

    sensor_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    configuration = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    home_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey('home.home_id', ondelete='CASCADE'),
        nullable=False
    )
    home = db.relationship('UserHome', back_populates='sensors')

