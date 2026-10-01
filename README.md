# SecureExam — Encrypted Examination Portal

<p align="center">
  <strong>
    Full-stack encrypted examination platform with a Python/FastAPI backend,
    React frontend, MySQL database, and educational cryptographic workflows.
  </strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=white" alt="React" />
  <img src="https://img.shields.io/badge/MySQL-4479A1?logo=mysql&logoColor=white" alt="MySQL" />
  <img src="https://img.shields.io/badge/JWT-Authentication-000000?logo=jsonwebtokens&logoColor=white" alt="JWT" />
</p>

---

## Overview

**SecureExam** is a full-stack web application for secure exam distribution and encrypted student submissions.

The platform combines normal application authentication with a separate cryptographic authorization layer.

A student may be allowed to see that an exam exists while still being unable to decrypt its questions without receiving the protected exam key.

SecureExam evolved from an original Python console-based cryptography course project into a complete full-stack web application.

> **Educational project:** the Kyber-style and Falcon-style modules are self-contained implementations designed to demonstrate public/private key concepts and digital signatures. They are not official production implementations of the corresponding standards.

---

## Key Features

- **Python/FastAPI backend**
- **React frontend**
- **MySQL persistence**
- **JWT authentication**
- **Role-based access control**
- **Lecturer exam creation and publishing**
- **Authorized-student decryption**
- **Unauthorized-student ciphertext-only access**
- **Serpent-style / OFB encryption**
- **Kyber-style public/private key delivery**
- **Falcon-style digital signatures**
- **Encrypted student submissions**
- **Fresh IV generation for each submitted answer**
- **Lecturer-controlled submission decryption**
- **Tampering detection**
- **One-click demo login**
- **Isolated public demo sandboxes**

---

## Tech Stack

| Layer | Technologies |
|---|---|
| Backend | Python, FastAPI, Pydantic |
| Frontend | React, Vite, React Router, CSS |
| Database | MySQL, SQLAlchemy, PyMySQL |
| Authentication | JWT, Argon2 |
| Cryptography | Serpent-style / OFB, Kyber-style, Falcon-style |
| Testing | Pytest, HTTPX, ESLint |
| Deployment Ready | Docker, Vercel configuration |

---

## Cryptographic Workflow

```text
Lecturer creates exam
        ↓
Generate symmetric exam key + IV
        ↓
Encrypt exam using Serpent-style / OFB
        ↓
Sign encrypted exam using Falcon-style signature
        ↓
Protect exam key for each authorized student
using the student's Kyber-style public key
        ↓
Student opens exam
        │
        ├── Signature invalid
        │       → Tampering detected
        │
        ├── No protected key package
        │       → Ciphertext only
        │
        └── Valid protected key package
                → Recover exam key
                → Decrypt exam
```

Student answers are encrypted before storage and use a **fresh IV for every submission**.

Plaintext answers are not persisted in the submissions table.

---

## Screenshots

### Login & Demo Roles

One-click access to Lecturer, Authorized Student, and Unauthorized Student demo roles.

![SecureExam Login](docs/screenshots/login-demo.png)

---

### Lecturer Dashboard

Lecturers can create and manage published examinations.

![Lecturer Dashboard](docs/screenshots/lecturer-dashboard.png)

---

### Authorized Student

The authorized student verifies the signature, recovers the exam key, and decrypts the examination.

![Authorized Student](docs/screenshots/authorized-student.png)

---

### Unauthorized Student

The unauthorized student can verify the exam signature but receives no protected exam key and therefore sees ciphertext only.

![Unauthorized Student](docs/screenshots/unauthorized-student.png)

---

### Encrypted Student Submission

Student answers are stored as ciphertext. The lecturer can decrypt a submission on demand.

![Submission Decryption](docs/screenshots/submission-decryption.png)

---

### Tampering Detection

The original encrypted exam passes signature verification, while a modified copy fails verification.

```text
Original signature: VALID
Tampered copy: INVALID
```

![Tampering Detection](docs/screenshots/tampering-detection.png)

---

## Public Demo Sandbox

SecureExam separates the current login identity from the browser's temporary demo environment.

```text
JWT                → Who is logged in?
Demo session token → Which sandbox belongs to this browser?
```

A single visitor can therefore test the complete flow:

```text
Lecturer
   ↓
Create and publish exam
   ↓ logout

Authorized Student
   ↓
Decrypt exam
   ↓
Submit encrypted answer
   ↓ logout

Unauthorized Student
   ↓
See ciphertext only
   ↓ logout

Lecturer
   ↓
View and decrypt submission
```

A different browser receives a different sandbox, preventing visitors from modifying each other's demo data.

---

## Project Structure

```text
SecureExam/
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
│
├── frontend/
│   ├── src/
│   ├── vercel.json
│   └── package.json
│
├── legacy_console/
│
├── docs/
│   └── screenshots/
│
└── README.md
```

---

## Security Notes

SecureExam is an educational security project demonstrating:

- symmetric encryption,
- public/private key concepts,
- digital signatures,
- cryptographic authorization,
- encrypted database storage,
- and tampering detection.

For a real production system, additional security measures would be required, including secure key-management infrastructure, encrypted private-key storage, secret rotation, monitoring, and further application hardening.

---

## Documentation

Additional documentation:

- [Public Demo Flow](PUBLIC_DEMO_FLOW.md)
- [Deployment Guide](DEPLOYMENT.md)

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