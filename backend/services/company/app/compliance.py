"""Compliance calendar — effective-dated config from the scaffold CSV."""
from __future__ import annotations

import csv
from datetime import date, timedelta

from .db import scaffold_dir


def load_calendar(today: date | None = None) -> list[dict]:
    today = today or date.today()
    path = scaffold_dir() / "compliance" / "compliance_calendar.csv"
    with path.open(encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    out = []
    for r in rows:
        due_raw = (r.get("example_due_fy2025_26") or "").strip()
        due = date.fromisoformat(due_raw) if due_raw else None
        if due is None:
            status = "unscheduled"
        elif due < today:
            status = "overdue"
        elif due <= today + timedelta(days=30):
            status = "due_soon"
        else:
            status = "upcoming"
        out.append({
            "area": r["area"],
            "form": r["form"],
            "authority": r["authority"],
            "frequency": r["frequency"],
            "covers": r["covers"],
            "due_date_rule": r["due_date_rule"],
            "due_date": due.isoformat() if due else None,
            "status": status,
            "notes": r.get("notes", ""),
        })
    return out
