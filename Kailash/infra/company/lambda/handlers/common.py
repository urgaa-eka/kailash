"""Shared Lambda bootstrap — resolves the ledger DSN from Secrets Manager.

On AWS the DB credential lives in the Aurora secret (COMPANY_DB_SECRET_ARN);
locally COMPANY_DB_URL is already set and this is a no-op. Resolution runs
once per container (cold start) and pins the env var for the engine code.
"""
from __future__ import annotations

import json
import os

_resolved = False


def resolve_db_url() -> None:
    global _resolved
    if _resolved or os.environ.get("COMPANY_DB_URL"):
        _resolved = True
        return
    arn = os.environ.get("COMPANY_DB_SECRET_ARN")
    if not arn:
        raise RuntimeError("neither COMPANY_DB_URL nor COMPANY_DB_SECRET_ARN set")
    import boto3

    raw = boto3.client("secretsmanager").get_secret_value(SecretId=arn)["SecretString"]
    s = json.loads(raw)
    host = os.environ.get("COMPANY_DB_HOST", s.get("host"))  # RDS Proxy endpoint override
    dbname = s.get("dbname", "kailash")
    os.environ["COMPANY_DB_URL"] = (
        f"postgresql://{s['username']}:{s['password']}@{host}:{s.get('port', 5432)}/{dbname}"
    )
    _resolved = True
