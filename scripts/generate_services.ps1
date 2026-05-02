# Generator for KAILASH-AI service skeletons.
# Each service gets:
#   app/main.py, app/settings.py, app/routes.py, app/service.py, app/__init__.py
#   tests/test_health.py, tests/test_routes.py, tests/__init__.py
#   requirements.txt, Dockerfile, README.md, .env.example, pytest.ini
param([string]$Root = "$env:TEMP\kailash-work\target-repo")

$services = @(
  @{ id="document-ai";     title="Document AI";     port=8101; deps=@("httpx>=0.27","pypdf>=4.2","pillow>=10.0") },
  @{ id="forecasting";     title="Forecasting";     port=8102; deps=@("numpy>=1.26") },
  @{ id="anomaly";         title="Anomaly Detection"; port=8103; deps=@("numpy>=1.26","scikit-learn>=1.4") },
  @{ id="rag";             title="RAG & Embeddings"; port=8104; deps=@("httpx>=0.27","numpy>=1.26") },
  @{ id="vision-gateway";  title="Vision LLM Gateway"; port=8105; deps=@("httpx>=0.27") },
  @{ id="speech";          title="Speech";           port=8106; deps=@("httpx>=0.27") },
  @{ id="model-registry";  title="Model Registry";   port=8107; deps=@() },
  @{ id="knowledge-graph"; title="Knowledge Graph";  port=8108; deps=@() },
  @{ id="automobile-llm";  title="Automobile LLM";   port=8109; deps=@("httpx>=0.27") }
)

foreach ($svc in $services) {
  $dir = Join-Path $Root "services\$($svc.id)"
  Remove-Item -Recurse -Force $dir -ErrorAction SilentlyContinue
  New-Item -ItemType Directory -Force -Path $dir,"$dir\app","$dir\tests" | Out-Null

  $envUpper = ($svc.id -replace '-','_').ToUpper()

  # requirements.txt — service-specific deps. kailash_shared installed separately in Docker.
  $reqs = @(
    "fastapi>=0.110",
    "uvicorn[standard]>=0.29",
    "pydantic>=2.6",
    "pydantic-settings>=2.2"
  ) + $svc.deps
  Set-Content -Path "$dir\requirements.txt" -Value ($reqs -join "`n") -Encoding UTF8

  # __init__
  Set-Content -Path "$dir\app\__init__.py" -Value "" -Encoding UTF8
  Set-Content -Path "$dir\tests\__init__.py" -Value "" -Encoding UTF8

  # settings.py
  $settings = @"
from kailash_shared import BaseServiceSettings


class Settings(BaseServiceSettings):
    service_name: str = "$($svc.id)"
    version: str = "0.1.0"


settings = Settings()
"@
  Set-Content -Path "$dir\app\settings.py" -Value $settings -Encoding UTF8

  # main.py uses build_app + routes.register
  $main = @"
from kailash_shared import build_app

from .routes import register
from .settings import settings

app = build_app(settings, routers=[register])
"@
  Set-Content -Path "$dir\app\main.py" -Value $main -Encoding UTF8

  # Dockerfile (expects build context = repo root)
  $dockerfile = @"
# syntax=docker/dockerfile:1.7
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

# Install shared platform library (build context must be repo root).
COPY platform /opt/platform
RUN pip install --upgrade pip && pip install /opt/platform

# Install service deps.
COPY services/$($svc.id)/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY services/$($svc.id)/app ./app

EXPOSE $($svc.port)
HEALTHCHECK --interval=30s --timeout=5s --retries=5 \
  CMD python -c "import urllib.request,sys;sys.exit(0 if urllib.request.urlopen('http://localhost:$($svc.port)/health').status==200 else 1)"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "$($svc.port)"]
"@
  Set-Content -Path "$dir\Dockerfile" -Value $dockerfile -Encoding UTF8

  # pytest.ini
  Set-Content -Path "$dir\pytest.ini" -Value "[pytest]`nasyncio_mode = auto`ntestpaths = tests`n" -Encoding UTF8

  # .env.example
  $envex = @"
SERVICE_NAME=$($svc.id)
ENV=dev
LOG_LEVEL=INFO
LOG_JSON=true
PLATFORM_INTERNAL_TOKEN=
CORS_ORIGINS=*
"@
  Set-Content -Path "$dir\.env.example" -Value $envex -Encoding UTF8

  # test_health.py
  $tHealth = @"
from fastapi.testclient import TestClient
from app.main import app


def test_health():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["service"] == "$($svc.id)"
    assert body["status"] == "ok"


def test_root():
    client = TestClient(app)
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["service"] == "$($svc.id)"


def test_metrics():
    client = TestClient(app)
    client.get("/health")
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "http_requests_total" in r.text
"@
  Set-Content -Path "$dir\tests\test_health.py" -Value $tHealth -Encoding UTF8

  Write-Host "scaffolded $($svc.id) on :$($svc.port)"
}
