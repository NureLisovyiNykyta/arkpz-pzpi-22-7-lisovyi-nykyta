from flask import Blueprint, request
from app.models import SubscriptionPlan, Subscription
from app.utils.auth_decorator import auth_required

subscription_bp = Blueprint('subscription', __name__)


@subscription_bp.route('/subscription_plans', methods=['Get'])
def get_subscription_plans():
    return SubscriptionPlan.get_all_subscription_plans()


@subscription_bp.route('/current_subscription', methods=['Get'])
@auth_required
def get_current_subscription():
    user = request.current_user
    return Subscription.get_current_subscription_info(user.user_id)


@subscription_bp.route('/cancel_current_subscription', methods=['Put'])
@auth_required
def cancel_current_subscription():
    user = request.current_user
    return Subscription.cancel_current_subscription(user.user_id)