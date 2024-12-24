from flask import jsonify
from werkzeug.exceptions import HTTPException

class ErrorHandler:
    @staticmethod
    def handle_error(error, message=None, status_code=None):
        if isinstance(error, HTTPException):
            response = jsonify({
                "error": error.name,
                "message": message + error.description
            })
            response.status_code = status_code + error.code
        else:
            response = jsonify({
                "error": "Internal Server Error",
                "message": message + str(error)
            })
            response.status_code = status_code or 500
        return response

    @staticmethod
    def handle_validation_error(message):
        if isinstance(message, dict):
            error_messages = []
            for field, errors in message.items():
                error_messages.append(f"{field}: {', '.join(errors)}")
            message = "; ".join(error_messages)

        return {
            'success': False,
            'message': message
        }, 400
