from dataclasses import dataclass
from datetime import datetime, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.demo_session import DemoSession
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AuthContext:
    user: User
    demo_session_id: int | None = None

    @property
    def is_demo(self) -> bool:
        return self.demo_session_id is not None


def _utcnow_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def get_current_identity(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> AuthContext:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        user_id = int(user_id)
        demo_session_id = payload.get("demo_session_id")
        demo_session_id = int(demo_session_id) if demo_session_id is not None else None
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except (jwt.InvalidTokenError, TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User no longer exists")

    if demo_session_id is not None:
        demo_session = db.get(DemoSession, demo_session_id)
        if demo_session is None or demo_session.expires_at <= _utcnow_naive():
            raise HTTPException(status_code=401, detail="Demo session has expired")

    return AuthContext(user=user, demo_session_id=demo_session_id)


def require_roles(*allowed_roles: str):
    def role_checker(identity: AuthContext = Depends(get_current_identity)) -> AuthContext:
        if identity.user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to perform this action",
            )
        return identity

    return role_checker
