from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr


class UserRole(str, Enum):
    STUDENT = "student"
    LECTURER = "lecturer"
    ADMIN = "admin"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    role: UserRole


class AuthUserResponse(UserResponse):
    is_demo: bool = False
