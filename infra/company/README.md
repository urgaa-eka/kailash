# infra/company — KailashCompanyStack

CDK (TypeScript) app deploying the **Company segment** to AWS, implementing
[`company-segment/docs/aws/Company_Segment_Backend_Architecture_AWS.md`](../../company-segment/docs/aws/Company_Segment_Backend_Architecture_AWS.md)
end-to-end. The Lambda application layer is the **same engine code** as
`backend/services/company/` — the local service, the tests, and the cloud
deployment all run one implementation.

## What the stack creates (94 resources)

| Layer | Resources |
|---|---|
| L1 ledger | Aurora Serverless v2 (PostgreSQL 16, `kailash` DB, KMS-encrypted, deletion-protected, 35-day PITR) behind **RDS Proxy** (TLS required), in private VPC subnets |
| L0 ingestion | REST API Gateway (+ **WAFv2**: AWS managed common rules + per-IP rate limit) → API Lambda; **SQS** buffer + DLQ → ingest-worker Lambda; **DynamoDB** `source_hash` idempotency table; **S3** document vault (versioned, KMS, lifecycle IA→Glacier, never auto-expires — Companies Act §128(5)) |
| L2 compliance | **Step Functions** `kailash-company-period-end-close`: lock → GSTR-1 → GSTR-3B → statements → recon → publish; **EventBridge rule** firing the compliance-calendar sweep daily at 09:00 IST |
| Migration | **Step Functions** `kailash-company-tally-migration`: stage (JSON or Tally XML) → balance check → post opening → verify trial balance |
| Center Lake | **EventBridge bus** `kailash-center-lake` — `JournalPosted`, `ReturnGenerated`, `ReconciliationCompleted`, `FinancialFactsPublished`, `ComplianceDue` |
| Secrets | Aurora credential secret; `kailash/company/gstn` placeholder for GSTN/IRP filing credentials |

Region defaults to **ap-south-1** (India data residency).

## Lambda functions

All share one asset bundle (engine code + handlers + scaffold + deps):

| Function | Handler | Role |
|---|---|---|
| `ApiFn` | `handlers.api_handler.handler` | Full FastAPI surface via Mangum |
| `IngestWorkerFn` | `handlers.ingest_worker.handler` | SQS batch consumer (partial-batch failure reporting) |
| `CloseStepFn` | `handlers.close_steps.handler` | Period-end close steps |
| `TallyMigrationFn` | `handlers.tally_migration.handler` | Tally staging/posting/verification |
| `CalendarAlertFn` | `handlers.calendar_alert.handler` | Daily `ComplianceDue` events |

DB credentials resolve from Secrets Manager at cold start
(`handlers/common.py`); locally `COMPANY_DB_URL` short-circuits it. The
EventBridge/DynamoDB/S3 touchpoints in the engine are env-gated
(`EVENT_BUS_NAME`, `IDEMPOTENCY_TABLE`, `DOCUMENT_VAULT_BUCKET`) — no-ops
in local dev/tests, active on Lambda.

## Build & deploy

```bash
# 1. Bundle the Lambda asset (engine + handlers + deps -> lambda-dist/)
bash scripts/build-lambda.sh          # or scripts/build-lambda.ps1 on Windows

# 2. Synthesize / deploy
npm install
npx cdk synth                          # verified in CI (company-infra job)
npx cdk bootstrap                      # once per account/region
npx cdk deploy

# 3. Bootstrap the ledger (once): call the API's /admin/init, then
#    /admin/company, then run the Tally migration state machine.
```

After deploy, apply the schema through the API:
`curl -X POST $ApiUrl/admin/init -H "X-Platform-Token: ..."` — the DDL and
seed CSVs ship inside the Lambda bundle.

## Local verification

- `backend/services/company/tests/test_z_close_flow.py` runs the actual
  Step Functions step handlers (close sequence + Tally migration + calendar
  alert) against local Postgres — the state-machine logic is tested without
  AWS.
- CI job `company-infra` builds the bundle and runs `cdk synth` on every
  push.

## Not wired yet (deliberate)

- **GSTN/IRP filing** — the secret + IAM grants exist; the actual filing
  call is the post-baseline step (shared construct with GSTSAAS per the
  architecture doc).
- **Textract / SageMaker / Bedrock touchpoints** — consumers of the bus,
  added when those features land platform-wide.
- **Cognito authorizer** — the API currently uses the platform
  `X-Platform-Token`; swap to Cognito + IAM Identity Center when org SSO
  is provisioned.
