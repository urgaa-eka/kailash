"""Optional AWS accelerators around the Postgres system-of-record.

Both are env-gated no-ops locally. Postgres remains the source of truth
for idempotency and documents; these mirror the architecture doc's fast
paths (DynamoDB `source_hash` pre-check, S3 FY-partitioned vault).
"""
from __future__ import annotations

import json
import os

from backend.shared import get_logger

log = get_logger("company.cloud")


def _table():
    name = os.environ.get("IDEMPOTENCY_TABLE")
    if not name:
        return None
    import boto3

    return boto3.resource("dynamodb").Table(name)


def seen_hash(source_hash: str) -> bool:
    """Fast pre-check; a miss always falls through to the DB check."""
    try:
        t = _table()
        if t is None:
            return False
        item = t.get_item(Key={"source_hash": source_hash}).get("Item")
        return item is not None
    except Exception:  # noqa: BLE001 - accelerator only, DB stays authoritative
        log.exception("idempotency_precheck_failed")
        return False


def record_hash(source_hash: str, ref: str) -> None:
    try:
        t = _table()
        if t is None:
            return
        t.put_item(Item={"source_hash": source_hash, "ref": ref})
    except Exception:  # noqa: BLE001
        log.exception("idempotency_record_failed")


def vault_put(fy: str, category: str, name: str, payload: dict) -> str | None:
    """Store the raw source document in the FY-partitioned S3 vault."""
    bucket = os.environ.get("DOCUMENT_VAULT_BUCKET")
    if not bucket:
        return None
    try:
        import boto3

        key = f"Company/03_Source_Docs/FY{fy}/{category}/{name}.json"
        boto3.client("s3").put_object(
            Bucket=bucket, Key=key,
            Body=json.dumps(payload, default=str).encode(),
            ContentType="application/json",
        )
        return key
    except Exception:  # noqa: BLE001
        log.exception("vault_put_failed")
        return None
