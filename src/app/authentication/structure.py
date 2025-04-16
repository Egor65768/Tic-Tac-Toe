from flask import session, Response
from app.web.route import auth_service, request_validation
from app.web.route import Constant_validation


class UserAuthenticator:
    @staticmethod
    def is_authenticated():
        user_login = session.get("user_login")
        if user_login:
            return True
        return False

    @staticmethod
    def get_login():
        return session.get("user_login")

    @staticmethod
    def get_name():
        user = auth_service.db_service.get_user_login(UserAuthenticator.get_login())
        if user is not None:
            return user.name
        return None


def jwt_authorization(func):
    def wrapper(*args, **kwargs):
        validation_result = request_validation()
        if isinstance(validation_result, Response):
            return validation_result
        response = func(*args, **kwargs)
        if validation_result[1] != Constant_validation.TOKENS_UNCHANGED:
            response.set_cookie("access_token", validation_result[0], httponly=False)
        return response

    return wrapper
