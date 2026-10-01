import os

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.demo_config import DEMO_STUDENT_IDS
from app.crypto.falcon_module import falcon_verify
from app.models.demo_session import DemoSession
from app.models.demo_session_exam import DemoSessionExam
from app.models.exam import Exam
from app.models.exam_access import ExamAccess
from app.models.exam_crypto import ExamCrypto
from app.models.exam_key_package import ExamKeyPackage
from app.models.student_crypto_key import StudentCryptoKey
from app.models.system_signing_key import SystemSigningKey
from app.models.user import User
from app.schemas.exam import ExamCreate, ExamManagementResponse, ExamPublicResponse, ExamStatus
from app.schemas.user import UserRole
from app.services.crypto_service import open_exam_for_student, prepare_encrypted_exam
from app.services.user_service import get_user_by_id

SYSTEM_SIGNING_KEY_NAME = "main-system-key"


def _build_public_exam_response(exam: Exam) -> ExamPublicResponse:
    return ExamPublicResponse(
        id=exam.id,
        title=exam.title,
        course=exam.course,
        lecturer_id=exam.lecturer_id,
        duration_minutes=exam.duration_minutes,
        status=ExamStatus(exam.status),
    )


def _authorized_student_ids(db: Session, exam_id: int) -> list[int]:
    statement = (
        select(ExamAccess.student_id)
        .where(ExamAccess.exam_id == exam_id)
        .order_by(ExamAccess.student_id)
    )
    return list(db.scalars(statement).all())


def _build_management_exam_response(db: Session, exam: Exam) -> ExamManagementResponse:
    return ExamManagementResponse(
        **_build_public_exam_response(exam).model_dump(),
        authorized_student_ids=_authorized_student_ids(db, exam.id),
    )


def exam_is_in_scope(
    db: Session,
    exam_id: int,
    demo_session_id: int | None,
) -> bool:
    mapping = db.get(DemoSessionExam, exam_id)

    if demo_session_id is None:
        # Normal authenticated accounts can only see non-demo exams.
        return mapping is None

    return mapping is not None and mapping.demo_session_id == demo_session_id


def _scoped_exam_statement(demo_session_id: int | None):
    if demo_session_id is None:
        return (
            select(Exam)
            .outerjoin(DemoSessionExam, DemoSessionExam.exam_id == Exam.id)
            .where(DemoSessionExam.exam_id.is_(None))
        )

    return (
        select(Exam)
        .join(DemoSessionExam, DemoSessionExam.exam_id == Exam.id)
        .where(DemoSessionExam.demo_session_id == demo_session_id)
    )


def get_exams_for_user(
    db: Session,
    user: User,
    demo_session_id: int | None = None,
):
    statement = _scoped_exam_statement(demo_session_id)

    if user.role == UserRole.ADMIN.value:
        pass
    elif user.role == UserRole.LECTURER.value:
        statement = statement.where(Exam.lecturer_id == user.id)
    elif user.role == UserRole.STUDENT.value:
        statement = statement.where(Exam.status == ExamStatus.PUBLISHED.value)
    else:
        return []

    statement = statement.order_by(Exam.id.desc())
    return [_build_public_exam_response(exam) for exam in db.scalars(statement).all()]


def get_exam_for_user(
    db: Session,
    exam_id: int,
    user: User,
    demo_session_id: int | None = None,
):
    exam = db.get(Exam, exam_id)
    if exam is None or not exam_is_in_scope(db, exam_id, demo_session_id):
        return None

    if user.role == UserRole.ADMIN.value:
        return _build_public_exam_response(exam)
    if user.role == UserRole.LECTURER.value:
        return _build_public_exam_response(exam) if exam.lecturer_id == user.id else None
    if user.role == UserRole.STUDENT.value:
        return _build_public_exam_response(exam) if exam.status == ExamStatus.PUBLISHED.value else None
    return None


def get_exam_management(
    db: Session,
    exam_id: int,
    user: User,
    demo_session_id: int | None = None,
):
    exam = db.get(Exam, exam_id)
    if exam is None or not exam_is_in_scope(db, exam_id, demo_session_id):
        return None
    if user.role == UserRole.LECTURER.value and exam.lecturer_id != user.id:
        raise PermissionError("You can only manage exams that you created")
    if user.role not in {UserRole.LECTURER.value, UserRole.ADMIN.value}:
        raise PermissionError("You do not have permission to manage this exam")
    return _build_management_exam_response(db, exam)


def create_exam(
    exam_data: ExamCreate,
    db: Session,
    lecturer: User,
    demo_session_id: int | None = None,
    commit: bool = True,
):
    if demo_session_id is not None:
        if db.get(DemoSession, demo_session_id) is None:
            raise ValueError("Demo session not found")

        try:
            max_demo_exams = int(os.getenv("DEMO_MAX_EXAMS_PER_SESSION", "10"))
        except ValueError:
            max_demo_exams = 10
        max_demo_exams = max(1, min(max_demo_exams, 50))

        current_count = db.scalar(
            select(func.count())
            .select_from(DemoSessionExam)
            .where(DemoSessionExam.demo_session_id == demo_session_id)
        ) or 0
        if current_count >= max_demo_exams:
            raise ValueError(
                "Demo sandbox exam limit reached. Use 'Start fresh' to begin a new demo."
            )

    student_ids = list(dict.fromkeys(exam_data.authorized_student_ids))

    for student_id in student_ids:
        if demo_session_id is not None and student_id not in DEMO_STUDENT_IDS:
            raise ValueError("Demo exams can only authorize demo student accounts")

        student = get_user_by_id(db, student_id)
        if student is None:
            raise ValueError(f"Student {student_id} not found")
        if student.role != UserRole.STUDENT.value:
            raise ValueError(f"User {student_id} is not a student")

    exam = Exam(
        title=exam_data.title.strip(),
        course=exam_data.course.strip(),
        lecturer_id=lecturer.id,
        duration_minutes=exam_data.duration_minutes,
        status=ExamStatus.DRAFT.value,
    )
    db.add(exam)
    db.flush()

    if demo_session_id is not None:
        db.add(
            DemoSessionExam(
                exam_id=exam.id,
                demo_session_id=demo_session_id,
            )
        )

    for student_id in student_ids:
        db.add(ExamAccess(exam_id=exam.id, student_id=student_id))

    db.flush()

    if commit:
        db.commit()
        db.refresh(exam)

    return _build_management_exam_response(db, exam)


def is_student_authorized(
    exam_id: int,
    student_id: int,
    db: Session,
    demo_session_id: int | None = None,
):
    exam = db.get(Exam, exam_id)
    if exam is None or not exam_is_in_scope(db, exam_id, demo_session_id):
        raise ValueError("Exam not found")

    student = get_user_by_id(db, student_id)
    if student is None or student.role != UserRole.STUDENT.value:
        raise ValueError("Student not found")

    return db.get(ExamAccess, (exam_id, student_id)) is not None


def publish_exam(
    db: Session,
    exam_id: int,
    lecturer_id: int,
    exam_content: str,
    demo_session_id: int | None = None,
    commit: bool = True,
):
    exam = db.get(Exam, exam_id)
    if exam is None or not exam_is_in_scope(db, exam_id, demo_session_id):
        raise ValueError("Exam not found")
    if exam.lecturer_id != lecturer_id:
        raise PermissionError("You can only publish exams that you created")
    if db.get(ExamCrypto, exam_id) is not None:
        raise ValueError("Exam has already been encrypted and published")

    authorized_ids = _authorized_student_ids(db, exam_id)
    if not authorized_ids:
        raise ValueError("Exam must have at least one authorized student")

    public_keys: dict[int, bytes] = {}
    for student_id in authorized_ids:
        key = db.get(StudentCryptoKey, student_id)
        if key is None:
            raise ValueError(f"Student {student_id} has no cryptographic key pair")
        public_keys[student_id] = key.kyber_public_key

    signing_key = db.scalar(
        select(SystemSigningKey).where(SystemSigningKey.key_name == SYSTEM_SIGNING_KEY_NAME)
    )
    if signing_key is None:
        raise ValueError("System signing key was not found")

    try:
        prepared = prepare_encrypted_exam(
            exam_text=exam_content,
            authorized_student_public_keys=public_keys,
            falcon_private_key=signing_key.falcon_private_key,
        )
        db.add(
            ExamCrypto(
                exam_id=exam.id,
                encrypted_exam=prepared["encrypted_exam"],
                exam_iv=prepared["exam_iv"],
                exam_signature=prepared["signature"],
                falcon_public_key=signing_key.falcon_public_key,
                lecturer_exam_key=prepared["exam_key"],
            )
        )
        for student_id, package in prepared["protected_exam_keys"].items():
            db.add(
                ExamKeyPackage(
                    exam_id=exam.id,
                    student_id=student_id,
                    protected_exam_key=package,
                )
            )
        exam.status = ExamStatus.PUBLISHED.value
        db.flush()

        if commit:
            db.commit()
            db.refresh(exam)
    except Exception:
        db.rollback()
        raise

    return _build_management_exam_response(db, exam)


def attempt_exam(
    db: Session,
    exam_id: int,
    student: User,
    demo_session_id: int | None = None,
):
    exam = db.get(Exam, exam_id)
    if (
        exam is None
        or exam.status != ExamStatus.PUBLISHED.value
        or not exam_is_in_scope(db, exam_id, demo_session_id)
    ):
        raise ValueError("Exam not found")

    crypto = db.get(ExamCrypto, exam_id)
    if crypto is None:
        raise ValueError("Encrypted exam data was not found")

    student_key = db.get(StudentCryptoKey, student.id)
    if student_key is None:
        raise ValueError("Student cryptographic key pair was not found")

    package_record = db.get(ExamKeyPackage, (exam_id, student.id))
    package = package_record.protected_exam_key if package_record else None

    return open_exam_for_student(
        encrypted_exam=crypto.encrypted_exam,
        exam_iv=crypto.exam_iv,
        exam_signature=crypto.exam_signature,
        falcon_public_key=crypto.falcon_public_key,
        student_private_key=student_key.kyber_private_key,
        protected_exam_key=package,
    )


def run_security_demo(
    db: Session,
    exam_id: int,
    lecturer: User,
    demo_session_id: int | None = None,
):
    exam = db.get(Exam, exam_id)
    if exam is None or not exam_is_in_scope(db, exam_id, demo_session_id):
        raise ValueError("Exam not found")
    if exam.lecturer_id != lecturer.id:
        raise PermissionError("You can only test exams that you created")

    crypto = db.get(ExamCrypto, exam_id)
    if crypto is None:
        raise ValueError("Encrypted exam data was not found")

    original_valid = falcon_verify(
        crypto.encrypted_exam,
        crypto.exam_signature,
        crypto.falcon_public_key,
    )

    tampered = bytearray(crypto.encrypted_exam)
    if tampered:
        tampered[0] ^= 0x01
    else:
        tampered.extend(b"TAMPERED")

    tampered_valid = falcon_verify(
        bytes(tampered),
        crypto.exam_signature,
        crypto.falcon_public_key,
    )

    return original_valid, tampered_valid
