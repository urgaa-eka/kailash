from backend.shared import BaseServiceSettings


class Settings(BaseServiceSettings):
    service_name: str = "company"
    version: str = "0.1.0"

    # Ledger database (PostgreSQL). Required — no default on purpose: a
    # fallback DSN here would carry a credential in source and would let the
    # service start against the wrong database instead of failing. Set
    # COMPANY_DB_URL (docker-compose publishes postgres on loopback via
    # docker-compose.override.yml).
    company_db_url: str

    # Path to the company-segment scaffold (schema DDL + seed CSVs).
    # Empty string -> auto-resolve to <repo-root>/company-segment.
    company_scaffold_dir: str = ""

    # Identities stamped on journals created by the automated ingestion
    # pipeline (maker-checker requires two distinct identities; the
    # "checker" here is the validation engine, per ingestion/README.md).
    ingest_maker: str = "ingestion-api"
    ingest_checker: str = "posting-engine"


settings = Settings()
