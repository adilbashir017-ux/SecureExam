from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, LargeBinary, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class StudentCryptoKey(Base):
    __tablename__ = "student_crypto_keys"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    kyber_public_key: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    kyber_private_key: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
