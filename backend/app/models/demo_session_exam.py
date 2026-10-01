from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class DemoSessionExam(Base):
    __tablename__ = "demo_session_exams"

    # One exam belongs to at most one demo sandbox.
    exam_id: Mapped[int] = mapped_column(
        ForeignKey("exams.id", ondelete="CASCADE"),
        primary_key=True,
    )
    demo_session_id: Mapped[int] = mapped_column(
        ForeignKey("demo_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
