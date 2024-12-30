from flask import jsonify
from app.utils import ErrorHandler, FirebaseUtils, JwtUtils
from app.models import User


def firebase_auth(data):
    try:
        firebase_id_token = data.get('firebase_id_token')
        if not firebase_id_token:
            raise ValueError("firebase_id_token is required for firebase authentication.")

        decoded_firebase_id_token = FirebaseUtils.verify_token(firebase_id_token)
        if decoded_firebase_id_token:
            user_email = decoded_firebase_id_token.get('email')
            user_name = decoded_firebase_id_token.get('name')
            user_google_id = decoded_firebase_id_token.get('sub')

            existing_user = User.get_user_by_email(user_email)

            if existing_user:
                if not existing_user.google_id:
                    existing_user.add_google_data(user_google_id)
                    existing_user.verify_email()
                token = JwtUtils.generate_jwt({'user_id': str(existing_user.user_id)})
            else:
                data = {
                    'name': user_name,
                    'email': user_email,
                    'google_id': user_google_id,
                }
                user = User.google_register_user(data)
                user.verify_email()

                token = JwtUtils.generate_jwt({'user_id': str(user.user_id)})

            return  jsonify({'message': 'Firebase logged in successfully.', 'token': token}), 200
        else:
            raise PermissionError('Invalid firebase_id_token.')

    except ValueError as ve:
        return ErrorHandler.handle_validation_error(str(ve))
    except PermissionError as pe:
        return ErrorHandler.handle_error(pe, message=str(pe), status_code=403)
    except RuntimeError as re:
        return ErrorHandler.handle_error(re, message=str(re), status_code=500)
    except Exception as e:
        return ErrorHandler.handle_error(
            e,
            message="Internal server error during Google login",
            status_code=500
        )
