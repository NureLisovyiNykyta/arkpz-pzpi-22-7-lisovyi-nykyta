from flask_mail import Message
from flask import render_template
from app import mail
from app.utils import ErrorHandler
import os


def send_subscription_expiration_email(user, subscription, days_left):
    try:
        formatted_end_date = subscription.end_date.strftime('%A, %d %B %Y')

        html_body = render_template(
            'email_subscription_expiration.html',
            name=user.name,
            subscription_name=subscription.plan.name,
            end_date=formatted_end_date,
            cancel_in_days=days_left,
            website_url=os.getenv('FRONTEND_LINK')
        )

        msg = Message(
            subject="Your Subscription is About to Expire",
            recipients=[user.email],
            body=f"""
                Hello {user.name},

                We wanted to inform you that your subscription to {subscription.plan.name} will expire on {subscription.end_date}.
                If you do not renew your subscription, it will be canceled automatically in {days_left} days.

                After cancellation:
                - Your subscription will be replaced with a basic one.
                - Homes and sensors will be archived until the subscription is extended.

                To continue enjoying the benefits of your subscription, please renew it before the expiration date.

                Visit our website for more details: {os.getenv('FRONTEND_LINK')}

                Thank you for using our service!

                Best regards,
                The Subscription Management Team
            """,
            html=html_body
        )

        mail.send(msg)

    except Exception as e:
        return ErrorHandler.handle_error(
            e,
            message="Internal server error while sending subscription expiration email.",
            status_code=500
        )


def send_subscription_canceled_email(user, subscription):
    try:
        formatted_end_date = subscription.end_date.strftime('%A, %d %B %Y')

        html_body = render_template(
            'email_subscription_cancelled.html',
            name=user.name,
            subscription_name=subscription.plan.name,
            end_date=formatted_end_date,
            website_url=os.getenv('FRONTEND_LINK')
        )

        msg = Message(
            subject="Your Subscription has been Canceled",
            recipients=[user.email],
            body=f"""
                Hello {user.name},

                We wanted to inform you that your subscription to {subscription.plan.name} has been canceled.
                The subscription was originally set to expire on {formatted_end_date}.

                Your account is now on a basic plan, and any associated data, including homes and sensors, has been archived.

                Visit our website to renew your subscription: {os.getenv('FRONTEND_LINK')}

                Thank you for being a part of our service!
            """,
            html=html_body
        )

        mail.send(msg)

    except Exception as e:
        return ErrorHandler.handle_error(
            e,
            message="Internal server error while sending subscription cancellation email.",
            status_code=500
        )