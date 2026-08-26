#!/usr/bin/env bash
# Build the Lambda asset bundle at infra/company/lambda-dist.
# Layout: handlers/ + backend/ (platform lib + company service) +
# company-segment/ (schema + templates) + pip deps at the root.
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
DIST="$HERE/lambda-dist"

rm -rf "$DIST"
mkdir -p "$DIST/backend/services/company"

pip install -q -r "$HERE/lambda/requirements.txt" -t "$DIST" \
  --platform manylinux2014_x86_64 --python-version 3.11 --only-binary=:all: \
  || pip install -q -r "$HERE/lambda/requirements.txt" -t "$DIST"

cp -r "$HERE/lambda/handlers" "$DIST/handlers"
cp -r "$REPO/backend/platform" "$DIST/backend/platform"
cp -r "$REPO/backend/services/company/app" "$DIST/backend/services/company/app"
touch "$DIST/backend/__init__.py" "$DIST/backend/services/__init__.py" \
      "$DIST/backend/services/company/__init__.py"
mkdir -p "$DIST/company-segment"
cp -r "$REPO/company-segment/schema" "$DIST/company-segment/schema"
cp -r "$REPO/company-segment/templates" "$DIST/company-segment/templates"
cp -r "$REPO/company-segment/compliance" "$DIST/company-segment/compliance"

find "$DIST" -name "__pycache__" -type d -prune -exec rm -rf {} +
echo "lambda bundle ready: $DIST"
