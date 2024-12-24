from flask_mail import Message
from app import mail, db
from app.models import User
from flask import render_template_string, jsonify
from app.utils import ErrorHandler
import random
import string


def send_password_reset_email(data):
    try:
        if not data or not data.get('email'):
            raise ValueError("Email is required")

        user = User.get_user_by_email(data['email'])
        if not user:
            return ErrorHandler.handle_error(
                None,
                message=f"User with email '{data['email']}' not found.",
                status_code=404
            )

        new_password = generate_random_password()
        update_password(user, new_password)

        with open("templates/password_reset_email.html", "r") as html_file:
            html_template = html_file.read()

        html_body = render_template_string(
            html_template,
            name=user.name,
            new_password=new_password
        )

        msg = Message(
            "Your New Password",
            recipients=[user.email],
            body=f"Your new password is: {new_password}\n"
                 f"You can log in using this password. "
                 f"Please change it after logging in.",
            html=html_body
        )

        mail.send(msg)
        return jsonify({'message': 'A new password has been sent to your email.'}), 200

    except ValueError as ve:
        return ErrorHandler.handle_validation_error(str(ve))
    except Exception as e:
        return ErrorHandler.handle_error(
            e,
            message="Internal server error while sending the password reset email.",
            status_code=500
        )


def generate_random_password(length=8):
    try:
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))
    except Exception as e:
        return ErrorHandler.handle_error(
            e,
            message="Internal server error while generating the random password.",
            status_code=500
        )


def update_password(user, new_password):
    try:
        user.set_password(new_password)
        db.session.commit()
    except Exception as e:
        return ErrorHandler.handle_error(
            e,
            message="Internal server error while updating the user's password.",
            status_code=500
        )
