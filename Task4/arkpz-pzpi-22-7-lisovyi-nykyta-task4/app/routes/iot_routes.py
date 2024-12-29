from flask import Blueprint, request
from app.models import Sensor
from app.services import auth_service
from app.utils import ErrorHandler

iot_bp = Blueprint('iot', __name__)


@iot_bp.route('/send_sensor_status', methods=['Put'])
def send_sensor_status():
    data = request.get_json()
    user = auth_service.login_user(data)
    if user:
        return Sensor.set_sensor_status(user.user_id, data)
    return ErrorHandler.handle_error(
        None,
        message="Invalid credentials",
        status_code=403
    )
