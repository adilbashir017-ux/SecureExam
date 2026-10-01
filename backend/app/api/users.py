from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import AuthContext, require_roles
from app.schemas.user import UserResponse
from app.services.user_service import get_all_users, get_students, get_user_by_id

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/students", response_model=list[UserResponse])
def read_students(
    db: Session = Depends(get_db),
    identity: AuthContext = Depends(require_roles("lecturer", "admin")),
):
    return get_students(db, demo_only=identity.is_demo)


@router.get("/", response_model=list[UserResponse])
def read_users(
    db: Session = Depends(get_db),
    identity: AuthContext = Depends(require_roles("admin")),
):
    return get_all_users(db)


@router.get("/{user_id}", response_model=UserResponse)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    identity: AuthContext = Depends(require_roles("admin")),
):
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
