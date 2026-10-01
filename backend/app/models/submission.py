from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, LargeBinary, UniqueConstraint, func
from sqlalchemy.dialects.mysql import MEDIUMBLOB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


BLOB_TYPE = LargeBinary().with_variant(MEDIUMBLOB(), "mysql")


class Submission(Base):
    __tablename__ = "submissions"
    __table_args__ = (
        UniqueConstraint("exam_id", "student_id", name="uq_submission_exam_student"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    exam_id: Mapped[int] = mapped_column(
        ForeignKey("exams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    student_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    encrypted_answer: Mapped[bytes] = mapped_column(BLOB_TYPE, nullable=False)
    answer_iv: Mapped[bytes] = mapped_column(LargeBinary(16), nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
