from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exam import Exam
from app.models.exam_crypto import ExamCrypto
from app.models.exam_key_package import ExamKeyPackage
from app.models.student_crypto_key import StudentCryptoKey
from app.models.submission import Submission
from app.models.user import User
from app.schemas.exam import ExamStatus
from app.services.crypto_service import decrypt_student_submission, encrypt_student_submission
from app.services.exam_service import exam_is_in_scope


def submit_exam_answer(
    db: Session,
    exam_id: int,
    student: User,
    answer_text: str,
    demo_session_id: int | None = None,
):
    exam = db.get(Exam, exam_id)
    if (
        exam is None
        or exam.status != ExamStatus.PUBLISHED.value
        or not exam_is_in_scope(db, exam_id, demo_session_id)
    ):
        raise ValueError("Exam not found")

    existing = db.scalar(
        select(Submission).where(
            Submission.exam_id == exam_id,
            Submission.student_id == student.id,
        )
    )
    if existing is not None:
        raise RuntimeError("You have already submitted this exam")

    crypto = db.get(ExamCrypto, exam_id)
    if crypto is None:
        raise ValueError("Encrypted exam data was not found")

    student_key = db.get(StudentCryptoKey, student.id)
    if student_key is None:
        raise ValueError("Student cryptographic key pair was not found")

    package_record = db.get(ExamKeyPackage, (exam_id, student.id))
    package = package_record.protected_exam_key if package_record else None

    encrypted = encrypt_student_submission(
        student_id=student.id,
        answer_text=answer_text,
        encrypted_exam=crypto.encrypted_exam,
        exam_signature=crypto.exam_signature,
        falcon_public_key=crypto.falcon_public_key,
        student_private_key=student_key.kyber_private_key,
        protected_exam_key=package,
    )

    submission = Submission(
        exam_id=exam_id,
        student_id=student.id,
        encrypted_answer=encrypted["encrypted_answer"],
        answer_iv=encrypted["answer_iv"],
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


def get_exam_submissions_for_lecturer(
    db: Session,
    exam_id: int,
    lecturer: User,
    demo_session_id: int | None = None,
):
    exam = db.get(Exam, exam_id)
    if exam is None or not exam_is_in_scope(db, exam_id, demo_session_id):
        raise ValueError("Exam not found")
    if exam.lecturer_id != lecturer.id:
        raise PermissionError("You can only view submissions for exams that you created")

    return db.scalars(
        select(Submission)
        .where(Submission.exam_id == exam_id)
        .order_by(Submission.submitted_at)
    ).all()


def decrypt_submission_for_lecturer(
    db: Session,
    exam_id: int,
    submission_id: int,
    lecturer: User,
    demo_session_id: int | None = None,
):
    exam = db.get(Exam, exam_id)
    if exam is None or not exam_is_in_scope(db, exam_id, demo_session_id):
        raise ValueError("Exam not found")
    if exam.lecturer_id != lecturer.id:
        raise PermissionError("You can only decrypt submissions for exams that you created")

    submission = db.get(Submission, submission_id)
    if submission is None or submission.exam_id != exam_id:
        raise ValueError("Submission not found")

    crypto = db.get(ExamCrypto, exam_id)
    if crypto is None:
        raise ValueError("Encrypted exam data was not found")

    plaintext = decrypt_student_submission(
        encrypted_answer=submission.encrypted_answer,
        answer_iv=submission.answer_iv,
        lecturer_exam_key=crypto.lecturer_exam_key,
    )
    return submission, plaintext
