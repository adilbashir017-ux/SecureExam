from app.core.database import Base, engine
from app.models import (  # noqa: F401
    DemoSession,
    DemoSessionExam,
    Exam,
    ExamAccess,
    ExamCrypto,
    ExamKeyPackage,
    StudentCryptoKey,
    Submission,
    SystemSigningKey,
    User,
)

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Database tables created successfully.")
