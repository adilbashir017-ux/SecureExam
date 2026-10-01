# Deployment checklist

## Backend + MySQL

Deploy the `backend` directory as a Docker service and provide a MySQL database.

Required production environment variables:

```text
DATABASE_URL=mysql+pymysql://USER:PASSWORD@HOST:PORT/DATABASE
JWT_SECRET_KEY=<long random secret, at least 32 bytes>
FRONTEND_URLS=https://YOUR-FRONTEND-DOMAIN
DEMO_SESSION_HOURS=12
DEMO_MAX_EXAMS_PER_SESSION=10
ALLOW_DEMO_PASSWORD_LOGIN=false
```

The Docker container runs:

```text
python init_db.py
python seed_demo.py
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Health endpoint:

```text
GET /health
```

## Frontend

Deploy the `frontend` directory to Vercel (or another static/Vite host).

Set:

```text
VITE_API_BASE_URL=https://YOUR-BACKEND-DOMAIN
```

Build command:

```text
npm run build
```

Output directory:

```text
dist
```

`vercel.json` already rewrites direct React Router URLs to `index.html`.

## Final verification

Use two different browsers (or a normal window + incognito) to confirm sandbox isolation:

```text
Browser A: Lecturer -> create exam -> Alice -> submit
Browser B: Lecturer -> should not see Browser A's created exam
Browser A: Lecturer -> should see/decrypt Alice's submission
Browser A: Eve -> same exam remains ciphertext-only unless Eve was explicitly authorized
```
