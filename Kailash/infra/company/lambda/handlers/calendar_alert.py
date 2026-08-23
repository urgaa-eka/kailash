"""Compliance-calendar alerter — EventBridge Scheduler target.

Runs daily: loads the effective-dated calendar, emits a `ComplianceDue`
event for anything overdue or due within the alert window so downstream
consumers (dashboards, Eka Brain agents, notifications) react.
"""
from __future__ import annotations

import os

from handlers.common import resolve_db_url

resolve_db_url()

from backend.services.company.app import compliance, events  # noqa: E402


def handler(event=None, context=None):  # noqa: ANN001
    window = int(os.environ.get("ALERT_WINDOW_DAYS", "30"))
    cal = compliance.load_calendar()
    due = [c for c in cal if c["status"] in ("overdue", "due_soon")]
    for item in due:
        events.publish("ComplianceDue", item)
    return {
        "checked": len(cal),
        "alerts": len(due),
        "window_days": window,
        "items": [f"{c['area']}/{c['form']}:{c['status']}" for c in due],
    }
