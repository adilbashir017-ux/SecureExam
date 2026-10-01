# SecureExam — Encrypted Examination Portal

<p align="center">
  <strong>
    Full-stack educational security platform for encrypted exam distribution,
    protected key delivery, signed exam content, and encrypted student submissions.
  </strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=white" alt="React" />
  <img src="https://img.shields.io/badge/MySQL-Database-4479A1?logo=mysql&logoColor=white" alt="MySQL" />
  <img src="https://img.shields.io/badge/JWT-Authentication-000000?logo=jsonwebtokens&logoColor=white" alt="JWT" />
</p>

---

## Overview

**SecureExam** is a full-stack encrypted examination portal with a **Python/FastAPI backend**, **React frontend**, and **MySQL database**.

The platform demonstrates how cryptographic concepts can be integrated into a complete examination workflow involving lecturers, authorized students, unauthorized students, encrypted submissions, authentication, role-based access, and tampering detection.

The system separates two important concepts:

- **Application authorization** — determines which user is logged in and what role they have.
- **Cryptographic authorization** — determines whether a student actually possesses the protected exam key required to decrypt an examination.

This means that a student may be allowed to see that an exam exists while still being unable to read its questions.

> **Educational project:** the Kyber-style and Falcon-style modules are self-contained course implementations designed to demonstrate public/private key concepts and digital signatures. They are **not production implementations of the official cryptographic standards**.

---

## Key Features

- **JWT-based authentication** for lecturers, students, and administrators.
- **Role-based access control** across the application.
- **Exam creation and publishing** through a lecturer dashboard.
- **Authorized-student management** for each examination.
- **Serpent-style / OFB symmetric encryption** for exam content and student answers.
- **Kyber-style public/private key delivery** of the symmetric exam key to authorized students only.
- **Falcon-style digital signatures** for exam authenticity and integrity verification.
- **Authorized-student workflow:** signature verification → exam-key recovery → exam decryption.
- **Unauthorized-student workflow:** exam metadata and ciphertext remain visible, but no protected exam key is provided.
- **Encrypted student submissions** with a fresh IV for every submitted answer.
- **Lecturer-controlled decryption** of encrypted submissions.
- **Tampering detection** through digital-signature verification.
- **MySQL persistence** for users, exams, cryptographic metadata, access control, and submissions.
- **Public demo sandbox architecture** that isolates different visitors from each other.
- **One-click demo login** for Lecturer, Authorized Student, and Unauthorized Student roles.

---

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

Student submissions use the same symmetric exam key but generate a **fresh IV for every answer**.

The plaintext student answer is not stored in the submissions table. It is returned only when the lecturer explicitly requests decryption.

---

## Public Demo Sandbox

The public-demo architecture separates the **current login identity** from the **browser demo workspace**.

```text
JWT                → Who is logged in now?
Demo session token → Which temporary sandbox belongs to this browser?
```

This allows one visitor to perform a complete workflow inside the same sandbox:

```text
Lecturer
   ↓
Create and publish an exam
   ↓ logout

Authorized Student
   ↓
Open and decrypt the same exam
   ↓
Submit encrypted answer
   ↓ logout

Unauthorized Student
   ↓
Open the same exam
   ↓
See ciphertext only
   ↓ logout

Lecturer
   ↓
View encrypted submission
   ↓
Decrypt submission
```

A different browser receives a different demo sandbox, preventing public visitors from modifying each other's demo data.

---

## Tech Stack

| Layer | Technologies |
|---|---|
| Backend | Python, FastAPI, Pydantic |
| Frontend | React, Vite, React Router, Lucide React, CSS |
| Database | MySQL, SQLAlchemy, PyMySQL |
| Authentication | JWT, Argon2 password hashing |
| Cryptography | Serpent-style / OFB, Kyber-style key delivery, Falcon-style signatures |
| Testing | Pytest, HTTPX, ESLint |
| Deployment | Docker, Vercel SPA configuration, environment variables |

---

## Project Structure

```text
SecureExam/
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI API routes
│   │   ├── core/             # Database, security, dependencies, demo configuration
│   │   ├── crypto/           # Educational cryptographic modules
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   └── services/         # Business logic
│   ├── tests/
│   ├── Dockerfile
│   ├── init_db.py
│   ├── seed_demo.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── context/
│   │   ├── layouts/
│   │   ├── pages/
│   │   ├── routes/
│   │   └── styles/
│   ├── vercel.json
│   └── package.json
│
├── legacy_console/           # Original console-based cryptography project
│
├── docs/
│   └── screenshots/
│       ├── login-demo.png
│       ├── lecturer-dashboard.png
│       ├── authorized-student.png
│       ├── unauthorized-student.png
│       ├── submission-decryption.png
│       └── tampering-detection.png
│
├── .gitignore
└── README.md
```

---

## Screenshots

### Login & Demo Roles

The login page provides standard authentication together with one-click demo access for the three main security scenarios.

![SecureExam Login and Demo Roles](docs/screenshots/login-demo.png)

---

### Lecturer Dashboard

Lecturers can manage published examinations, create new exams, and open individual exam-management pages.

![Lecturer Dashboard](docs/screenshots/lecturer-dashboard.png)

---

### Authorized vs Unauthorized Student

<table>
<tr>

<td width="50%" valign="top">

#### Authorized Student

The authorized student successfully:

- verifies the exam signature,
- recovers the protected exam key,
- decrypts the examination,
- views the original questions,
- and can submit an encrypted answer.

<img src="docs/screenshots/authorized-student.png" width="100%" alt="Authorized Student" />

</td>

<td width="50%" valign="top">

#### Unauthorized Student

The unauthorized student can verify that the encrypted exam is authentic, but receives no protected exam key.

The result is:

- Signature: **Verified**
- Exam key: **Unavailable**
- Decryption: **Unavailable**
- Exam content: **Ciphertext only**

<img src="docs/screenshots/unauthorized-student.png" width="100%" alt="Unauthorized Student" />

</td>

</tr>
</table>

---

### Encrypted Student Submission

Student answers are encrypted before being stored in the database.

The lecturer initially sees ciphertext and can explicitly decrypt a submission when needed.

![Encrypted Submission and Lecturer Decryption](docs/screenshots/submission-decryption.png)

---

### Tampering Detection

SecureExam demonstrates integrity protection through digital signatures.

The original encrypted exam passes verification, while a modified copy fails verification.

```text
Original signature: VALID
Tampered copy: INVALID
```

![Tampering Detection](docs/screenshots/tampering-detection.png)

---

## Database Design

The application stores users, examinations, cryptographic metadata, access permissions, protected exam keys, and encrypted submissions in MySQL.

Main tables include:

```text
users
exams
exam_access
student_crypto_keys
system_signing_keys
exam_crypto
exam_key_packages
submissions
demo_sessions
demo_session_exams
```

Exam questions are stored in encrypted form after publication.

Student submissions are also stored as encrypted ciphertext together with their IV.

---

## Main User Roles

### Lecturer

A lecturer can:

- create examinations,
- select authorized students,
- encrypt and publish examinations,
- view authorized-student information,
- inspect encrypted submissions,
- decrypt submissions on demand,
- run tampering-verification demonstrations.

### Authorized Student

An authorized student can:

- view published exams,
- verify the exam signature,
- recover the protected exam key,
- decrypt the exam,
- read the original questions,
- submit an encrypted answer.

### Unauthorized Student

An unauthorized student can:

- see published exam metadata,
- receive the encrypted examination,
- verify its signature,
- view ciphertext,

but cannot recover the symmetric exam key and therefore cannot decrypt the questions or submit a valid encrypted answer.

### Administrator

The administrator handles system-level management.

Authentication roles do not automatically provide cryptographic decryption privileges.

---

## Local Setup

### Prerequisites

Install:

- Python 3.12+
- Node.js / npm
- MySQL
- Git

---

### 1. Create the Database

Create a MySQL database:

```sql
CREATE DATABASE secureexam
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

---

### 2. Backend Setup

```powershell
cd backend

python -m venv .venv

.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt

Copy-Item .env.example .env
```

Update the generated `.env` file with your local MySQL credentials and JWT secret.

Then initialize and seed the database:

```powershell
python init_db.py
python seed_demo.py
```

Start FastAPI:

```powershell
uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger API documentation:

```text
http://127.0.0.1:8000/docs
```

Health endpoint:

```text
http://127.0.0.1:8000/health
```

---

### 3. Frontend Setup

Open a second terminal:

```powershell
cd frontend

npm install

Copy-Item .env.example .env

npm run dev
```

Open:

```text
http://localhost:5173
```

---

## Environment Variables

### Backend

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

### Frontend

```text
VITE_API_BASE_URL
```

Real `.env` files are excluded from Git.

Only `.env.example` files belong in the repository.

---

## Tests

### Backend

Run:

```powershell
cd backend
pytest
```

The backend test suite covers the core cryptographic workflow and public-demo sandbox behavior.

### Frontend

Run:

```powershell
cd frontend
npm run lint
```

Production build:

```powershell
npm run build
```

---

## API

FastAPI automatically exposes interactive API documentation through Swagger:

```text
http://127.0.0.1:8000/docs
```

Examples of supported operations include:

```text
Authentication
Exam creation
Exam publishing
Exam access verification
Exam decryption attempts
Encrypted answer submission
Submission listing
Lecturer-controlled decryption
Tampering verification
Public demo login
```

---

## Cryptographic Concepts Demonstrated

### Symmetric Encryption

SecureExam uses a symmetric exam key with a Serpent-style cipher operating through OFB mode.

The same key is used to encrypt and decrypt the exam and student answers.

---

### Public / Private Key Delivery

Each student has a Kyber-style public/private key pair.

```text
Student public key
      ↓
Protect exam key
      ↓
Authorized student receives protected package
      ↓
Student private key
      ↓
Recover symmetric exam key
```

Unauthorized students do not receive an exam-key package.

---

### Digital Signatures

The encrypted exam is signed using the Falcon-style signing private key.

Students verify the signature using the corresponding public key.

```text
Private key → Sign
Public key  → Verify
```

If the encrypted examination is modified, verification fails.

---

## Deployment

The repository is prepared for a deployment architecture such as:

```text
                Internet
                   │
                   ▼
          React Frontend
              Vercel
                   │
                HTTPS
                   │
                   ▼
          Python / FastAPI
            Backend Host
                   │
                   ▼
              Cloud MySQL
```

The project includes:

- Backend Dockerfile
- Environment-variable configuration
- Production database URL support
- Vercel SPA routing configuration
- CORS configuration
- Public demo sandbox architecture

### Live Demo

A public **Live Demo** URL will be added after deployment.

---

## Security Notes

This repository is an educational security project.

For the web version:

- exam and answer ciphertext may be visible,
- symmetric exam keys are protected separately,
- signature verification is independent from decryption authorization,
- unauthorized users may receive ciphertext without receiving the key,
- plaintext student answers are not persisted in the submissions table.

For production systems, further security measures would normally be required, including secure key-management infrastructure, encrypted private-key storage, secret rotation, monitoring, and additional application hardening.

---

## Original Course Version

The `legacy_console/` directory preserves the original console-based cryptography project.

The current SecureExam web platform extends that work into a complete full-stack system with:

- React user interfaces,
- Python/FastAPI REST APIs,
- MySQL persistence,
- JWT authentication,
- role-based access control,
- encrypted examination workflows,
- encrypted student submissions,
- digital-signature verification,
- tampering detection,
- and isolated public demo sessions.

---

## Future Improvements

Possible future extensions include:

- Cloud deployment and public Live Demo
- Automated demo-session cleanup jobs
- Docker Compose environment
- Lecturer analytics dashboard
- Exam scheduling and expiration
- Student submission history
- Key-management service integration
- CI/CD pipeline
- Additional automated frontend tests

---

## Author

**Adel Bashir**  
B.Sc. Software Engineering Student  
Braude College of Engineering

GitHub: [adilbashir017-ux](https://github.com/adilbashir017-ux)

---

<p align="center">
  <strong>SecureExam — Protect every exam from creation to submission.</strong>
</p>