from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import decode_token
from flask_jwt_extended.exceptions import JWTDecodeError
from jwt import ExpiredSignatureError
from app.domain.user import User
from flask import abort


class Constant_validation:
    ACCESS_TOKEN = 0
    SUCCESSFUL_VALIDATION = 1
    EXPIRED_TOKEN = 2
    EXPIRED_REFRESH_TOKEN = 3
    NEW_ACCESS_TOKEN = 4
    NEW_REFRESH_TOKEN = 5
    TOKENS_UNCHANGED = 6
    LACK_TOKEN = 7


def get_uuid_from_token(token: str):
    try:
        my_decode_token = decode_token(token)
        return my_decode_token["sub"]
    except JWTDecodeError as error:
        print(error)
        abort(401)


class JwtProvider:

    @staticmethod
    def generate_access_token(user: User):
        return create_access_token(identity=user.id)

    @staticmethod
    def generate_refresh_token(user: User):
        return create_refresh_token(identity=user.id)

    @staticmethod
    def validate_refresh_token(token: str):
        from app.web.route import db_service

        try:
            user_uuid = get_uuid_from_token(token)
        except ExpiredSignatureError:
            return Constant_validation.EXPIRED_REFRESH_TOKEN
        if not (user_uuid is not None and db_service.get_user(user_uuid) is not None):
            abort(401)
        return Constant_validation.SUCCESSFUL_VALIDATION

    @staticmethod
    def validate_access_token(token: str):
        from app.web.route import db_service

        try:
            user_uuid = get_uuid_from_token(token)
        except ExpiredSignatureError:
            return Constant_validation.EXPIRED_TOKEN
        if not (user_uuid is not None and db_service.get_user(user_uuid) is not None):
            abort(401)
        return Constant_validation.SUCCESSFUL_VALIDATION
