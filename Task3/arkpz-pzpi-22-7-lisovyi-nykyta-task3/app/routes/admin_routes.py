from flask import Blueprint, request, jsonify
from app.models import User, Subscription, SubscriptionPlan, GeneralUserNotification
from app.utils.auth_decorator import role_required

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/users', methods=['Get'])
@role_required(['admin']) 
def get_users():
    return User.get_all_users()


@admin_bp.route('/user/user', methods=['Get'])
@role_required(['admin']) 
def get_user():
    user_id = request.args.get('user')
    return User.get_user(user_id)


@admin_bp.route('/delete_user/user', methods=['Post'])
@role_required(['admin']) 
def delete_user():
    user_id = request.args.get('user')
    return User.delete_user(user_id)


@admin_bp.route('/register_admin', methods=['Post'])
@role_required(['admin']) 
def register_admin():
    data = request.get_json()
    return User.register_admin(data)


@admin_bp.route('/create_subscription_plan', methods=['Post'])
@role_required(['admin']) 
def create_subscription_plan():
    data = request.get_json()
    return SubscriptionPlan.create_subscription_plan(data)


@admin_bp.route('/user_subscriptions/user', methods=['Get'])
@role_required(['admin']) 
def get_user_subscriptions():
    user_id = request.args.get('user')
    return Subscription.get_user_subscriptions(user_id)


@admin_bp.route('/cancel_current_user_subscription/user', methods=['Put'])
@role_required(['admin']) 
def cancel_current_user_subscription():
    user_id = request.args.get('user')
    return Subscription.cancel_current_subscription(user_id)


@admin_bp.route('/general_user_notifications/user', methods=['Get'])
@role_required(['admin']) 
def get_user_general_notifications():
    user_id = request.args.get('user')
    return GeneralUserNotification.get_notifications_by_user(user_id)
