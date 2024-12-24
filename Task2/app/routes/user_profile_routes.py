from flask import Blueprint, request
from app.models import MobileDevice, Home, Sensor, DefaultSecurityMode
from app.services.password_reset_service import send_password_reset_email
from app.services import profile_service
from app.utils.auth_decorator import auth_required

user_profile_bp = Blueprint('user_profile', __name__)


@user_profile_bp.route('/profile', methods=['GET'])
@auth_required
def get_profile():
    user = request.current_user
    return profile_service.get_user_profile(user.user_id)


@user_profile_bp.route('/update_profile', methods=['PUT'])
@auth_required
def update_profile():
    user = request.current_user
    data = request.get_json()
    return profile_service.update_user_profile(user.user_id, data)


@user_profile_bp.route('/update_password', methods=['PUT'])
@auth_required
def update_password():
    user = request.current_user
    data = request.get_json()
    return profile_service.update_user_password(user.user_id, data)


@user_profile_bp.route('/reset_password', methods=['POST'])
def reset_password_request():
    data = request.get_json()
    return send_password_reset_email(data)


@user_profile_bp.route('/user_devices', methods=['Get'])
@auth_required
def get_user_devices():
    user = request.current_user
    return MobileDevice.get_user_devices(user.user_id)


@user_profile_bp.route('/add_user_device', methods=['Post'])
@auth_required
def add_user_device():
    user = request.current_user
    data = request.get_json()
    return MobileDevice.add_user_device(user.user_id, data)


@user_profile_bp.route('/delete_user_device/device', methods=['Post'])
@auth_required
def delete_user_device():
    user = request.current_user
    device_id = request.args.get('device')
    return MobileDevice.delete_user_device_(user.user_id, device_id)


@user_profile_bp.route('/user_homes', methods=['Get'])
@auth_required
def get_user_homes():
    user = request.current_user
    return MobileDevice.get_user_devices(user.user_id)


@user_profile_bp.route('/add_user_home', methods=['Post'])
@auth_required
def add_user_home():
    user = request.current_user
    data = request.get_json()
    return MobileDevice.add_user_device(user.user_id, data)


@user_profile_bp.route('/delete_user_home/home', methods=['Post'])
@auth_required
def delete_user_home():
    user = request.current_user
    home_id = request.args.get('home')
    return MobileDevice.delete_user_device_(user.user_id, home_id)


@user_profile_bp.route('/home_sensors', methods=['Get'])
@auth_required
def get_home_sensors():
    user = request.current_user
    return MobileDevice.get_user_devices(user.user_id)


@user_profile_bp.route('/add_home_sensor', methods=['Post'])
@auth_required
def add_home_sensor():
    user = request.current_user
    data = request.get_json()
    return MobileDevice.add_user_device(user.user_id, data)


@user_profile_bp.route('/delete_home_sensors/sensor', methods=['Post'])
@auth_required
def delete_home_sensor():
    user = request.current_user
    sensor_id = request.args.get('sensor')
    return MobileDevice.delete_user_device_(user.user_id, sensor_id)
