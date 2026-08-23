"""Company-segment API — L0 ingestion, L1 posting, L2 compliance,
L3 reconciliation, L4 reporting/dashboard.

Mutating endpoints require X-Platform-Token; reads are open, matching the
other platform services.
"""
from __future__ import annotations

import os
from datetime import date

from fastapi import Depends, FastAPI, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, field_validator

from backend.shared import ApiResponse, ValidationError, require_internal_token

from . import compliance, dashboard, go4garage, gst, ingest, posting, recon, reports
from .db import audit, fy_for, get_conn, init_schema, seed_all

GSTIN_RE = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][0-9A-Z]Z[0-9A-Z]$"
STATE_RE = r"^[0-9]{2}$"
GST_2_0_SLABS = {0, 0.25, 3, 5, 12, 18, 28, 40}


# ---------------------------------------------------------------------------
# Request models (contracts)
# ---------------------------------------------------------------------------

class PartyIn(BaseModel):
    name: str
    gstin: str | None = Field(default=None, pattern=GSTIN_RE)
    pan: str | None = None
    state_code: str | None = Field(default=None, pattern=STATE_RE)


class SalesLineIn(BaseModel):
    item_name: str | None = None
    hsn_sac: str = Field(min_length=4, max_length=8)
    qty: float | None = None
    uqc: str | None = None
    rate: float | None = None
    taxable_value: float = Field(ge=0)
    gst_rate: float

    @field_validator("gst_rate")
    @classmethod
    def _slab(cls, v: float) -> float:
        if v not in GST_2_0_SLABS:
            raise ValueError(f"gst_rate {v} is not a GST 2.0 slab {sorted(GST_2_0_SLABS)}")
        return v


class SalesInvoiceIn(BaseModel):
    """Mirrors ingestion/sales_invoice.contract.json."""
    source_hash: str
    gstin: str = Field(pattern=GSTIN_RE)
    invoice_no: str
    invoice_date: date
    party: PartyIn
    supply_type: str = Field(pattern="^(B2B|B2CL|B2CS|EXPORT|SEZ|NIL|EXEMPT)$")
    place_of_supply: str = Field(pattern=STATE_RE)
    reverse_charge: bool = False
    irn: str | None = None
    ewb_no: str | None = None
    lines: list[SalesLineIn] = Field(min_length=1)
    totals: dict[str, float] | None = None


class PurchaseBillIn(BaseModel):
    source_hash: str
    gstin: str = Field(pattern=GSTIN_RE)
    bill_no: str
    bill_date: date
    vendor: PartyIn
    place_of_supply: str | None = Field(default=None, pattern=STATE_RE)
    itc_eligible: bool = True
    lines: list[SalesLineIn] = Field(min_length=1)


class BankTxnIn(BaseModel):
    source_hash: str
    txn_date: date
    value_date: date | None = None
    description: str | None = None
    debit: float = 0
    credit: float = 0
    running_balance: float | None = None


class BankStatementIn(BaseModel):
    bank_account_id: int
    txns: list[BankTxnIn] = Field(min_length=1)


class CompanyIn(BaseModel):
    legal_name: str
    cin: str | None = None
    pan: str | None = None
    tan: str | None = None
    incorporation_dt: date
    class_of_company: str | None = None
    registered_office: str | None = None
    gstin: str = Field(pattern=GSTIN_RE)
    authorised_capital: float = 0
    paidup_capital: float = 0


class BankAccountIn(BaseModel):
    bank_name: str
    account_no: str
    ifsc: str | None = None
    ledger_account_code: str = "5030"


class JournalLineIn(BaseModel):
    account_code: str
    debit: float = 0
    credit: float = 0


class ManualJournalIn(BaseModel):
    gstin: str = Field(pattern=GSTIN_RE)
    voucher_date: date
    narration: str | None = None
    maker: str
    lines: list[JournalLineIn] = Field(min_length=2)


class PostIn(BaseModel):
    checker: str


class ReverseIn(BaseModel):
    maker: str
    checker: str
    narration: str | None = None


class OpeningBalanceIn(BaseModel):
    gstin: str = Field(pattern=GSTIN_RE)
    as_of: date
    maker: str
    checker: str
    lines: list[JournalLineIn] = Field(min_length=1)


class ReconRunIn(BaseModel):
    fy: str = Field(pattern=r"^[0-9]{4}-[0-9]{2}$")
    period_label: str | None = None
    externals: dict[str, float | None] = Field(default_factory=dict)


class VarianceUpdateIn(BaseModel):
    status: str
    owner: str | None = None
    root_cause: str | None = None
    note: str | None = None


class TdsEntryIn(BaseModel):
    section: str
    fy: str = Field(pattern=r"^[0-9]{4}-[0-9]{2}$")
    quarter: str = Field(pattern="^Q[1-4]$")
    amount_paid: float
    tds_amount: float
    deductee_party_id: int | None = None
    challan_no: str | None = None
    return_form: str | None = None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

def register(app: FastAPI) -> None:
    protected = [Depends(require_internal_token)]

    # ---- L0/L1 admin -----------------------------------------------------
    @app.post("/admin/init", response_model=ApiResponse,
              dependencies=protected, tags=["admin"])
    async def admin_init():
        with get_conn() as conn:
            init_schema(conn)
            seeded = seed_all(conn)
        return ApiResponse(data={"schema": "applied", "seeded": seeded})

    @app.post("/admin/company", response_model=ApiResponse,
              dependencies=protected, tags=["admin"])
    async def admin_company(req: CompanyIn):
        with get_conn() as conn:
            existing = conn.execute(
                "SELECT company_id FROM co_company WHERE legal_name = %s",
                (req.legal_name,),
            ).fetchone()
            if existing:
                company_id = existing["company_id"]
            else:
                company_id = conn.execute(
                    """
                    INSERT INTO co_company (legal_name, cin, pan, tan,
                        incorporation_dt, class_of_company, registered_office,
                        authorised_capital, paidup_capital)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING company_id
                    """,
                    (req.legal_name, req.cin, req.pan, req.tan,
                     req.incorporation_dt, req.class_of_company,
                     req.registered_office, req.authorised_capital,
                     req.paidup_capital),
                ).fetchone()["company_id"]
            g = conn.execute(
                "SELECT gstin_id FROM co_gstin WHERE gstin = %s", (req.gstin,)
            ).fetchone()
            if g is None:
                g = conn.execute(
                    """
                    INSERT INTO co_gstin (company_id, gstin, state_code, effective_from)
                    VALUES (%s,%s,%s,%s) RETURNING gstin_id
                    """,
                    (company_id, req.gstin, req.gstin[:2], req.incorporation_dt),
                ).fetchone()
            audit(conn, "admin", "company_setup", "co_company", str(company_id),
                  after={"legal_name": req.legal_name, "gstin": req.gstin})
        return ApiResponse(data={"company_id": company_id, "gstin_id": g["gstin_id"]})

    @app.post("/admin/bank-account", response_model=ApiResponse,
              dependencies=protected, tags=["admin"])
    async def admin_bank_account(req: BankAccountIn):
        with get_conn() as conn:
            company = conn.execute(
                "SELECT company_id FROM co_company ORDER BY company_id LIMIT 1"
            ).fetchone()
            if company is None:
                raise ValidationError("set up the company first (POST /admin/company)")
            ledger = conn.execute(
                "SELECT account_id FROM co_account WHERE account_code = %s",
                (req.ledger_account_code,),
            ).fetchone()
            row = conn.execute(
                """
                INSERT INTO co_bank_account (company_id, bank_name, account_no,
                                             ifsc, ledger_account_id)
                VALUES (%s,%s,%s,%s,%s) RETURNING bank_account_id
                """,
                (company["company_id"], req.bank_name, req.account_no,
                 req.ifsc, ledger["account_id"] if ledger else None),
            ).fetchone()
        return ApiResponse(data=row)

    # ---- L0 ingestion ----------------------------------------------------
    @app.post("/ingest/sales", response_model=ApiResponse,
              dependencies=protected, tags=["ingestion"])
    async def ingest_sales(req: SalesInvoiceIn):
        with get_conn() as conn:
            result = ingest.ingest_sales_invoice(conn, req.model_dump(mode="json"))
        return ApiResponse(data=result)

    @app.post("/ingest/purchase", response_model=ApiResponse,
              dependencies=protected, tags=["ingestion"])
    async def ingest_purchase(req: PurchaseBillIn):
        with get_conn() as conn:
            result = ingest.ingest_purchase_bill(conn, req.model_dump(mode="json"))
        return ApiResponse(data=result)

    @app.post("/ingest/bank", response_model=ApiResponse,
              dependencies=protected, tags=["ingestion"])
    async def ingest_bank(req: BankStatementIn):
        with get_conn() as conn:
            result = ingest.ingest_bank_statement(
                conn, req.bank_account_id,
                [t.model_dump(mode="json") for t in req.txns],
            )
        return ApiResponse(data=result)

    @app.get("/ingest/errors", response_model=ApiResponse, tags=["ingestion"])
    async def ingest_errors(resolved: bool = False):
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM co_ingest_error WHERE resolved = %s ORDER BY error_id DESC LIMIT 200",
                (resolved,),
            ).fetchall()
        return ApiResponse(data={"errors": rows})

    # ---- L1 posting ------------------------------------------------------
    @app.post("/journal", response_model=ApiResponse,
              dependencies=protected, tags=["ledger"])
    async def create_manual_journal(req: ManualJournalIn):
        with get_conn() as conn:
            g = conn.execute(
                "SELECT gstin_id FROM co_gstin WHERE gstin = %s", (req.gstin,)
            ).fetchone()
            if g is None:
                raise ValidationError(f"unknown GSTIN {req.gstin}")
            from .db import account_by_code
            lines = [
                {"account_id": account_by_code(conn, ln.account_code)["account_id"],
                 "debit": ln.debit, "credit": ln.credit}
                for ln in req.lines
            ]
            j = posting.create_journal(
                conn, voucher_type="JOURNAL", voucher_date=req.voucher_date,
                gstin_id=g["gstin_id"], lines=lines, narration=req.narration,
                maker=req.maker,
            )
        return ApiResponse(data=j)

    @app.post("/journal/{fy}/{journal_id}/post", response_model=ApiResponse,
              dependencies=protected, tags=["ledger"])
    async def post_journal_route(fy: str, journal_id: int, req: PostIn):
        with get_conn() as conn:
            row = posting.post_journal(conn, journal_id, fy, req.checker)
        return ApiResponse(data=row)

    @app.post("/journal/{fy}/{journal_id}/reverse", response_model=ApiResponse,
              dependencies=protected, tags=["ledger"])
    async def reverse_journal_route(fy: str, journal_id: int, req: ReverseIn):
        with get_conn() as conn:
            row = posting.reverse_journal(
                conn, journal_id, fy,
                maker=req.maker, checker=req.checker, narration=req.narration,
            )
        return ApiResponse(data=row)

    @app.get("/journal/{fy}/{journal_id}", response_model=ApiResponse, tags=["ledger"])
    async def get_journal_route(fy: str, journal_id: int):
        with get_conn() as conn:
            row = posting.get_journal(conn, journal_id, fy)
        return ApiResponse(data=row)

    # ---- Tally migration -------------------------------------------------
    @app.post("/migration/opening-balance", response_model=ApiResponse,
              dependencies=protected, tags=["migration"])
    async def opening_balance(req: OpeningBalanceIn):
        with get_conn() as conn:
            j = ingest.post_opening_balance(
                conn, gstin=req.gstin, as_of=req.as_of,
                lines=[ln.model_dump() for ln in req.lines],
                maker=req.maker, checker=req.checker,
            )
        return ApiResponse(data=j)

    # ---- L2 GST ----------------------------------------------------------
    @app.post("/gst/gstr1/generate", response_model=ApiResponse,
              dependencies=protected, tags=["gst"])
    async def gstr1_generate(gstin: str = Query(pattern=GSTIN_RE),
                             period: str = Query(pattern=r"^[0-9]{6}$")):
        with get_conn() as conn:
            payload = gst.generate_gstr1(conn, gstin, period)
        return ApiResponse(data=payload)

    @app.get("/gst/gstr1", response_model=ApiResponse, tags=["gst"])
    async def gstr1_get(gstin: str = Query(pattern=GSTIN_RE),
                        period: str = Query(pattern=r"^[0-9]{6}$")):
        with get_conn() as conn:
            payload = gst.get_gstr1(conn, gstin, period)
        return ApiResponse(data=payload)

    @app.post("/gst/gstr3b/generate", response_model=ApiResponse,
              dependencies=protected, tags=["gst"])
    async def gstr3b_generate(gstin: str = Query(pattern=GSTIN_RE),
                              period: str = Query(pattern=r"^[0-9]{6}$")):
        with get_conn() as conn:
            payload = gst.generate_gstr3b(conn, gstin, period)
        return ApiResponse(data=payload)

    # ---- TDS (deduction capture feeding 24Q/26Q/27Q) ---------------------
    @app.post("/tds/entry", response_model=ApiResponse,
              dependencies=protected, tags=["tds"])
    async def tds_entry(req: TdsEntryIn):
        with get_conn() as conn:
            row = conn.execute(
                """
                INSERT INTO co_tds_ledger (section, deductee_party_id, fy,
                    quarter, amount_paid, tds_amount, challan_no, return_form)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING tds_id
                """,
                (req.section, req.deductee_party_id, req.fy, req.quarter,
                 req.amount_paid, req.tds_amount, req.challan_no,
                 req.return_form),
            ).fetchone()
        return ApiResponse(data=row)

    # ---- L4 reports ------------------------------------------------------
    @app.get("/reports/trial-balance", response_model=ApiResponse, tags=["reports"])
    async def trial_balance_route(fy: str = Query(pattern=r"^[0-9]{4}-[0-9]{2}$")):
        with get_conn() as conn:
            data = reports.trial_balance(conn, fy)
        return ApiResponse(data=data)

    @app.get("/reports/schedule-iii", response_model=ApiResponse, tags=["reports"])
    async def schedule_iii_route(fy: str = Query(pattern=r"^[0-9]{4}-[0-9]{2}$")):
        with get_conn() as conn:
            data = reports.schedule_iii(conn, fy)
        return ApiResponse(data=data)

    @app.post("/reports/financials/snapshot", response_model=ApiResponse,
              dependencies=protected, tags=["reports"])
    async def snapshot_route(fy: str = Query(pattern=r"^[0-9]{4}-[0-9]{2}$")):
        with get_conn() as conn:
            data = reports.snapshot_financials(conn, fy)
        return ApiResponse(data=data)

    # ---- L3 reconciliation ----------------------------------------------
    @app.post("/recon/run", response_model=ApiResponse,
              dependencies=protected, tags=["reconciliation"])
    async def recon_run(req: ReconRunIn):
        with get_conn() as conn:
            data = recon.run_reconciliation(
                conn, fy=req.fy, period_label=req.period_label,
                externals={k: v for k, v in req.externals.items() if v is not None},
            )
        return ApiResponse(data=data)

    @app.get("/recon/variances", response_model=ApiResponse, tags=["reconciliation"])
    async def recon_variances():
        with get_conn() as conn:
            data = recon.open_variances(conn)
        return ApiResponse(data={"variances": data})

    @app.patch("/recon/variance/{variance_id}", response_model=ApiResponse,
               dependencies=protected, tags=["reconciliation"])
    async def recon_variance_update(variance_id: int, req: VarianceUpdateIn):
        with get_conn() as conn:
            data = recon.resolve_variance(
                conn, variance_id, status=req.status, owner=req.owner,
                root_cause=req.root_cause, note=req.note,
            )
        return ApiResponse(data=data)

    # ---- Compliance calendar --------------------------------------------
    @app.get("/compliance/calendar", response_model=ApiResponse, tags=["compliance"])
    async def calendar_route():
        return ApiResponse(data={"calendar": compliance.load_calendar()})

    # ---- L4 dashboard ----------------------------------------------------
    @app.get("/dashboard", response_class=HTMLResponse, tags=["dashboard"])
    async def dashboard_route(fy: str | None = None):
        with get_conn() as conn:
            html = dashboard.render(conn, fy or fy_for(date.today()))
        return HTMLResponse(content=html)

    # ---- L4 Go4Garage FY dashboard --------------------------------------
    # The financial-controller view (ten departments, Net Payable, GST cockpit,
    # defects/decisions). The data source is chosen by the G4G_PROVIDER env var:
    #   knowledge-pack (default) — the confirmed Knowledge-Pack figures
    #   null                     — structure only, "awaiting source"
    # Zoho org 60083342031 / Supabase providers slot in here once their data is
    # populated (the target org is a near-empty rebuild today).
    _g4g_providers = {
        "knowledge-pack": go4garage.KnowledgePackProvider,
        "null": go4garage.NullProvider,
        "db": lambda: go4garage.DbProvider(get_conn),
    }
    _g4g_provider = _g4g_providers.get(
        os.environ.get("G4G_PROVIDER", "knowledge-pack"),
        go4garage.KnowledgePackProvider)()

    @app.get("/dashboard/fy", response_class=HTMLResponse, tags=["dashboard"])
    async def go4garage_dashboard(fy: str | None = None):
        default_fy = go4garage.model.FINANCIAL_YEARS[-1].fy
        html = go4garage.render_fy(_g4g_provider, fy or default_fy)
        return HTMLResponse(content=html)

    @app.get("/dashboard/fy/all", response_class=HTMLResponse, tags=["dashboard"])
    async def go4garage_dashboard_all():
        """All five FYs in one self-contained page (client-side switcher)."""
        return HTMLResponse(content=go4garage.render_static(_g4g_provider))

    # ---- Go4Garage data store (so the company can load / edit its figures) --
    @app.post("/go4garage/admin/init", response_model=ApiResponse,
              dependencies=protected, tags=["go4garage"])
    async def go4garage_init():
        """Create the g4g_* tables and seed them from the confirmed figures.
        Idempotent. Set G4G_PROVIDER=db to serve the dashboard from here."""
        with get_conn() as conn:
            go4garage.store.init_schema(conn)
            seeded = go4garage.store.seed_from_kp(conn)
        return ApiResponse(data={"schema": "applied", "years_seeded": seeded})

    @app.post("/go4garage/fy/{fy}", response_model=ApiResponse,
              dependencies=protected, tags=["go4garage"])
    async def go4garage_upsert_fy(fy: str, data: dict):
        """Upsert one financial year's figures (partial payloads allowed)."""
        if fy not in {m.fy for m in go4garage.model.FINANCIAL_YEARS}:
            raise ValidationError(f"unknown FY {fy!r}")
        with get_conn() as conn:
            go4garage.store.upsert_fy(conn, fy, data)
        return ApiResponse(data={"fy": fy, "upserted": True})

    # convenience: current FY label
    @app.get("/meta/fy", response_model=ApiResponse, tags=["meta"])
    async def meta_fy(on: date | None = None):
        d = on or date.today()
        return ApiResponse(data={"date": d.isoformat(), "fy": fy_for(d)})
