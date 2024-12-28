from flask import Blueprint, request
from app.models import SecurityUserNotification, GeneralUserNotification
from app.utils.auth_decorator import role_required

notification_bp = Blueprint('notification', __name__)


@notification_bp.route('/general_notifications', methods=['Get'])
@role_required(['user']) 
def get_general_notifications():
    user = request.current_user
    return GeneralUserNotification.get_notifications_by_user(user.user_id)


@notification_bp.route('/security_notifications', methods=['Get'])
@role_required(['user']) 
def get_security_notifications():
    user = request.current_user
    return SecurityUserNotification.get_notifications_by_user(user.user_id)


@notification_bp.route('/security_notifications_by_home/home', methods=['Get'])
@role_required(['user']) 
def get_security_notifications_by_home():
    home_id = request.args.get('home')
    return SecurityUserNotification.get_notifications_by_home(home_id)
