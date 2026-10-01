# Upgrade from the previous SecureExam_Final

This version intentionally does **not** include real `.env` files.

To use your existing local MySQL database without losing the exams you already created:

1. Copy your previous `backend/.env` into this version's `backend/.env`.
2. Copy your previous `frontend/.env` into this version's `frontend/.env`.
3. From `backend`, run:

```powershell
python init_db.py
python seed_demo.py
```

`init_db.py` uses SQLAlchemy `create_all`, so it keeps the existing SecureExam tables/data and adds the two new public-demo tables if they do not exist:

```text
demo_sessions
demo_session_exams
```

No existing exam needs to be converted. Existing exams remain non-demo/global records. One-click demo logins create new isolated sandbox exams and cannot see those old global exams.

For the public website, keep:

```text
ALLOW_DEMO_PASSWORD_LOGIN=false
```

If you deliberately want to use the old seeded email/password accounts during local development, set:

```text
ALLOW_DEMO_PASSWORD_LOGIN=true
```

The one-click Lecturer / Authorized Student / Unauthorized Student buttons work regardless of that setting.
