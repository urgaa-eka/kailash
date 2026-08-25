"""SQS ingestion worker — buffered L0 path for high-volume feeds.

Message body: {"type": "sales"|"purchase"|"bank", "payload": {...contract...}}.
Validation failures land in co_ingest_error (engine behaviour); a failed
record is re-raised so SQS retries and eventually parks it on the DLQ.
"""
from __future__ import annotations

import json

from handlers.common import resolve_db_url

resolve_db_url()

from backend.services.company.app import ingest  # noqa: E402
from backend.services.company.app.db import get_conn  # noqa: E402


def handler(event, context):  # noqa: ANN001
    results, failures = [], []
    for record in event.get("Records", []):
        body = json.loads(record["body"])
        kind = body["type"]
        try:
            with get_conn() as conn:
                if kind == "sales":
                    out = ingest.ingest_sales_invoice(conn, body["payload"])
                elif kind == "purchase":
                    out = ingest.ingest_purchase_bill(conn, body["payload"])
                elif kind == "bank":
                    out = ingest.ingest_bank_statement(
                        conn, body["payload"]["bank_account_id"],
                        body["payload"]["txns"],
                    )
                else:
                    raise ValueError(f"unknown ingest type {kind}")
            results.append(out)
        except Exception:  # noqa: BLE001 - partial-batch failure reporting
            failures.append({"itemIdentifier": record["messageId"]})
    return {"batchItemFailures": failures, "processed": len(results)}
