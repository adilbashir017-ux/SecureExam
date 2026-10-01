from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.demo_config import DEMO_STUDENT_IDS
from app.models.user import User
from app.schemas.user import UserRole


def get_all_users(db: Session):
    return db.scalars(select(User).order_by(User.id)).all()


def get_students(db: Session, demo_only: bool = False):
    statement = select(User).where(User.role == UserRole.STUDENT.value)

    if demo_only:
        statement = statement.where(User.id.in_(DEMO_STUDENT_IDS))

    statement = statement.order_by(User.id)
    return db.scalars(statement).all()


def get_user_by_id(db: Session, user_id: int):
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str):
    return db.scalar(select(User).where(User.email == email))
