from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import AuthContext, get_current_identity
from app.core.security import create_access_token
from app.schemas.auth import (
    DemoLoginRequest,
    DemoResetResponse,
    LoginRequest,
    LoginResponse,
)
from app.schemas.user import AuthUserResponse
from app.services.auth_service import login_user
from app.services.demo_service import (
    get_demo_user,
    get_or_create_demo_session,
    reset_demo_session,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _auth_user_response(identity: AuthContext) -> AuthUserResponse:
    user = identity.user
    return AuthUserResponse(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        role=user.role,
        is_demo=identity.is_demo,
    )


@router.post("/login", response_model=LoginResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    result = login_user(db, login_data.email, login_data.password)
    if result is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user, token = result
    return LoginResponse(
        access_token=token,
        user=AuthUserResponse(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            role=user.role,
            is_demo=False,
        ),
    )


@router.post("/demo-login", response_model=LoginResponse)
def demo_login(
    login_data: DemoLoginRequest,
    db: Session = Depends(get_db),
    x_demo_session: str | None = Header(default=None, alias="X-Demo-Session"),
):
    try:
        demo_session, raw_token = get_or_create_demo_session(db, x_demo_session)
        user = get_demo_user(db, login_data.demo_role)
        access_token = create_access_token(
            user_id=user.id,
            role=user.role,
            demo_session_id=demo_session.id,
        )
        return LoginResponse(
            access_token=access_token,
            user=AuthUserResponse(
                id=user.id,
                full_name=user.full_name,
                email=user.email,
                role=user.role,
                is_demo=True,
            ),
            demo_session_token=raw_token,
            demo_session_expires_at=demo_session.expires_at,
        )
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error))


@router.post("/demo-reset", response_model=DemoResetResponse)
def demo_reset(
    db: Session = Depends(get_db),
    x_demo_session: str | None = Header(default=None, alias="X-Demo-Session"),
):
    return DemoResetResponse(reset=reset_demo_session(db, x_demo_session))


@router.get("/me", response_model=AuthUserResponse)
def read_current_user(identity: AuthContext = Depends(get_current_identity)):
    return _auth_user_response(identity)
