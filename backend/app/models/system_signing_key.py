from datetime import datetime

from sqlalchemy import DateTime, LargeBinary, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SystemSigningKey(Base):
    __tablename__ = "system_signing_keys"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    key_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    falcon_public_key: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    falcon_private_key: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
