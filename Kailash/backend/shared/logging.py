"""Structured logging using the stdlib — no structlog dependency.

- JSON output when ``log_json=True``, plaintext otherwise.
- Attaches ``request_id`` automatically if present in the log record extras.
"""
from __future__ import annotations

import json
import logging
import sys
import time
from typing import Any


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:  # noqa: D401
        payload: dict[str, Any] = {
            "ts": round(time.time(), 3),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        for key in ("service", "request_id", "route", "upstream", "latency_ms", "event"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: str = "INFO", json_mode: bool = True, service: str | None = None) -> None:
    root = logging.getLogger()
    for h in list(root.handlers):
        root.removeHandler(h)
    handler = logging.StreamHandler(sys.stdout)
    if json_mode:
        handler.setFormatter(_JsonFormatter())
    else:
        fmt = "%(asctime)s %(levelname)s %(name)s :: %(message)s"
        handler.setFormatter(logging.Formatter(fmt))
    root.addHandler(handler)
    root.setLevel(level.upper())

    if service:
        class _ServiceFilter(logging.Filter):
            def __init__(self, svc: str) -> None:
                super().__init__()
                self._svc = svc

            def filter(self, record: logging.LogRecord) -> bool:  # noqa: D401
                if not hasattr(record, "service"):
                    record.service = self._svc
                return True

        handler.addFilter(_ServiceFilter(service))


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
