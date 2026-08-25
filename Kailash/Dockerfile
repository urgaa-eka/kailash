FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/backend/requirements.txt
# emergentintegrations is a private package (not on public PyPI), so a plain
# `pip install -r requirements.txt` fails outright. Install the rest, then the
# package itself best-effort from the Emergent index.
#
# `|| true` keeps a transient index outage from failing the build, but it does
# NOT make the package optional: app/guardians/ganesha.py imports it at module
# level with no guard, so `import app.main` raises ModuleNotFoundError without
# it. If that index ever goes dark, this image builds and then fails to start.
RUN grep -vi "^emergentintegrations" /app/backend/requirements.txt > /tmp/requirements.txt \
    && pip install --no-cache-dir -r /tmp/requirements.txt
RUN pip install --no-cache-dir emergentintegrations==0.1.0 \
      --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/ || true

COPY backend/ /app/backend/
COPY database/ /app/database/

# The app logs to /var/log/kailash (see app/middleware/error_handler.py);
# create it before dropping privileges or startup dies on PermissionError.
RUN useradd -m appuser \
    && mkdir -p /var/log/kailash \
    && chown -R appuser:appuser /app /var/log/kailash
USER appuser

EXPOSE 8000

# Run from backend/ as `app.main:app` — matching backend/server.py. Twenty
# modules use absolute `from app.…` imports, which only resolve with
# backend/ on sys.path; `backend.app.main:app` raises ModuleNotFoundError.
WORKDIR /app/backend
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
