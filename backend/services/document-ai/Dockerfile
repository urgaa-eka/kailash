# syntax=docker/dockerfile:1.7
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

# Install shared platform library (build context must be repo root).
COPY platform /opt/platform
RUN pip install --upgrade pip && pip install /opt/platform

# Install service deps.
COPY services/document-ai/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY services/document-ai/app ./app

EXPOSE 8101
HEALTHCHECK --interval=30s --timeout=5s --retries=5 \
  CMD python -c "import urllib.request,sys;sys.exit(0 if urllib.request.urlopen('http://localhost:8101/health').status==200 else 1)"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8101"]
