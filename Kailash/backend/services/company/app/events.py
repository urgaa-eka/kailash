"""Center Lake egress — typed events onto the EventBridge bus.

Env-gated: without EVENT_BUS_NAME every publish is a no-op, so local dev
and tests run unchanged. On AWS the Lambdas set EVENT_BUS_NAME and the
segment publishes `JournalPosted`, `ReturnGenerated`,
`ReconciliationCompleted`, `FinancialFactsPublished`, `ComplianceDue`.
"""
from __future__ import annotations

import json
import os
from datetime import UTC, datetime

from backend.platform import get_logger

log = get_logger("company.events")

SOURCE = "kailash.company-segment"


def publish(detail_type: str, detail: dict) -> bool:
    """Fire one event; returns True if actually published."""
    bus = os.environ.get("EVENT_BUS_NAME")
    if not bus:
        return False
    try:
        import boto3  # runtime-provided on Lambda; optional locally

        boto3.client("events").put_events(
            Entries=[{
                "EventBusName": bus,
                "Source": SOURCE,
                "DetailType": detail_type,
                "Time": datetime.now(UTC),
                "Detail": json.dumps(detail, default=str),
            }]
        )
        log.info("event_published", extra={"event": detail_type})
        return True
    except Exception:  # noqa: BLE001 - egress must never break the ledger path
        log.exception("event_publish_failed")
        return False


def journal_posted(journal: dict) -> None:
    publish("JournalPosted", {
        "journal_id": journal.get("journal_id"),
        "fy": journal.get("fy"),
        "voucher_no": journal.get("voucher_no"),
        "posted_at": journal.get("posted_at"),
    })


def return_generated(kind: str, gstin: str, period: str, summary: dict) -> None:
    publish("ReturnGenerated", {
        "return": kind, "gstin": gstin, "period": period, **summary,
    })


def reconciliation_completed(result: dict) -> None:
    publish("ReconciliationCompleted", {
        "fy": result.get("fy"),
        "control_points_run": result.get("control_points_run"),
        "matched": result.get("matched"),
        "open_variances": result.get("open_variances"),
    })


def financial_facts_published(facts: dict) -> None:
    publish("FinancialFactsPublished", facts)
