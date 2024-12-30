from flask import Blueprint, request, jsonify, render_template, current_app, url_for
import stripe
from app.models import SubscriptionPlan, Subscription
from app.utils.auth_decorator import role_required
from app.utils import ErrorHandler

payments_bp = Blueprint('payments', __name__)


@payments_bp.route('/create-checkout-session', methods=['POST'])
@role_required(['user']) 
def create_checkout_session():
    try:
        data = request.json
        plan_id = data.get('plan_id')
        user = request.current_user

        if not plan_id:
            raise ValueError("Plan id required for subscription payment.")

        plan = SubscriptionPlan.query.filter_by(plan_id=plan_id).first()
        if not plan:
            return ErrorHandler.handle_error(
                None,
                message=f"Subscription plan with ID '{plan_id}' not found.",
                status_code=404
            )

        if plan.name == 'basic':
            raise ValueError("Cannot purchase a basic plan as a paid subscription.")

        current_subscription = Subscription.get_current_subscription(user.user_id)
        if not current_subscription:
            raise ValueError("User does not have an active subscription..")

        if current_subscription.plan.name not in ['basic', plan.name]:
            raise ValueError(f"You already have '{current_subscription.plan.name}' subscription. "
                             f"Canceled it first to purchase another paid subscription!")

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': plan.name,
                        'description': plan.description,
                    },
                    'unit_amount': int(plan.price * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('payments.payment_success', _external=True),
            cancel_url=url_for('payments.payment_cancel', _external=True),
            metadata={'user_id': user.user_id, 'plan_id': plan_id}
        )

        return jsonify({"url": session.url}), 200

    except ValueError as ve:
        return ErrorHandler.handle_validation_error(str(ve))
    except RuntimeError as re:
        return ErrorHandler.handle_error(re, message=str(re), status_code=500)
    except Exception as e:
        return ErrorHandler.handle_error(
            e,
            message="Internal Server Error while creating checkout session",
            status_code=500
        )

@payments_bp.route('/success', methods=['GET'])
@role_required(['user']) 
def payment_success():
    try:
        session_id = request.args.get('session_id')

        session = stripe.checkout.Session.retrieve(session_id)

        user_id = session.metadata.get('user_id')
        plan_id = session.metadata.get('plan_id')

        plan = SubscriptionPlan.query.filter_by(plan_id=plan_id).first()

        current_subscription = Subscription.get_current_subscription(user_id)
        if current_subscription.plan.name == 'basic':
            Subscription.purchase_paid_subscription(user_id, plan_id)

        if current_subscription.plan.name == plan.name:
            Subscription.extend_current_subscription(user_id)

    except ValueError as ve:
        return ErrorHandler.handle_validation_error(str(ve))
    except RuntimeError as re:
        return ErrorHandler.handle_error(re, message=str(re), status_code=500)
    except Exception as e:
        return ErrorHandler.handle_error(
            e,
            message="Internal Server Error while creating checkout session",
            status_code=500
        )

@payments_bp.route('/cancel', methods=['GET'])
@role_required(['user']) 
def payment_cancel():
    return render_template('cancelled.html',
                           message="Payment was cancelled. Please try again if needed.")
