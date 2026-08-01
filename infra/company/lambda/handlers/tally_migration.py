"""Tally migration — Step Functions step handlers.

Steps (event["step"]):
  stage        -> read the staged export from S3 (JSON, or Tally Day Book
                  XML reduced to ledger opening balances), return line count
  post_opening -> post the opening-balance journal (origin=TALLY_MIGRATION)
  verify       -> prove co_v_trial_balance ties to the staged Tally totals

Input: {"step": "...", "bucket": "...", "key": "...", "gstin": "27...",
        "as_of": "2025-04-01", "maker": "migration", "checker": "ca-verified"}

Staged file shape (JSON): {"lines": [{"account_code": "5030", "debit": X,
"credit": Y}, ...]} — produced from Tally's Trial Balance export via the
co_map_tally mapping. A minimal Tally-XML ledger parser is included for
direct Day Book exports.
"""
from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from decimal import Decimal

from handlers.common import resolve_db_url

resolve_db_url()

from backend.services.company.app.db import get_conn  # noqa: E402
from backend.services.company.app.ingest import post_opening_balance  # noqa: E402
from backend.services.company.app.reports import trial_balance  # noqa: E402


def _fetch(bucket: str, key: str) -> bytes:
    import boto3

    return boto3.client("s3").get_object(Bucket=bucket, Key=key)["Body"].read()


def parse_tally_xml(raw: bytes) -> list[dict]:
    """Minimal Tally master export parser: LEDGER name + OPENINGBALANCE.
    Tally sign convention: positive = credit, negative = debit."""
    root = ET.fromstring(raw.decode("utf-8", errors="replace"))
    lines = []
    for ledger in root.iter("LEDGER"):
        name = ledger.get("NAME") or (
            ledger.findtext("NAME") or ""
        )
        ob = ledger.findtext("OPENINGBALANCE")
        if not ob:
            continue
        amt = Decimal(ob.replace(",", ""))
        lines.append({
            "tally_name": name.strip(),
            "debit": float(-amt) if amt < 0 else 0.0,
            "credit": float(amt) if amt > 0 else 0.0,
        })
    return lines


def _load_lines(event) -> list[dict]:
    raw = _fetch(event["bucket"], event["key"])
    if event["key"].lower().endswith(".xml"):
        parsed = parse_tally_xml(raw)
        # Resolve Tally ledger names -> account codes via co_map_tally.
        with get_conn() as conn:
            out = []
            for ln in parsed:
                row = conn.execute(
                    """
                    SELECT a.account_code FROM co_map_tally m
                    JOIN co_account a ON a.account_id = m.kailash_id
                    WHERE m.tally_name = %s AND m.entity = 'account'
                    """,
                    (ln["tally_name"],),
                ).fetchone()
                if row is None:
                    raise ValueError(
                        f"Tally ledger '{ln['tally_name']}' has no co_map_tally entry"
                    )
                out.append({"account_code": row["account_code"],
                            "debit": ln["debit"], "credit": ln["credit"]})
            return out
    return json.loads(raw)["lines"]


def handler(event, context=None):  # noqa: ANN001
    step = event["step"]
    if step == "stage":
        lines = _load_lines(event)
        total_dr = sum(Decimal(str(ln.get("debit", 0))) for ln in lines)
        total_cr = sum(Decimal(str(ln.get("credit", 0))) for ln in lines)
        return {**event, "result": {
            "lines": len(lines), "total_debit": str(total_dr),
            "total_credit": str(total_cr),
            "balanced": total_dr == total_cr,
        }}
    if step == "post_opening":
        from datetime import date

        lines = _load_lines(event)
        with get_conn() as conn:
            j = post_opening_balance(
                conn, gstin=event["gstin"],
                as_of=date.fromisoformat(event["as_of"]),
                lines=lines, maker=event.get("maker", "migration"),
                checker=event.get("checker", "ca-verified"),
            )
        return {**event, "result": {
            "journal_id": j["journal_id"], "fy": j["fy"],
            "voucher_no": j["voucher_no"], "status": j["status"],
        }}
    if step == "verify":
        with get_conn() as conn:
            from datetime import date

            from backend.services.company.app.db import fy_for
            fy = fy_for(date.fromisoformat(event["as_of"]))
            tb = trial_balance(conn, fy)
        return {**event, "result": {
            "fy": tb["fy"], "balanced": tb["balanced"],
            "total_debit": tb["total_debit"],
            "total_credit": tb["total_credit"],
        }}
    raise ValueError(f"unknown migration step {step}")
