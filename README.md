# SecureExam — Encrypted Examination Portal

SecureExam is a full-stack educational security project built with **React, FastAPI and MySQL**. It demonstrates encrypted exam distribution, per-student key delivery, digital signatures, encrypted submissions, role-based access and an isolated public demo workflow.

## Main security flow

- **Serpent-style + OFB** encrypts exam questions and student answers.
- **Kyber-style public/private keys** protect the symmetric exam key separately for each authorized student.
- **Falcon-style digital signatures** sign the encrypted exam and detect tampering before decryption.
- Every student can see published exam metadata.
- Authorized students receive a protected exam-key package and can decrypt the questions.
- Unauthorized students receive the encrypted exam but no exam-key package, so they only see ciphertext.
- Student answers are encrypted with a fresh IV before storage.
- The lecturer sees encrypted submissions first and explicitly decrypts them.
- Plaintext exam questions and plaintext submissions are not persisted in MySQL.

> The Kyber-style and Falcon-style modules are self-contained educational course implementations. They are not production implementations of the official cryptographic standards.

## Public Demo Sandbox

The one-click demo buttons do **not** expose passwords in the browser.

On the first demo login, the backend creates a temporary private sandbox and returns a random `demo_session_token`. The browser keeps that token separately from the JWT.

- JWT = which role is currently logged in.
- Demo session token = which private demo workspace this browser belongs to.

This allows a visitor to:

1. Enter as **Lecturer**, create and publish an exam.
2. Log out / switch role.
3. Enter as **Authorized Student** and see the same exam decrypted.
4. Submit an encrypted answer.
5. Switch to **Unauthorized Student** and see the same exam as ciphertext only.
6. Switch back to **Lecturer** and decrypt the student's submission.

Different browsers receive different sandboxes, so visitors do not overwrite each other's demo data. A sandbox expires after `DEMO_SESSION_HOURS` (12 hours by default). Expired sandboxes are cleaned automatically during future demo logins. The login page also provides **Start fresh** to discard the current browser sandbox.

## Project structure

```text
SecureExam_Final_Public_Demo/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── crypto/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   ├── tests/
│   ├── Dockerfile
│   ├── init_db.py
│   ├── seed_demo.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── vercel.json
│   └── package.json
├── legacy_console/
└── README.md
```

## Local setup

Create a MySQL database:

```sql
CREATE DATABASE secureexam CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Backend (Windows PowerShell):

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python init_db.py
python seed_demo.py
uvicorn app.main:app --reload
```

Frontend:

```powershell
cd frontend
npm install
copy .env.example .env
npm run dev
```

Open:

```text
Frontend: http://localhost:5173
API:      http://127.0.0.1:8000
Swagger:  http://127.0.0.1:8000/docs
```

## Environment variables

Backend local development uses the individual MySQL variables:

```text
DB_HOST
DB_PORT
DB_NAME
DB_USER
DB_PASSWORD
```

Cloud deployments can use one connection string instead:

```text
DATABASE_URL=mysql+pymysql://USER:PASSWORD@HOST:PORT/DATABASE
```

Other important backend variables:

```text
JWT_SECRET_KEY
JWT_ALGORITHM
JWT_EXPIRE_MINUTES
FRONTEND_URLS
DEMO_SESSION_HOURS
DEMO_MAX_EXAMS_PER_SESSION
ALLOW_DEMO_PASSWORD_LOGIN
```

Frontend:

```text
VITE_API_BASE_URL
```

Never commit the real `.env` files. Only `.env.example` belongs in Git.

## Public deployment layout

Recommended architecture:

```text
Visitor
  ↓
React / Vercel
  ↓ HTTPS
FastAPI / container host
  ↓
Cloud MySQL
```

For the frontend, set:

```text
VITE_API_BASE_URL=https://YOUR-BACKEND-DOMAIN
```

For the backend, set at minimum:

```text
DATABASE_URL=...
JWT_SECRET_KEY=...
FRONTEND_URLS=https://YOUR-FRONTEND-DOMAIN
DEMO_SESSION_HOURS=12
```

The backend Dockerfile automatically runs `init_db.py` and `seed_demo.py` before starting Uvicorn, so a new cloud database receives the required tables, demo identities and educational cryptographic key pairs.

`frontend/vercel.json` contains the SPA rewrite needed for direct React Router URLs and browser refreshes.

## Demo identities

The public UI offers one-click roles:

- Lecturer — David
- Authorized Student — Alice
- Unauthorized Student — Eve

Bob is also available as an authorized demo student when the lecturer chooses authorized students for a newly created exam.

Optional manual demo passwords can be configured in `backend/.env` for local testing. Public deployments should keep `ALLOW_DEMO_PASSWORD_LOGIN=false`; one-click demo login does not send demo passwords to the frontend.

## Tests

Backend crypto workflow:

```powershell
cd backend
pytest
```

Frontend validation:

```powershell
cd frontend
npm run lint
npm run build
```
