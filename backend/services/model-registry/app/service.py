"""Model Registry — SQLite-backed lightweight MLflow-compatible registry.

Stores model versions + metrics + arbitrary tags. Good enough for internal
tracking; swap to full MLflow by pointing consumers at an MLflow server
and mirroring this API.
"""
from __future__ import annotations

import os
import sqlite3
import time
from contextlib import contextmanager
from typing import Any

from backend.shared import NotFoundError, ValidationError, get_logger

log = get_logger("model-registry")

DB_PATH = os.environ.get("MODEL_REGISTRY_DB", "/tmp/kailash_model_registry.db")


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            version TEXT NOT NULL,
            stage TEXT NOT NULL DEFAULT 'dev',
            created_at REAL NOT NULL,
            metrics TEXT NOT NULL DEFAULT '{}',
            tags TEXT NOT NULL DEFAULT '{}',
            artifact_uri TEXT,
            UNIQUE(name, version)
        );
        CREATE INDEX IF NOT EXISTS idx_models_name ON models(name);
        """
    )
    conn.commit()


@contextmanager
def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    try:
        _ensure_schema(c)
        yield c
    finally:
        c.close()


VALID_STAGES = {"dev", "staging", "prod", "archived"}


def register_model(
    name: str, version: str, metrics: dict[str, Any] | None = None,
    tags: dict[str, Any] | None = None, artifact_uri: str | None = None,
    stage: str = "dev",
) -> dict[str, Any]:
    import json
    if not name or not version:
        raise ValidationError("name and version are required")
    if stage not in VALID_STAGES:
        raise ValidationError(f"invalid stage: {stage}", hint=f"one of {sorted(VALID_STAGES)}")
    with _conn() as c:
        try:
            c.execute(
                "INSERT INTO models(name,version,stage,created_at,metrics,tags,artifact_uri) VALUES (?,?,?,?,?,?,?)",
                (name, version, stage, time.time(),
                 json.dumps(metrics or {}), json.dumps(tags or {}), artifact_uri),
            )
            c.commit()
        except sqlite3.IntegrityError:
            raise ValidationError(f"{name}@{version} already registered")
    return get_model(name, version)


def get_model(name: str, version: str) -> dict[str, Any]:
    import json
    with _conn() as c:
        row = c.execute(
            "SELECT * FROM models WHERE name=? AND version=?", (name, version),
        ).fetchone()
    if not row:
        raise NotFoundError(f"model not found: {name}@{version}")
    d = dict(row)
    d["metrics"] = json.loads(d["metrics"])
    d["tags"] = json.loads(d["tags"])
    return d


def list_models(name: str | None = None) -> list[dict[str, Any]]:
    import json
    with _conn() as c:
        if name:
            rows = c.execute(
                "SELECT * FROM models WHERE name=? ORDER BY created_at DESC", (name,),
            ).fetchall()
        else:
            rows = c.execute("SELECT * FROM models ORDER BY created_at DESC LIMIT 500").fetchall()
    out = []
    for r in rows:
        d = dict(r)
        d["metrics"] = json.loads(d["metrics"])
        d["tags"] = json.loads(d["tags"])
        out.append(d)
    return out


def promote(name: str, version: str, stage: str) -> dict[str, Any]:
    if stage not in VALID_STAGES:
        raise ValidationError(f"invalid stage: {stage}")
    with _conn() as c:
        cur = c.execute(
            "UPDATE models SET stage=? WHERE name=? AND version=?",
            (stage, name, version),
        )
        c.commit()
        if cur.rowcount == 0:
            raise NotFoundError(f"model not found: {name}@{version}")
    return get_model(name, version)
