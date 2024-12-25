from flask import Blueprint, request
from app.models import Home, Sensor, DefaultSecurityMode
from app.utils.auth_decorator import auth_required

security_bp = Blueprint('security', __name__)


@security_bp.route('/user_homes', methods=['Get'])
@auth_required
def get_user_homes():
    user = request.current_user
    return Home.get_all_homes(user.user_id)


@security_bp.route('/add_user_home', methods=['Post'])
@auth_required
def add_user_home():
    user = request.current_user
    data = request.get_json()
    return Home.add_home(user.user_id, data)


@security_bp.route('/delete_user_home/home', methods=['Post'])
@auth_required
def delete_user_home():
    user = request.current_user
    home_id = request.args.get('home')
    return Home.delete_home(user.user_id, home_id)


@security_bp.route('/home_sensors', methods=['Get'])
@auth_required
def get_home_sensors():
    user = request.current_user
    return Sensor.get_all_sensors(user.user_id)


@security_bp.route('/add_home_sensor', methods=['Post'])
@auth_required
def add_home_sensor():
    user = request.current_user
    data = request.get_json()
    return Sensor.add_sensor(user.user_id, data)


@security_bp.route('/delete_home_sensors/sensor', methods=['Post'])
@auth_required
def delete_home_sensor():
    user = request.current_user
    sensor_id = request.args.get('sensor')
    return Sensor.delete_sensor(user.user_id, sensor_id)


@security_bp.route('/set_home_sensor_activity', methods=['Put'])
@auth_required
def set_home_sensor_activity():
    user = request.current_user
    data = request.get_json()
    return Sensor.set_sensor_activity(user.user_id, data)


@security_bp.route('/default_security_modes', methods=['Get'])
@auth_required
def get_default_security_modes():
    return DefaultSecurityMode.get_all_default_modes()


@security_bp.route('/archive_home_sensors/home', methods=['Put'])
@auth_required
def archive_home_sensors():
    user = request.current_user
    home_id = request.args.get('home')
    return Home.archive_home_sensors(user.user_id, home_id)


@security_bp.route('/unarchive_home/home', methods=['Put'])
@auth_required
def unarchive_home():
    user = request.current_user
    home_id = request.args.get('home')
    return Home.unarchive_home(user.user_id, home_id)


@security_bp.route('/archive_home/sensor', methods=['Put'])
@auth_required
def archive_sensor():
    user = request.current_user
    sensor_id = request.args.get('sensor')
    return Sensor.archive_sensor(user.user_id, sensor_id)


@security_bp.route('/unarchive_home/sensor', methods=['Put'])
@auth_required
def unarchive_sensor():
    user = request.current_user
    sensor_id = request.args.get('sensor')
    return Sensor.unarchive_sensor(user.user_id, sensor_id)
