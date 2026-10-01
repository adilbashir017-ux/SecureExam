import os

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


load_dotenv()


def build_database_url():
    """
    Production:
        Prefer DATABASE_URL when provided by a cloud database.

    Local development:
        Fall back to the individual DB_* variables.
    """

    database_url = os.getenv("DATABASE_URL")

    if database_url:
        # Some providers return mysql://...
        # SQLAlchemy + PyMySQL expects mysql+pymysql://...
        if database_url.startswith("mysql://"):
            database_url = database_url.replace(
                "mysql://",
                "mysql+pymysql://",
                1,
            )

        return database_url

    return URL.create(
        drivername="mysql+pymysql",
        username=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(
            os.getenv(
                "DB_PORT",
                "3306",
            )
        ),
        database=os.getenv(
            "DB_NAME",
            "secureexam",
        ),
    )


DATABASE_URL = build_database_url()


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=280,
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()