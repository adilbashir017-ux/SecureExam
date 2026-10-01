from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import AuthContext, get_current_identity, require_roles
from app.schemas.exam import (
    ExamAccessResponse,
    ExamAttemptResponse,
    ExamCreate,
    ExamManagementResponse,
    ExamPublicResponse,
    ExamPublishRequest,
    SecurityDemoResponse,
)
from app.services.exam_service import (
    attempt_exam,
    create_exam,
    get_exam_for_user,
    get_exam_management,
    get_exams_for_user,
    is_student_authorized,
    publish_exam,
    run_security_demo,
)

router = APIRouter(prefix="/exams", tags=["Exams"])


@router.get("/", response_model=list[ExamPublicResponse])
def read_exams(
    db: Session = Depends(get_db),
    identity: AuthContext = Depends(get_current_identity),
):
    return get_exams_for_user(db, identity.user, identity.demo_session_id)


@router.post("/", response_model=ExamManagementResponse, status_code=201)
def add_exam(
    exam_data: ExamCreate,
    db: Session = Depends(get_db),
    identity: AuthContext = Depends(require_roles("lecturer")),
):
    try:
        return create_exam(
            exam_data,
            db,
            identity.user,
            demo_session_id=identity.demo_session_id,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.get("/{exam_id}", response_model=ExamPublicResponse)
def read_exam(
    exam_id: int,
    db: Session = Depends(get_db),
    identity: AuthContext = Depends(get_current_identity),
):
    exam = get_exam_for_user(db, exam_id, identity.user, identity.demo_session_id)
    if exam is None:
        raise HTTPException(status_code=404, detail="Exam not found")
    return exam


@router.get("/{exam_id}/management", response_model=ExamManagementResponse)
def read_exam_management(
    exam_id: int,
    db: Session = Depends(get_db),
    identity: AuthContext = Depends(require_roles("lecturer", "admin")),
):
    try:
        exam = get_exam_management(
            db,
            exam_id,
            identity.user,
            identity.demo_session_id,
        )
        if exam is None:
            raise HTTPException(status_code=404, detail="Exam not found")
        return exam
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error))


@router.get("/{exam_id}/my-access", response_model=ExamAccessResponse)
def check_my_exam_access(
    exam_id: int,
    db: Session = Depends(get_db),
    identity: AuthContext = Depends(require_roles("student")),
):
    exam = get_exam_for_user(db, exam_id, identity.user, identity.demo_session_id)
    if exam is None:
        raise HTTPException(status_code=404, detail="Exam not found")
    authorized = is_student_authorized(
        exam_id,
        identity.user.id,
        db,
        identity.demo_session_id,
    )
    return ExamAccessResponse(
        exam_id=exam_id,
        student_id=identity.user.id,
        authorized=authorized,
    )


@router.post("/{exam_id}/attempt", response_model=ExamAttemptResponse)
def attempt_exam_endpoint(
    exam_id: int,
    db: Session = Depends(get_db),
    identity: AuthContext = Depends(require_roles("student")),
):
    try:
        result = attempt_exam(
            db,
            exam_id,
            identity.user,
            identity.demo_session_id,
        )
        return ExamAttemptResponse(exam_id=exam_id, **result)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.post("/{exam_id}/publish", response_model=ExamManagementResponse)
def publish_exam_endpoint(
    exam_id: int,
    publish_data: ExamPublishRequest,
    db: Session = Depends(get_db),
    identity: AuthContext = Depends(require_roles("lecturer")),
):
    try:
        return publish_exam(
            db=db,
            exam_id=exam_id,
            lecturer_id=identity.user.id,
            exam_content=publish_data.exam_content,
            demo_session_id=identity.demo_session_id,
        )
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.get("/{exam_id}/security-demo", response_model=SecurityDemoResponse)
def security_demo(
    exam_id: int,
    db: Session = Depends(get_db),
    identity: AuthContext = Depends(require_roles("lecturer")),
):
    try:
        original_valid, tampered_valid = run_security_demo(
            db,
            exam_id,
            identity.user,
            identity.demo_session_id,
        )
        return SecurityDemoResponse(
            exam_id=exam_id,
            original_signature_valid=original_valid,
            tampered_signature_valid=tampered_valid,
        )
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
