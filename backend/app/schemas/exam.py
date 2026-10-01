from enum import Enum

from pydantic import BaseModel, Field


class ExamStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"


class ExamCreate(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    course: str = Field(min_length=1, max_length=150)
    authorized_student_ids: list[int] = Field(min_length=1, max_length=20)
    duration_minutes: int = Field(gt=0, le=720)


class ExamPublishRequest(BaseModel):
    exam_content: str = Field(min_length=1, max_length=50_000)


class ExamPublicResponse(BaseModel):
    id: int
    title: str
    course: str
    lecturer_id: int
    duration_minutes: int
    status: ExamStatus


class ExamManagementResponse(ExamPublicResponse):
    authorized_student_ids: list[int]


class ExamAccessResponse(BaseModel):
    exam_id: int
    student_id: int
    authorized: bool


class ExamAttemptResponse(BaseModel):
    exam_id: int
    signature_valid: bool
    key_available: bool
    decryption_successful: bool
    exam_content: str | None = None
    encrypted_content: str


class SecurityDemoResponse(BaseModel):
    exam_id: int
    original_signature_valid: bool
    tampered_signature_valid: bool
