from functools import wraps
from flask import request
from app.utils import ErrorHandler, JwtUtils
from app.models import User
from flask_login import current_user


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Check if a token is provided (JWT)
        token = request.headers.get('Authorization')
        if token:
            try:
                # Remove "Bearer" prefix if present
                if token.startswith("Bearer "):
                    token = token.split(" ")[1]

                # Decode the token and extract the payload
                payload = JwtUtils.decode_jwt(token)
                user = User.query.get(payload['user_id'])
                if not user:
                    return ErrorHandler.handle_error(
                        None,
                        message=f"User with ID '{payload['user_id']}' not found.",
                        status_code=404
                    )

                # Attach the user to the request context
                request.current_user = user
            except ValueError as ve:
                return ErrorHandler.handle_error(ve, status_code=401)
            except Exception as e:
                return ErrorHandler.handle_error(
                    e,
                    message="Iternal server error while token verify",
                    status_code=500
                )

            return f(*args, **kwargs)

        # If no JWT token is provided, check if the user is authenticated via Flask-Login session
        if current_user.is_authenticated:
            request.current_user = current_user
            return f(*args, **kwargs)

        # If neither session nor token is valid, return an error
        return ErrorHandler.handle_error(
            None,
            message="Authentication required",
            status_code=401
        )

    return decorated

def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Проверка JWT
            token = request.headers.get('Authorization')
            if token:
                try:
                    if token.startswith("Bearer "):
                        token = token.split(" ")[1]

                    payload = JwtUtils.decode_jwt(token)
                    user = User.query.get(payload['user_id'])
                    if not user:
                        return ErrorHandler.handle_error(
                            None,
                            message=f"User with ID '{payload['user_id']}' not found.",
                            status_code=404
                        )

                    if user.role.role_name not in roles:
                        return ErrorHandler.handle_error(
                            None,
                            message=f"User does not have the required role. Required roles: {roles}",
                            status_code=403
                        )

                    request.current_user = user
                except ValueError as ve:
                    return ErrorHandler.handle_error(ve, status_code=401)
                except Exception as e:
                    return ErrorHandler.handle_error(
                        e,
                        message="Internal server error while token verify",
                        status_code=500
                    )
                return f(*args, **kwargs)

            if current_user.is_authenticated:
                if current_user.role.role_name not in roles:
                    return ErrorHandler.handle_error(
                        None,
                        message=f"User does not have the required role. Required roles: {roles}",
                        status_code=403
                    )
                request.current_user = current_user
                return f(*args, **kwargs)

            return ErrorHandler.handle_error(
                None,
                message="Authentication required",
                status_code=401
            )

        return decorated
    return decorator
