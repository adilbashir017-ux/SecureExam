FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# create_all + seed_demo are idempotent and make a fresh cloud database ready
# before the API starts. Public demo sandboxes are then created on demand.
CMD ["sh", "-c", "python init_db.py && python seed_demo.py && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
