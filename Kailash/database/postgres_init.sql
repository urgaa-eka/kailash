-- Postgres bootstrap for fresh volumes (docker-entrypoint-initdb.d).
-- Extensions the Kailash stack uses: pgcrypto (PII column encryption,
-- digests), uuid-ossp (UUID generation). Idempotent.
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
