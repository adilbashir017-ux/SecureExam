from datetime import datetime

from pydantic import BaseModel, Field


class SubmissionCreate(BaseModel):
    answer_text: str = Field(min_length=1, max_length=50_000)


class SubmissionResponse(BaseModel):
    id: int
    exam_id: int
    student_id: int
    encrypted_answer_hex: str
    submitted_at: datetime


class LecturerSubmissionResponse(SubmissionResponse):
    pass


class DecryptedSubmissionResponse(BaseModel):
    submission_id: int
    exam_id: int
    student_id: int
    decrypted_answer: str
