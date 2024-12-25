from app.models import User
from flask import jsonify
from app.utils import ErrorHandler


def get_user_profile(user_id):
    try:
        user = User.query.get(user_id)
        if user:
            return jsonify(user.get_profile_data())
        else:
            return ErrorHandler.handle_error(
                None,
                message=f"User with ID '{user_id}' not found.",
                status_code=404
            )
    except Exception as e:
        return ErrorHandler.handle_error(
            e,
            message="Internal server error while retrieving the user profile.",
            status_code=500
        )


def update_user_profile(user_id, data):
    try:
        user = User.query.get(user_id)
        if user:
            user.update_profile(data)
            return jsonify({'message': 'Profile updated successfully.'}), 200
        else:
            return ErrorHandler.handle_error(
                None,
                message=f"User with ID '{user_id}' not found.",
                status_code=404
            )
    except ValueError as ve:
        return ErrorHandler.handle_validation_error(str(ve))
    except RuntimeError as re:
        return ErrorHandler.handle_error(re, message=str(re), status_code=500)
    except Exception as e:
        return ErrorHandler.handle_error(
            e,
            message="Internal server error while updating the user profile.",
            status_code=500
        )


def update_user_password(user_id, data):
    try:
        user = User.query.get(user_id)
        if user:
            user.update_password(data)
            return jsonify({'message': 'Password updated successfully.'}), 200
        else:
            return ErrorHandler.handle_error(None, message="User not found.", status_code=404)
    except ValueError as ve:
        return ErrorHandler.handle_validation_error(str(ve))
    except RuntimeError as re:
        return ErrorHandler.handle_error(re, message=str(re), status_code=500)
    except Exception as e:
        return ErrorHandler.handle_error(
            e,
            message="Internal server error while updating password.",
            status_code=500
        )
