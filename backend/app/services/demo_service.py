import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.demo_config import (
    DEMO_ADMIN_ID,
    DEMO_ALICE_ID,
    DEMO_BOB_ID,
    DEMO_EVE_ID,
    DEMO_LECTURER_ID,
    DEMO_ROLE_TO_USER_ID,
)
from app.core.security import hash_password
from app.crypto.falcon_module import falcon_keygen
from app.crypto.kyber_module import kyber_keygen
from app.models.demo_session import DemoSession
from app.models.demo_session_exam import DemoSessionExam
from app.models.exam import Exam
from app.models.exam_access import ExamAccess
from app.models.exam_crypto import ExamCrypto
from app.models.exam_key_package import ExamKeyPackage
from app.models.submission import Submission
from app.models.student_crypto_key import StudentCryptoKey
from app.models.system_signing_key import SystemSigningKey
from app.models.user import User
from app.schemas.auth import DemoRole
from app.schemas.exam import ExamCreate
from app.services.exam_service import create_exam, publish_exam

SYSTEM_SIGNING_KEY_NAME = "main-system-key"

DEMO_USERS = [
    (
        DEMO_LECTURER_ID,
        "Dr. David Cohen",
        "david@secureexam.com",
        "lecturer",
        "DEMO_LECTURER_PASSWORD",
    ),
    (
        DEMO_ADMIN_ID,
        "System Administrator",
        "admin@secureexam.com",
        "admin",
        "DEMO_ADMIN_PASSWORD",
    ),
    (
        DEMO_ALICE_ID,
        "Alice Student",
        "alice@secureexam.com",
        "student",
        "DEMO_ALICE_PASSWORD",
    ),
    (
        DEMO_BOB_ID,
        "Bob Student",
        "bob@secureexam.com",
        "student",
        "DEMO_BOB_PASSWORD",
    ),
    (
        DEMO_EVE_ID,
        "Eve Student",
        "eve@secureexam.com",
        "student",
        "DEMO_EVE_PASSWORD",
    ),
]

DEFAULT_EXAM_TITLE = "Data Security Final"
DEFAULT_EXAM_COURSE = "Data Security & Cryptology"
DEFAULT_EXAM_DURATION = 120
DEFAULT_EXAM_CONTENT = """Data Security Final

Question 1: Explain symmetric encryption.

Question 2: Explain asymmetric encryption.

Question 3: What is a digital signature?"""


def _utcnow_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _demo_session_hours() -> int:
    try:
        configured = int(os.getenv("DEMO_SESSION_HOURS", "12"))
    except ValueError:
        configured = 12
    return max(1, min(configured, 72))


def generate_demo_token() -> str:
    return f"dmo_{secrets.token_urlsafe(32)}"


def hash_demo_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def ensure_demo_prerequisites(db: Session) -> None:
    for user_id, full_name, email, role, env_name in DEMO_USERS:
        user = db.get(User, user_id)
        same_email_user = db.scalar(select(User).where(User.email == email))

        if user is None:
            if same_email_user is not None and same_email_user.id != user_id:
                raise ValueError(
                    f"Demo email {email} already belongs to another user. "
                    "Use a clean SecureExam database or restore the expected demo users."
                )
            db.add(
                User(
                    id=user_id,
                    full_name=full_name,
                    email=email,
                    role=role,
                    password_hash=hash_password(
                        os.getenv(env_name) or secrets.token_urlsafe(24)
                    ),
                )
            )
        elif user.email != email or user.role != role:
            raise ValueError(
                f"Demo user ID {user_id} is already used by a different account. "
                "Use a clean SecureExam database or restore the expected demo users."
            )

    db.flush()

    for user_id in (DEMO_ALICE_ID, DEMO_BOB_ID, DEMO_EVE_ID):
        if db.get(StudentCryptoKey, user_id) is None:
            public_key, private_key = kyber_keygen()
            db.add(
                StudentCryptoKey(
                    user_id=user_id,
                    kyber_public_key=public_key,
                    kyber_private_key=private_key,
                )
            )

    signing_key = db.scalar(
        select(SystemSigningKey).where(
            SystemSigningKey.key_name == SYSTEM_SIGNING_KEY_NAME
        )
    )
    if signing_key is None:
        public_key, private_key = falcon_keygen()
        db.add(
            SystemSigningKey(
                key_name=SYSTEM_SIGNING_KEY_NAME,
                falcon_public_key=public_key,
                falcon_private_key=private_key,
            )
        )

    db.flush()


def _delete_demo_session(db: Session, session: DemoSession) -> None:
    exam_ids = list(
        db.scalars(
            select(DemoSessionExam.exam_id).where(
                DemoSessionExam.demo_session_id == session.id
            )
        ).all()
    )

    if exam_ids:
        # Delete child data explicitly. This works even if an existing MySQL
        # installation was created without ON DELETE CASCADE constraints.
        db.execute(delete(Submission).where(Submission.exam_id.in_(exam_ids)))
        db.execute(delete(ExamKeyPackage).where(ExamKeyPackage.exam_id.in_(exam_ids)))
        db.execute(delete(ExamCrypto).where(ExamCrypto.exam_id.in_(exam_ids)))
        db.execute(delete(ExamAccess).where(ExamAccess.exam_id.in_(exam_ids)))

    db.execute(
        delete(DemoSessionExam).where(
            DemoSessionExam.demo_session_id == session.id
        )
    )

    if exam_ids:
        db.execute(delete(Exam).where(Exam.id.in_(exam_ids)))

    db.delete(session)
    db.flush()


def cleanup_expired_demo_sessions(db: Session) -> int:
    now = _utcnow_naive()
    sessions = list(
        db.scalars(
            select(DemoSession).where(DemoSession.expires_at <= now)
        ).all()
    )

    for session in sessions:
        _delete_demo_session(db, session)

    return len(sessions)


def _seed_demo_session(db: Session, demo_session_id: int) -> None:
    lecturer = db.get(User, DEMO_LECTURER_ID)
    if lecturer is None:
        raise ValueError("Demo lecturer account is not available")

    exam = create_exam(
        ExamCreate(
            title=DEFAULT_EXAM_TITLE,
            course=DEFAULT_EXAM_COURSE,
            authorized_student_ids=[DEMO_ALICE_ID, DEMO_BOB_ID],
            duration_minutes=DEFAULT_EXAM_DURATION,
        ),
        db,
        lecturer,
        demo_session_id=demo_session_id,
        commit=False,
    )

    publish_exam(
        db=db,
        exam_id=exam.id,
        lecturer_id=lecturer.id,
        exam_content=DEFAULT_EXAM_CONTENT,
        demo_session_id=demo_session_id,
        commit=False,
    )


def get_or_create_demo_session(
    db: Session,
    raw_token: str | None,
) -> tuple[DemoSession, str]:
    try:
        cleanup_expired_demo_sessions(db)

        if raw_token:
            token_hash = hash_demo_token(raw_token)
            existing = db.scalar(
                select(DemoSession).where(DemoSession.token_hash == token_hash)
            )
            if existing is not None and existing.expires_at > _utcnow_naive():
                db.commit()
                return existing, raw_token

        ensure_demo_prerequisites(db)

        new_raw_token = generate_demo_token()
        session = DemoSession(
            token_hash=hash_demo_token(new_raw_token),
            expires_at=_utcnow_naive() + timedelta(hours=_demo_session_hours()),
        )
        db.add(session)
        db.flush()

        _seed_demo_session(db, session.id)
        db.commit()
        db.refresh(session)
        return session, new_raw_token
    except Exception:
        db.rollback()
        raise


def get_demo_user(db: Session, demo_role: DemoRole) -> User:
    user_id = DEMO_ROLE_TO_USER_ID[demo_role.value]
    user = db.get(User, user_id)
    if user is None:
        raise ValueError("Demo user is not available")
    return user


def reset_demo_session(db: Session, raw_token: str | None) -> bool:
    if not raw_token:
        return False

    try:
        token_hash = hash_demo_token(raw_token)
        session = db.scalar(
            select(DemoSession).where(DemoSession.token_hash == token_hash)
        )
        if session is None:
            return False

        _delete_demo_session(db, session)
        db.commit()
        return True
    except Exception:
        db.rollback()
        raise
