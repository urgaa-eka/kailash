# syntax=docker/dockerfile:1.7
# Build context must be the repo root:
#   docker build -f backend/services/company/Dockerfile .
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /srv

COPY backend/services/company/requirements.txt ./requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Shared platform library + service code + scaffold (schema/templates).
COPY backend/shared /srv/backend/shared
COPY backend/services/company/app /srv/backend/services/company/app
COPY company-segment /srv/company-segment
RUN touch /srv/backend/__init__.py /srv/backend/services/__init__.py \
          /srv/backend/services/company/__init__.py

ENV PYTHONPATH=/srv COMPANY_SCAFFOLD_DIR=/srv/company-segment
EXPOSE 8110
HEALTHCHECK --interval=30s --timeout=5s --retries=5 \
  CMD python -c "import urllib.request,sys;sys.exit(0 if urllib.request.urlopen('http://localhost:8110/health').status==200 else 1)"
CMD ["uvicorn", "backend.services.company.app.main:app", "--host", "0.0.0.0", "--port", "8110"]
