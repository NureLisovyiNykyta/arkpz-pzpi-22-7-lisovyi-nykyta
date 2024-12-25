from app.models import User, Subscription
from app import login_manager
from app.services.email_confirm_service import send_email_confirmation
from app.utils import ErrorHandler, JwtUtils
from flask import jsonify
import flask_login


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


def register_user(data):
    try:
        email = data.get('email')
        if not email:
            raise ValueError("Email is required for registration.")

        existing_user = User.get_user_by_email(email)

        if existing_user:
            if existing_user.google_id:
                existing_user.drop_email_verification()
                send_email_confirmation(existing_user)
                existing_user.add_user_data(data)
                return jsonify({'message': 'User data updated successfully.'}), 200
            raise ValueError('User already exists.')

        user = User.register_user(data)
        Subscription.create_basic_subscription(user)

        if not user.email_confirmed:
            send_email_confirmation(user)
        return jsonify({'message': 'User registered successfully.'}), 201

    except ValueError as ve:
        return ErrorHandler.handle_validation_error(str(ve))
    except RuntimeError as re:
        return ErrorHandler.handle_error(re, message=str(re), status_code=500)
    except Exception as e:
        return ErrorHandler.handle_error(
            e,
            message="Internal Server Error while register",
            status_code=500
        )


def session_login_user(data):
    try:
        user = login_user(data)
        if user:
            flask_login.login_user(user)
            return jsonify({'message': 'Logged in successfully.'}), 200

        raise PermissionError('Invalid credentials.')

    except ValueError as ve:
        return ErrorHandler.handle_validation_error(str(ve))
    except PermissionError as pe:
        return ErrorHandler.handle_error(pe, message=str(pe), status_code=403)
    except RuntimeError as re:
        return ErrorHandler.handle_error(re, message=str(re), status_code=500)
    except Exception as e:
        return ErrorHandler.handle_error(
            e,
            message="Internal server error during session login",
            status_code=500
        )


def token_login_user(data):
    try:
        user = login_user(data)
        if user:
            token = JwtUtils.generate_jwt({'user_id': str(user.user_id)})
            return jsonify({'message': 'Logged in successfully.', 'token': token}), 200

        raise PermissionError('Invalid credentials.')

    except ValueError as ve:
        return ErrorHandler.handle_validation_error(str(ve))
    except PermissionError as pe:
        return ErrorHandler.handle_error(pe, message=str(pe), status_code=403)
    except RuntimeError as re:
        return ErrorHandler.handle_error(re, message=str(re), status_code=500)
    except Exception as e:
        return ErrorHandler.handle_error(
            e,
            message="Internal server error during token login",
            status_code=500
        )


def login_user(data):
    email = data.get('email')
    if not email:
        raise ValueError("Email is required for login.")

    user = User.get_user_by_email(email)
    if not user:
        raise PermissionError('Invalid credentials.')

    if not user.email_confirmed:
        send_email_confirmation(user)
        raise PermissionError("Please confirm your email first.")

    if user.password is None:
        raise PermissionError('Please login via Google or complete regular registration.')

    if user.check_password(data.get('password')):
        return user

    raise PermissionError('Invalid credentials.')


def logout_user():
    try:
        if flask_login.current_user.is_authenticated:
            flask_login.logout_user()
            return jsonify({'message': 'Logged out successfully.'}), 200
        else:
            return ErrorHandler.handle_error(
                None,
                message="No user logged in",
                status_code=401
            )
    except Exception as e:
        return ErrorHandler.handle_error(
            e,
            message="Internal server error while logout",
            status_code=500
        )
