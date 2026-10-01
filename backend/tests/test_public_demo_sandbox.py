import os

os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret-key")

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models import (  # noqa: F401
    DemoSession,
    DemoSessionExam,
    Exam,
    ExamAccess,
    ExamCrypto,
    ExamKeyPackage,
    StudentCryptoKey,
    Submission,
    SystemSigningKey,
    User,
)
from app.schemas.auth import DemoRole
from app.services.demo_service import (
    get_demo_user,
    get_or_create_demo_session,
    reset_demo_session,
)
from app.services.exam_service import (
    attempt_exam,
    get_exams_for_user,
    is_student_authorized,
)
from app.services.submission_service import (
    decrypt_submission_for_lecturer,
    submit_exam_answer,
)


def _make_db():
    engine = create_engine("sqlite+pysqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def _enable_fk(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False)()


def test_demo_sessions_are_isolated_and_survive_role_switching():
    db = _make_db()
    try:
        session_a, token_a = get_or_create_demo_session(db, None)
        session_a_again, token_a_again = get_or_create_demo_session(db, token_a)

        assert session_a_again.id == session_a.id
        assert token_a_again == token_a

        david = get_demo_user(db, DemoRole.LECTURER)
        alice = get_demo_user(db, DemoRole.AUTHORIZED_STUDENT)
        eve = get_demo_user(db, DemoRole.UNAUTHORIZED_STUDENT)

        david_exams = get_exams_for_user(db, david, session_a.id)
        assert len(david_exams) == 1
        exam_id_a = david_exams[0].id

        assert is_student_authorized(exam_id_a, alice.id, db, session_a.id) is True
        assert is_student_authorized(exam_id_a, eve.id, db, session_a.id) is False

        alice_attempt = attempt_exam(db, exam_id_a, alice, session_a.id)
        assert alice_attempt["signature_valid"] is True
        assert alice_attempt["decryption_successful"] is True
        assert "Explain symmetric encryption" in alice_attempt["exam_content"]

        eve_attempt = attempt_exam(db, exam_id_a, eve, session_a.id)
        assert eve_attempt["signature_valid"] is True
        assert eve_attempt["key_available"] is False
        assert eve_attempt["decryption_successful"] is False
        assert eve_attempt["exam_content"] is None

        submission = submit_exam_answer(
            db,
            exam_id_a,
            alice,
            "Symmetric encryption uses the same secret key.",
            session_a.id,
        )
        _, plaintext = decrypt_submission_for_lecturer(
            db,
            exam_id_a,
            submission.id,
            david,
            session_a.id,
        )
        assert "same secret key" in plaintext

        session_b, token_b = get_or_create_demo_session(db, None)
        assert session_b.id != session_a.id
        assert token_b != token_a

        exams_b = get_exams_for_user(db, david, session_b.id)
        assert len(exams_b) == 1
        assert exams_b[0].id != exam_id_a

        # Session B cannot see Session A's exam.
        assert all(exam.id != exam_id_a for exam in exams_b)

        assert reset_demo_session(db, token_a) is True
        assert get_exams_for_user(db, david, session_b.id)
    finally:
        db.close()
