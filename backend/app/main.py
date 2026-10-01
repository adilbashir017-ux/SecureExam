import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.exams import router as exams_router
from app.api.submissions import router as submissions_router
from app.api.users import router as users_router


def get_allowed_origins():
    origins = os.getenv(
        "FRONTEND_URLS",
        (
            "http://localhost:5173,"
            "http://127.0.0.1:5173"
        ),
    )

    return [
        origin.strip().rstrip("/")
        for origin in origins.split(",")
        if origin.strip()
    ]


app = FastAPI(
    title="SecureExam API",
    description=(
        "Backend API for the Secure "
        "Encrypted Examination Portal"
    ),
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(exams_router)
app.include_router(submissions_router)


@app.get("/")
def root():
    return {
        "message": "SecureExam API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }