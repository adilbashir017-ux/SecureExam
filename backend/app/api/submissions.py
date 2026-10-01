from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import AuthContext, require_roles
from app.schemas.submission import (
    DecryptedSubmissionResponse,
    LecturerSubmissionResponse,
    SubmissionCreate,
    SubmissionResponse,
)
from app.services.submission_service import (
    decrypt_submission_for_lecturer,
    get_exam_submissions_for_lecturer,
    submit_exam_answer,
)

router = APIRouter(prefix="/exams", tags=["Submissions"])


@router.post("/{exam_id}/submit", response_model=SubmissionResponse, status_code=201)
def submit_exam(
    exam_id: int,
    submission_data: SubmissionCreate,
    db: Session = Depends(get_db),
    identity: AuthContext = Depends(require_roles("student")),
):
    try:
        submission = submit_exam_answer(
            db,
            exam_id,
            identity.user,
            submission_data.answer_text,
            identity.demo_session_id,
        )
        return SubmissionResponse(
            id=submission.id,
            exam_id=submission.exam_id,
            student_id=submission.student_id,
            encrypted_answer_hex=submission.encrypted_answer.hex(),
            submitted_at=submission.submitted_at,
        )
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error))
    except RuntimeError as error:
        raise HTTPException(status_code=409, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.get("/{exam_id}/submissions", response_model=list[LecturerSubmissionResponse])
def get_exam_submissions(
    exam_id: int,
    db: Session = Depends(get_db),
    identity: AuthContext = Depends(require_roles("lecturer")),
):
    try:
        submissions = get_exam_submissions_for_lecturer(
            db,
            exam_id,
            identity.user,
            identity.demo_session_id,
        )
        return [
            LecturerSubmissionResponse(
                id=item.id,
                exam_id=item.exam_id,
                student_id=item.student_id,
                encrypted_answer_hex=item.encrypted_answer.hex(),
                submitted_at=item.submitted_at,
            )
            for item in submissions
        ]
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.post(
    "/{exam_id}/submissions/{submission_id}/decrypt",
    response_model=DecryptedSubmissionResponse,
)
def decrypt_exam_submission(
    exam_id: int,
    submission_id: int,
    db: Session = Depends(get_db),
    identity: AuthContext = Depends(require_roles("lecturer")),
):
    try:
        submission, plaintext = decrypt_submission_for_lecturer(
            db,
            exam_id,
            submission_id,
            identity.user,
            identity.demo_session_id,
        )
        return DecryptedSubmissionResponse(
            submission_id=submission.id,
            exam_id=submission.exam_id,
            student_id=submission.student_id,
            decrypted_answer=plaintext,
        )
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
