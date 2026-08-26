# Build the Lambda asset bundle at infra/company/lambda-dist (Windows dev).
# Layout mirrors build-lambda.sh: handlers/ + backend/ + company-segment/ + deps.
$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $PSScriptRoot          # infra/company
$Repo = Split-Path -Parent (Split-Path -Parent $Here)
$Dist = Join-Path $Here "lambda-dist"

if (Test-Path $Dist) { Remove-Item -Recurse -Force $Dist }
New-Item -ItemType Directory -Force (Join-Path $Dist "backend/services/company") | Out-Null

$req = Join-Path $Here "lambda/requirements.txt"
python -m pip install -q -r $req -t $Dist `
  --platform manylinux2014_x86_64 --python-version 3.11 --only-binary=:all:
if ($LASTEXITCODE -ne 0) { python -m pip install -q -r $req -t $Dist }

Copy-Item -Recurse (Join-Path $Here "lambda/handlers") (Join-Path $Dist "handlers")
Copy-Item -Recurse (Join-Path $Repo "backend/platform") (Join-Path $Dist "backend/platform")
Copy-Item -Recurse (Join-Path $Repo "backend/services/company/app") (Join-Path $Dist "backend/services/company/app")
foreach ($f in @("backend/__init__.py", "backend/services/__init__.py", "backend/services/company/__init__.py")) {
  New-Item -ItemType File -Force (Join-Path $Dist $f) | Out-Null
}
New-Item -ItemType Directory -Force (Join-Path $Dist "company-segment") | Out-Null
foreach ($d in @("schema", "templates", "compliance")) {
  Copy-Item -Recurse (Join-Path $Repo "company-segment/$d") (Join-Path $Dist "company-segment/$d")
}
Get-ChildItem $Dist -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
Write-Output "lambda bundle ready: $Dist"
