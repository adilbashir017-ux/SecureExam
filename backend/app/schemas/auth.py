from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr

from app.schemas.user import AuthUserResponse


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class DemoRole(str, Enum):
    LECTURER = "lecturer"
    AUTHORIZED_STUDENT = "authorized_student"
    UNAUTHORIZED_STUDENT = "unauthorized_student"


class DemoLoginRequest(BaseModel):
    demo_role: DemoRole


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AuthUserResponse
    demo_session_token: str | None = None
    demo_session_expires_at: datetime | None = None


class DemoResetResponse(BaseModel):
    reset: bool
