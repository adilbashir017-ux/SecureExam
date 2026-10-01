from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, LargeBinary, func
from sqlalchemy.dialects.mysql import MEDIUMBLOB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


BLOB_TYPE = LargeBinary().with_variant(MEDIUMBLOB(), "mysql")


class ExamCrypto(Base):
    __tablename__ = "exam_crypto"

    exam_id: Mapped[int] = mapped_column(
        ForeignKey("exams.id", ondelete="CASCADE"),
        primary_key=True,
    )
    encrypted_exam: Mapped[bytes] = mapped_column(BLOB_TYPE, nullable=False)
    exam_iv: Mapped[bytes] = mapped_column(LargeBinary(16), nullable=False)
    exam_signature: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    falcon_public_key: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    lecturer_exam_key: Mapped[bytes] = mapped_column(LargeBinary(16), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
