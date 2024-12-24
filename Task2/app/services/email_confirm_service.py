from app.models import User
from app import mail
from app.config import Config
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from flask import url_for, render_template_string, jsonify
from app.utils import ErrorHandler

s = URLSafeTimedSerializer(Config.SECRET_KEY)


def send_email_confirmation(user):
    try:
        token = s.dumps(user.email, salt='email-confirm-salt')
        confirmation_url = url_for('auth.confirm_email', token=token, _external=True)

        with open("templates/email_confirmation.html", "r") as html_file:
            html_template = html_file.read()

        html_body = render_template_string(
            html_template,
            name=user.name,
            confirmation_url=confirmation_url
        )

        msg = Message(
            "Email Confirmation",
            recipients=[user.email],
            body=f"To confirm your email address, "
                 f"visit the following link: {confirmation_url}",
            html=html_body)

        mail.send(msg)
        return jsonify({'message': 'The email confirmation was sent successfully.'}), 200

    except Exception as e:
        return ErrorHandler.handle_error(
            e,
            message="Internal server error while sending the email confirmation.",
            status_code=500
        )


def verify_email_token(token):
    try:
        email = s.loads(token, salt='email-confirm-salt', max_age=3600)
        user = User.query.filter_by(email=email).first()

        if user is None:
            raise PermissionError('The token is invalid or expired.')

        user.verify_email()

        with open("templates/email_confirmation_success.html", "r") as html_file:
            success_html_template = html_file.read()

        success_html_body = render_template_string(
            success_html_template,
            user=user
        )

        return success_html_body

    except PermissionError as pe:
        with open("templates/email_confirmation_error.html", "r") as html_file:
            error_html_template = html_file.read()

        error_html_body = render_template_string(
            error_html_template,
            error_message=str(pe)
        )

        return error_html_body

    except RuntimeError as re:
        with open("templates/email_confirmation_error.html", "r") as html_file:
            error_html_template = html_file.read()

        error_html_body = render_template_string(
            error_html_template,
            error_message=str(re)
        )
        return error_html_body

    except Exception as e:
        with open("templates/email_confirmation_error.html", "r") as html_file:
            error_html_template = html_file.read()

        error_html_body = render_template_string(
            error_html_template,
            error_message=f"Internal server error during email confirmation. {str(e)}"
        )
        return error_html_body
