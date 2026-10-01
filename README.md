# SecureExam — Encrypted Examination Portal

<p align="center">
  <strong>Full-stack educational security platform for encrypted exam distribution, protected key delivery, signed exam content, and encrypted student submissions.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=white" alt="React" />
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/MySQL-Database-4479A1?logo=mysql&logoColor=white" alt="MySQL" />
  <img src="https://img.shields.io/badge/JWT-Authentication-000000?logo=jsonwebtokens&logoColor=white" alt="JWT" />
</p>

## Overview

**SecureExam** is a full-stack examination portal built with **React, FastAPI, Python, SQLAlchemy, and MySQL**. The project demonstrates how cryptographic concepts can be integrated into a complete web workflow involving lecturers, authorized students, unauthorized students, encrypted submissions, role-based access, and tampering detection.

The system combines application-level authentication with a separate cryptographic authorization layer: a student may be allowed to see that an exam exists while still being unable to decrypt its content without the protected exam key.

> **Educational project:** the Kyber-style and Falcon-style modules are self-contained course implementations designed to demonstrate public/private key concepts and digital signatures. They are **not production implementations of the official cryptographic standards**.

## Key Features

- **Role-based authentication** for lecturers, students, and administrators using JWT.
- **Exam creation and publishing** through a React lecturer dashboard.
- **Serpent-style / OFB encryption** for exam content and student answers.
- **Kyber-style public/private key delivery** of the symmetric exam key to authorized students only.
- **Falcon-style digital signatures** to verify exam authenticity and integrity before decryption.
- **Authorized-student workflow:** verified signature → exam-key recovery → decrypted questions.
- **Unauthorized-student workflow:** published exam metadata and ciphertext are visible, but no exam key is provided.
- **Encrypted submissions:** answers are encrypted with a fresh IV before being stored in MySQL.
- **Lecturer-controlled decryption:** lecturers initially see ciphertext and explicitly decrypt a submission when required.
- **Tampering demonstration:** modifying encrypted exam content causes signature verification to fail.
- **Isolated public demo sandboxes:** different visitors can test the same demo roles without modifying each other's data.

## Security Workflow

```text
Lecturer creates exam
        │
        ▼
Generate symmetric exam key + IV
        │
        ▼
Serpent-style / OFB encryption
        │
        ├──────────────► Encrypted exam stored in MySQL
        │
        ▼
Falcon-style signature
        │
        ▼
For each authorized student
        │
        ▼
Protect exam key using that student's
Kyber-style public key
        │
        ▼
Student opens exam
        │
        ├─ Signature invalid ─────► Reject / tampering detected
        │
        ├─ No key package ────────► Ciphertext only
        │
        └─ Valid key package ─────► Recover key → decrypt exam
```

Student submissions follow the same symmetric exam key but use a **fresh IV for every answer**. Plaintext answers are returned only when explicitly decrypted and are not persisted in the submissions table.

## Public Demo Sandbox

The public-demo architecture separates the **login identity** from the **browser demo workspace**.

```text
JWT                → Who is logged in now?
Demo session token → Which temporary sandbox belongs to this browser?
```

A visitor can therefore:

```text
Lecturer → create and publish an exam
   ↓ logout
Authorized Student → open the same exam and submit an encrypted answer
   ↓ logout
Unauthorized Student → see the same exam as ciphertext only
   ↓ logout
Lecturer → inspect and decrypt the encrypted submission
```

A different browser receives a different sandbox, preventing public visitors from overwriting each other's demo data.

## Tech Stack

| Layer | Technologies |
|---|---|
| Frontend | React, Vite, React Router, Lucide React, CSS |
| Backend | FastAPI, Python, Pydantic |
| Database | MySQL, SQLAlchemy, PyMySQL |
| Authentication | JWT, Argon2 password hashing |
| Cryptography | Serpent-style/OFB, Kyber-style key delivery, Falcon-style signatures |
| Testing | Pytest, HTTPX, ESLint |
| Deployment-ready | Docker, Vercel SPA configuration, environment variables |

## Project Structure

```text
SecureExam/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routes
│   │   ├── core/         # DB, security, dependencies, demo configuration
│   │   ├── crypto/       # Educational crypto modules
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── services/     # Business logic
│   ├── tests/
│   ├── Dockerfile
│   ├── init_db.py
│   ├── seed_demo.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── context/
│   │   ├── layouts/
│   │   ├── pages/
│   │   └── routes/
│   ├── vercel.json
│   └── package.json
├── legacy_console/       # Original console-based course project
├── docs/
└── README.md
```

## Screenshots

> Add screenshots to `docs/screenshots/` and replace the placeholders below.

### Login & Demo Roles

```text
One-click roles: Lecturer · Authorized Student · Unauthorized Student
```

### Lecturer Dashboard

```text
Create exams · Encrypt & publish · Manage authorized students
```

### Authorized vs Unauthorized Student

```text
Authorized student   → Signature ✓ Key ✓ Decryption ✓
Unauthorized student → Signature ✓ Key unavailable · Ciphertext only
```

### Encrypted Submission & Tampering Detection

```text
Encrypted answer → Lecturer decrypts on demand
Original signature: VALID
Tampered copy: INVALID
```

## Local Setup

### 1. Database

Create a MySQL database:

```sql
CREATE DATABASE secureexam
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

### 2. Backend

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

Backend endpoints:

```text
API:     http://127.0.0.1:8000
Swagger: http://127.0.0.1:8000/docs
Health:  http://127.0.0.1:8000/health
```

### 3. Frontend

```powershell
cd frontend
npm install
copy .env.example .env
npm run dev
```

Open:

```text
http://localhost:5173
```

## Environment Variables

Backend:

```text
DB_HOST
DB_PORT
DB_NAME
DB_USER
DB_PASSWORD
DATABASE_URL
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

Real `.env` files are excluded from Git. Only `.env.example` files belong in the repository.

## Tests

Backend:

```powershell
cd backend
pytest
```

Frontend:

```powershell
cd frontend
npm run lint
npm run build
```

## Deployment

The repository is prepared for a deployment architecture such as:

```text
React / Vercel
      ↓ HTTPS
FastAPI / container host
      ↓
Cloud MySQL
```

A public **Live Demo** link will be added after deployment.

## Original Course Version

The `legacy_console/` directory preserves the original console-based cryptography project. The current web platform extends that work into a full-stack application with authentication, database persistence, role-specific interfaces, encrypted submissions, and isolated public demo sessions.

## Author

**Adel Bashir**  
B.Sc. Software Engineering student — Braude College of Engineering

GitHub: [adilbashir017-ux](https://github.com/adilbashir017-ux)
