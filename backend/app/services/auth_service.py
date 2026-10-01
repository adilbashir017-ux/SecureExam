import os

from sqlalchemy.orm import Session

from app.core.demo_config import (
    DEMO_ADMIN_ID,
    DEMO_ALICE_ID,
    DEMO_BOB_ID,
    DEMO_EVE_ID,
    DEMO_LECTURER_ID,
)
from app.core.security import create_access_token, verify_password
from app.services.user_service import get_user_by_email

DEMO_USER_IDS = {
    DEMO_LECTURER_ID,
    DEMO_ADMIN_ID,
    DEMO_ALICE_ID,
    DEMO_BOB_ID,
    DEMO_EVE_ID,
}


def _demo_password_login_allowed() -> bool:
    return os.getenv("ALLOW_DEMO_PASSWORD_LOGIN", "false").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def login_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if user is None:
        return None

    # Public demo identities are intended to use /auth/demo-login so they always
    # receive an isolated sandbox. Password login can be enabled explicitly for
    # local development if needed.
    if user.id in DEMO_USER_IDS and not _demo_password_login_allowed():
        return None

    if not verify_password(password, user.password_hash):
        return None

    token = create_access_token(user_id=user.id, role=user.role)
    return user, token
