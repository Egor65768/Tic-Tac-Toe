from pydantic import BaseModel


class JwtRequest(BaseModel):
    login: str
    password: str


class JwtResponse(BaseModel):
    typeToken: str
    accessToken: str
    refreshToken: str


class RefreshJwtRequest(BaseModel):
    refreshToken: str


class SignUpRequest(BaseModel):
    login: str
    password: str
    name: str
