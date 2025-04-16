from uuid import uuid4
from app.database.service import DB_Service
from app.database.model import User_Status
from typing import Optional
from app.domain.user import create_user
from app.authentication.model import SignUpRequest, JwtResponse, JwtRequest
from app.authentication.jwt_service import JwtProvider, get_uuid_from_token
from app.domain.user import User


class Authentication_Service:
    def __init__(self, dbase: DB_Service):
        self.db_service = dbase

    def authorization(self, jwt_request: JwtRequest) -> Optional[JwtResponse]:
        try:
            db_user = self.db_service.get_user_login(jwt_request.login)
            if db_user is not None and db_user.check_password(jwt_request.password):
                self.db_service.set_status(User_Status.ONLINE, jwt_request.login)
                return JwtResponse(
                    typeToken="Bearer",
                    accessToken=JwtProvider.generate_access_token(
                        create_user(db_user.user_id)
                    ),
                    refreshToken=JwtProvider.generate_refresh_token(
                        create_user(db_user.user_id)
                    ),
                )
        except Exception as e:
            print(f"Ошибка при работе с БД.{e}")
        return None

    def register(self, sign_up_request: SignUpRequest):
        try:
            user = self.db_service.get_user_login(sign_up_request.login)
            if user is not None:
                return False
            new_user = User(
                id_user=uuid4(),
                name=sign_up_request.name,
                login=sign_up_request.login,
                password=sign_up_request.password,
            )
            return self.db_service.save_user(new_user)
        except Exception as e:
            print(f"Ошибка при работе с БД.{e}")
            return False

    @staticmethod
    def refresh_access_token(refreshToken: str) -> Optional[JwtResponse]:
        if JwtProvider.validate_refresh_token(refreshToken):
            new_access_token = JwtProvider.generate_access_token(
                create_user(get_uuid_from_token(refreshToken))
            )
            return JwtResponse(
                typeToken="Bearer",
                accessToken=new_access_token,
                refreshToken=refreshToken,
            )
        return None

    @staticmethod
    def refresh_refreshToken(refreshToken: str) -> Optional[JwtResponse]:
        if JwtProvider.validate_refresh_token(refreshToken):
            new_access_token = JwtProvider.generate_access_token(
                create_user(get_uuid_from_token(refreshToken))
            )
            new_refresh_token = JwtProvider.generate_refresh_token(
                create_user(get_uuid_from_token(refreshToken))
            )
            return JwtResponse(
                typeToken="Bearer",
                accessToken=new_access_token,
                refreshToken=new_refresh_token,
            )
        return None
