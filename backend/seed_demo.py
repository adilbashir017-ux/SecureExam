from app.core.database import SessionLocal
from app.services.demo_service import ensure_demo_prerequisites


def main():
    db = SessionLocal()
    try:
        ensure_demo_prerequisites(db)
        db.commit()
        print("Demo users and cryptographic keys are ready.")
        print("Public demo sandboxes are created automatically on first demo login.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
