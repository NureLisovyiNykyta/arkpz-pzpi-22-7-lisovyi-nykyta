from flask import Blueprint, request
from app.models import MobileDevice
from app.utils.auth_decorator import role_required

mobile_device_bp = Blueprint('mobile_device', __name__)


@mobile_device_bp.route('/mobile_devices', methods=['Get'])
@role_required(['user']) 
def get_mobile_devices():
    user = request.current_user
    return MobileDevice.get_user_devices(user.user_id)


@mobile_device_bp.route('/add_mobile_device', methods=['Post'])
@role_required(['user']) 
def add_mobile_device():
    user = request.current_user
    data = request.get_json()
    return MobileDevice.add_user_device(user.user_id, data)


@mobile_device_bp.route('/delete_mobile_device', methods=['Post'])
@role_required(['user']) 
def delete_mobile_device():
    user = request.current_user
    data = request.get_json()
    return MobileDevice.delete_device_by_token_and_user(user.user_id, data)
