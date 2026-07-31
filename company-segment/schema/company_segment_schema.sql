-- =====================================================================
--  KAILASH — COMPANY SEGMENT
--  PostgreSQL DDL : double-entry system-of-record + statutory compliance
--  Target: PostgreSQL 14+   |   Currency: INR   |   FY: Apr->Mar (India)
--  Namespace prefix: co_  (Company segment)
--  ---------------------------------------------------------------------
--  Load order is top-to-bottom. Idempotent-ish (IF NOT EXISTS) so it can
--  be re-run during the 3-day baseline build without dropping data.
--  ---------------------------------------------------------------------
--  v1.1 HARDENING (schema review fixes):
--    C1  Balance check now also guards the INSERT path — a journal can
--        never be INSERTed with status='posted'; it must be posted via
--        UPDATE so the Σdr=Σcr check always runs against real lines.
--    C2  co_journal_line rows are frozen (no INSERT/UPDATE/DELETE) once
--        the parent journal is posted (trg_block_posted_lines).
--    C3  Un-posting is forbidden: 'posted' may only transition to
--        'reversed'; 'reversed' is terminal. Header business fields are
--        compared wholesale, not selectively.
--    C4  co_journal.source_hash carries a UNIQUE index (source_hash, fy)
--        — partition-key-complete; the ingestion API additionally
--        enforces global (cross-FY) dedup before insert.
--    N1  DEFAULT partitions added so historical-FY Tally migration
--        vouchers land instead of erroring.
--    N2  Business-document -> journal links now carry fy and composite
--        FOREIGN KEYs (journal_id, fy) — the audit trail is enforced.
--    N3  co_populate_fiscal_calendar(from,to) generates calendar rows.
--    N4  co_tax_rate CHECK: cgst+sgst = total AND igst = total.
--    N5  co_account.fin_class generated column resolves the
--        account_type dual-dimension (AR is an ASSET, etc.).
--    N6  Maker-checker enforced at post time (checker NOT NULL and
--        distinct from maker).
--    N7  co_audit_log is trigger-enforced append-only.
--  Deferred to post-baseline (documented in README): row-level security
--  policies per GSTIN/cost-center; pgcrypto column encryption for PII.
-- =====================================================================

CREATE SCHEMA IF NOT EXISTS company;
SET search_path TO company, public;

-- =====================================================================
-- 0. ENUMS
-- =====================================================================
DO $$ BEGIN
  CREATE TYPE acct_type   AS ENUM ('ASSET','LIABILITY','EQUITY','INCOME','EXPENSE',
                                   'AR','AP','BANK','CASH','GST_OUT','GST_IN',
                                   'TDS_PAYABLE','TDS_RECEIVABLE');
  EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN
  CREATE TYPE norm_bal    AS ENUM ('D','C');
  EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN
  CREATE TYPE voucher_t   AS ENUM ('SALES','PURCHASE','RECEIPT','PAYMENT','CONTRA',
                                   'JOURNAL','CREDIT_NOTE','DEBIT_NOTE','OPENING','PAYROLL');
  EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN
  CREATE TYPE journal_st  AS ENUM ('draft','posted','reversed');
  EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN
  CREATE TYPE party_t     AS ENUM ('CUSTOMER','VENDOR','BOTH','EMPLOYEE','STATUTORY');
  EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN
  CREATE TYPE supply_t    AS ENUM ('B2B','B2CL','B2CS','EXPORT','SEZ','NIL','EXEMPT');
  EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN
  CREATE TYPE recon_sev   AS ENUM ('matched','minor','material');
  EXCEPTION WHEN duplicate_object THEN NULL; END $$;
DO $$ BEGIN
  CREATE TYPE recon_st    AS ENUM ('open','investigating','resolved','accepted');
  EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- =====================================================================
-- 1. MASTERS (dimensions)
-- =====================================================================

-- 1.1 Legal entity / Day-1 identity ----------------------------------
CREATE TABLE IF NOT EXISTS co_company (
    company_id      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    legal_name      TEXT        NOT NULL,
    cin             VARCHAR(21) UNIQUE,                 -- Corporate Identity No.
    pan             CHAR(10)    UNIQUE,
    tan             CHAR(10)    UNIQUE,
    incorporation_dt DATE       NOT NULL,               -- "Day 1"
    class_of_company TEXT,                              -- private / opc / small
    registered_office TEXT,
    authorised_capital  NUMERIC(18,2) DEFAULT 0,
    paidup_capital      NUMERIC(18,2) DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 1.2 GST registrations (one per state) ------------------------------
CREATE TABLE IF NOT EXISTS co_gstin (
    gstin_id        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    company_id      BIGINT      NOT NULL REFERENCES co_company(company_id),
    gstin           CHAR(15)    NOT NULL UNIQUE,
    state_code      CHAR(2)     NOT NULL,               -- first 2 chars of GSTIN
    reg_type        TEXT        DEFAULT 'Regular',
    einvoice_applicable BOOLEAN DEFAULT FALSE,          -- turnover > 5cr
    effective_from  DATE        NOT NULL,
    active          BOOLEAN     DEFAULT TRUE
);

-- 1.3 Fiscal calendar : every fact joins here ------------------------
CREATE TABLE IF NOT EXISTS co_fiscal_calendar (
    cal_date        DATE        PRIMARY KEY,
    fy              CHAR(7)     NOT NULL,               -- e.g. '2025-26'
    fy_start        DATE        NOT NULL,
    quarter         CHAR(2)     NOT NULL,               -- Q1..Q4
    month_no        SMALLINT    NOT NULL,               -- 1..12 (Apr=1)
    gst_period      CHAR(6)     NOT NULL                -- MMYYYY (GSTN format)
);

-- N3: populator — every fact joins the calendar; this fills it.
CREATE OR REPLACE FUNCTION co_populate_fiscal_calendar(p_from DATE, p_to DATE)
RETURNS INTEGER AS $$
DECLARE n INTEGER;
BEGIN
  INSERT INTO co_fiscal_calendar (cal_date, fy, fy_start, quarter, month_no, gst_period)
  SELECT s.d,
         to_char(s.fy_year, 'FM0000') || '-' || to_char((s.fy_year + 1) % 100, 'FM00'),
         make_date(s.fy_year, 4, 1),
         'Q' || (((s.m + 8) % 12) / 3 + 1)::text,
         ((s.m + 8) % 12 + 1)::smallint,
         to_char(s.d, 'MMYYYY')
  FROM (
    SELECT g.d::date AS d,
           EXTRACT(MONTH FROM g.d)::int AS m,
           CASE WHEN EXTRACT(MONTH FROM g.d) >= 4
                THEN EXTRACT(YEAR FROM g.d)::int
                ELSE EXTRACT(YEAR FROM g.d)::int - 1 END AS fy_year
    FROM generate_series(p_from::timestamp, p_to::timestamp, interval '1 day') AS g(d)
  ) s
  ON CONFLICT (cal_date) DO NOTHING;
  GET DIAGNOSTICS n = ROW_COUNT;
  RETURN n;
END; $$ LANGUAGE plpgsql SET search_path TO company, public;

-- 1.4 Chart of Accounts (tree) ---------------------------------------
CREATE TABLE IF NOT EXISTS co_account (
    account_id      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    account_code    VARCHAR(20) NOT NULL UNIQUE,
    account_name    TEXT        NOT NULL,
    parent_id       BIGINT      REFERENCES co_account(account_id),
    account_type    acct_type   NOT NULL,
    normal_balance  norm_bal    NOT NULL,
    schedule_iii_group TEXT     NOT NULL,               -- Schedule III line
    tax_nature      TEXT,                               -- GST_OUT/GST_IN/TDS_194C...
    -- N5: single statutory dimension derived from the operational subtype,
    -- so "assets = liabilities + equity" is assertable from one column.
    fin_class       TEXT GENERATED ALWAYS AS (
        CASE account_type
          WHEN 'ASSET'          THEN 'ASSET'
          WHEN 'AR'             THEN 'ASSET'
          WHEN 'BANK'           THEN 'ASSET'
          WHEN 'CASH'           THEN 'ASSET'
          WHEN 'GST_IN'         THEN 'ASSET'
          WHEN 'TDS_RECEIVABLE' THEN 'ASSET'
          WHEN 'LIABILITY'      THEN 'LIABILITY'
          WHEN 'AP'             THEN 'LIABILITY'
          WHEN 'GST_OUT'        THEN 'LIABILITY'
          WHEN 'TDS_PAYABLE'    THEN 'LIABILITY'
          WHEN 'EQUITY'         THEN 'EQUITY'
          WHEN 'INCOME'         THEN 'INCOME'
          WHEN 'EXPENSE'        THEN 'EXPENSE'
        END) STORED,
    is_leaf         BOOLEAN     DEFAULT TRUE,
    active          BOOLEAN     DEFAULT TRUE
);

-- 1.5 Parties (customers / vendors) ----------------------------------
CREATE TABLE IF NOT EXISTS co_party (
    party_id        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    party_name      TEXT        NOT NULL,
    party_type      party_t     NOT NULL,
    gstin           CHAR(15),
    pan             CHAR(10),
    state_code      CHAR(2),                            -- place-of-supply default
    is_msme         BOOLEAN     DEFAULT FALSE,          -- drives MSME-1
    udyam_no        TEXT,
    tds_applicable  BOOLEAN     DEFAULT FALSE,
    ledger_account_id BIGINT    REFERENCES co_account(account_id),  -- AR/AP control
    active          BOOLEAN     DEFAULT TRUE
);

-- 1.6 Items (goods/services) -----------------------------------------
CREATE TABLE IF NOT EXISTS co_item (
    item_id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    item_name       TEXT        NOT NULL,
    is_service      BOOLEAN     DEFAULT FALSE,
    hsn_sac         VARCHAR(8)  NOT NULL,               -- HSN (goods)/SAC (services)
    uqc             VARCHAR(10),                        -- unit quantity code
    default_tax_rate_id BIGINT,
    active          BOOLEAN     DEFAULT TRUE
);

-- 1.7 GST rate master (GST 2.0), effective-dated ---------------------
CREATE TABLE IF NOT EXISTS co_tax_rate (
    tax_rate_id     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    label           TEXT        NOT NULL,               -- 'GST 18%'
    total_rate      NUMERIC(5,2) NOT NULL,              -- 0/5/18/40 + niche
    cgst_rate       NUMERIC(6,3) NOT NULL,
    sgst_rate       NUMERIC(6,3) NOT NULL,
    igst_rate       NUMERIC(5,2) NOT NULL,
    cess_rate       NUMERIC(5,2) DEFAULT 0,
    effective_from  DATE        NOT NULL,               -- 2025-09-22 for GST 2.0
    effective_to    DATE,
    -- N4: a tax engine must not be able to hold an inconsistent split.
    CONSTRAINT chk_rate_split CHECK (
        cgst_rate + sgst_rate = total_rate AND igst_rate = total_rate
    )
);
DO $$ BEGIN
  ALTER TABLE co_item
      ADD CONSTRAINT co_item_tax_fk FOREIGN KEY (default_tax_rate_id)
      REFERENCES co_tax_rate(tax_rate_id);
  EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- 1.8 Cost centre / department ---------------------------------------
CREATE TABLE IF NOT EXISTS co_cost_center (
    cost_center_id  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name            TEXT        NOT NULL,
    parent_id       BIGINT      REFERENCES co_cost_center(cost_center_id),
    active          BOOLEAN     DEFAULT TRUE
);

-- 1.9 Employees (payroll) --------------------------------------------
CREATE TABLE IF NOT EXISTS co_employee (
    employee_id     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    emp_code        TEXT        UNIQUE,
    full_name       TEXT        NOT NULL,
    pan             CHAR(10),
    uan             VARCHAR(12),                        -- PF UAN
    esi_no          VARCHAR(20),
    cost_center_id  BIGINT      REFERENCES co_cost_center(cost_center_id),
    ctc_annual      NUMERIC(15,2),
    active          BOOLEAN     DEFAULT TRUE
);

-- 1.10 Bank accounts --------------------------------------------------
CREATE TABLE IF NOT EXISTS co_bank_account (
    bank_account_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    company_id      BIGINT      NOT NULL REFERENCES co_company(company_id),
    bank_name       TEXT        NOT NULL,
    account_no      TEXT        NOT NULL,
    ifsc            CHAR(11),
    ledger_account_id BIGINT    REFERENCES co_account(account_id),
    active          BOOLEAN     DEFAULT TRUE
);

-- 1.11 Document numbering series (gap-free, per GSTIN, per FY) --------
CREATE TABLE IF NOT EXISTS co_document_series (
    series_id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    gstin_id        BIGINT      NOT NULL REFERENCES co_gstin(gstin_id),
    voucher_type    voucher_t   NOT NULL,
    fy              CHAR(7)     NOT NULL,
    prefix          TEXT,
    last_number     BIGINT      NOT NULL DEFAULT 0,
    UNIQUE (gstin_id, voucher_type, fy)
);

-- =====================================================================
-- 2. LEDGER CORE (system of record) — partitioned by FY
-- =====================================================================

CREATE TABLE IF NOT EXISTS co_journal (
    journal_id      BIGINT      GENERATED ALWAYS AS IDENTITY,
    voucher_type    voucher_t   NOT NULL,
    voucher_no      TEXT        NOT NULL,
    voucher_date    DATE        NOT NULL,
    fy              CHAR(7)     NOT NULL,
    gstin_id        BIGINT      NOT NULL REFERENCES co_gstin(gstin_id),
    narration       TEXT,
    source_ref      TEXT,                               -- link to L0 document
    source_hash     TEXT,                               -- idempotency key
    origin          TEXT        DEFAULT 'KAILASH',      -- KAILASH | TALLY_MIGRATION
    status          journal_st  NOT NULL DEFAULT 'draft',
    reverses_journal_id BIGINT,                         -- correction trail
    reverses_fy     CHAR(7),                            -- N2: partition-aware link
    maker           TEXT,
    checker         TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    posted_at       TIMESTAMPTZ,
    PRIMARY KEY (journal_id, fy),
    FOREIGN KEY (reverses_journal_id, reverses_fy) REFERENCES co_journal(journal_id, fy)
) PARTITION BY LIST (fy);

-- Example partitions (add one per live FY) ----------------------------
CREATE TABLE IF NOT EXISTS co_journal_2025_26 PARTITION OF co_journal FOR VALUES IN ('2025-26');
CREATE TABLE IF NOT EXISTS co_journal_2026_27 PARTITION OF co_journal FOR VALUES IN ('2026-27');
-- N1: historical FYs (Tally migration) land here instead of erroring.
CREATE TABLE IF NOT EXISTS co_journal_default PARTITION OF co_journal DEFAULT;

CREATE TABLE IF NOT EXISTS co_journal_line (
    line_id         BIGINT      GENERATED ALWAYS AS IDENTITY,
    journal_id      BIGINT      NOT NULL,
    fy              CHAR(7)     NOT NULL,
    line_no         SMALLINT    NOT NULL,
    account_id      BIGINT      NOT NULL REFERENCES co_account(account_id),
    debit           NUMERIC(18,2) NOT NULL DEFAULT 0,
    credit          NUMERIC(18,2) NOT NULL DEFAULT 0,
    party_id        BIGINT      REFERENCES co_party(party_id),
    item_id         BIGINT      REFERENCES co_item(item_id),
    cost_center_id  BIGINT      REFERENCES co_cost_center(cost_center_id),
    tax_rate_id     BIGINT      REFERENCES co_tax_rate(tax_rate_id),
    hsn_sac         VARCHAR(8),
    place_of_supply CHAR(2),
    PRIMARY KEY (line_id, fy),
    FOREIGN KEY (journal_id, fy) REFERENCES co_journal(journal_id, fy) ON DELETE CASCADE,
    CONSTRAINT chk_one_side  CHECK ( (debit = 0) <> (credit = 0) ),   -- exactly one side
    CONSTRAINT chk_nonneg    CHECK ( debit >= 0 AND credit >= 0 )
) PARTITION BY LIST (fy);
CREATE TABLE IF NOT EXISTS co_journal_line_2025_26 PARTITION OF co_journal_line FOR VALUES IN ('2025-26');
CREATE TABLE IF NOT EXISTS co_journal_line_2026_27 PARTITION OF co_journal_line FOR VALUES IN ('2026-27');
CREATE TABLE IF NOT EXISTS co_journal_line_default PARTITION OF co_journal_line DEFAULT;

CREATE INDEX IF NOT EXISTS ix_jline_account ON co_journal_line (account_id);
CREATE INDEX IF NOT EXISTS ix_jline_party   ON co_journal_line (party_id);
CREATE INDEX IF NOT EXISTS ix_jrnl_date     ON co_journal (voucher_date);
CREATE INDEX IF NOT EXISTS ix_jrnl_gstin    ON co_journal (gstin_id);

-- C4: idempotency at the ledger. A UNIQUE index on a partitioned table
-- must include the partition key, so uniqueness here is per (hash, fy);
-- the posting/ingestion API additionally rejects a source_hash seen in
-- ANY fy before inserting (global dedup).
CREATE UNIQUE INDEX IF NOT EXISTS co_journal_source_hash_uq
    ON co_journal (source_hash, fy) WHERE source_hash IS NOT NULL;

-- 2.1 DOUBLE-ENTRY INVARIANT + MAKER-CHECKER (post time) -------------
-- C1: fires on INSERT too — a journal can never be born 'posted'.
-- N6: posting demands a checker distinct from the maker.
CREATE OR REPLACE FUNCTION co_assert_balanced() RETURNS TRIGGER AS $$
DECLARE d NUMERIC(18,2); c NUMERIC(18,2); was_posted BOOLEAN := FALSE;
BEGIN
  IF TG_OP = 'UPDATE' THEN
    was_posted := (OLD.status IN ('posted','reversed'));
  END IF;
  IF NEW.status = 'posted' AND NOT was_posted THEN
    IF TG_OP = 'INSERT' THEN
      RAISE EXCEPTION 'Journal cannot be INSERTed as posted; insert draft, add lines, then post';
    END IF;
    IF NEW.maker IS NULL OR NEW.checker IS NULL OR NEW.checker = NEW.maker THEN
      RAISE EXCEPTION 'Journal % posting requires maker and a distinct checker', NEW.journal_id;
    END IF;
    SELECT COALESCE(SUM(debit),0), COALESCE(SUM(credit),0)
      INTO d, c FROM co_journal_line WHERE journal_id = NEW.journal_id AND fy = NEW.fy;
    IF d <> c THEN
      RAISE EXCEPTION 'Journal % unbalanced: debit=% credit=%', NEW.journal_id, d, c;
    END IF;
    IF d = 0 THEN
      RAISE EXCEPTION 'Journal % has zero value', NEW.journal_id;
    END IF;
    NEW.posted_at := now();
  END IF;
  RETURN NEW;
END; $$ LANGUAGE plpgsql SET search_path TO company, public;

DROP TRIGGER IF EXISTS trg_assert_balanced ON co_journal;
CREATE TRIGGER trg_assert_balanced BEFORE UPDATE ON co_journal
  FOR EACH ROW EXECUTE FUNCTION co_assert_balanced();
DROP TRIGGER IF EXISTS trg_assert_balanced_ins ON co_journal;
CREATE TRIGGER trg_assert_balanced_ins BEFORE INSERT ON co_journal
  FOR EACH ROW EXECUTE FUNCTION co_assert_balanced();

-- 2.2 IMMUTABILITY : posted vouchers cannot be updated/deleted --------
-- C3: no un-posting ('posted' -> only 'reversed'; 'reversed' terminal),
-- and the whole business header is compared, not selected fields.
CREATE OR REPLACE FUNCTION co_block_posted_mutation() RETURNS TRIGGER AS $$
BEGIN
  IF (TG_OP = 'DELETE') THEN
    IF OLD.status IN ('posted','reversed') THEN
      RAISE EXCEPTION 'Posted journal % is immutable (use a reversal)', OLD.journal_id;
    END IF; RETURN OLD;
  END IF;
  IF OLD.status IN ('posted','reversed') THEN
    IF NEW.status NOT IN ('posted','reversed') THEN
      RAISE EXCEPTION 'Cannot un-post journal % (posted may only become reversed)', OLD.journal_id;
    END IF;
    IF OLD.status = 'reversed' AND NEW.status = 'posted' THEN
      RAISE EXCEPTION 'Cannot re-post reversed journal %', OLD.journal_id;
    END IF;
    IF (NEW.voucher_type, NEW.voucher_no, NEW.voucher_date, NEW.fy, NEW.gstin_id,
        NEW.narration, NEW.source_ref, NEW.source_hash, NEW.origin, NEW.maker,
        NEW.checker, NEW.reverses_journal_id, NEW.reverses_fy, NEW.created_at,
        NEW.posted_at)
       IS DISTINCT FROM
       (OLD.voucher_type, OLD.voucher_no, OLD.voucher_date, OLD.fy, OLD.gstin_id,
        OLD.narration, OLD.source_ref, OLD.source_hash, OLD.origin, OLD.maker,
        OLD.checker, OLD.reverses_journal_id, OLD.reverses_fy, OLD.created_at,
        OLD.posted_at) THEN
      RAISE EXCEPTION 'Posted journal % header is immutable', OLD.journal_id;
    END IF;
  END IF;
  RETURN NEW;
END; $$ LANGUAGE plpgsql SET search_path TO company, public;

DROP TRIGGER IF EXISTS trg_block_posted ON co_journal;
CREATE TRIGGER trg_block_posted BEFORE UPDATE OR DELETE ON co_journal
  FOR EACH ROW EXECUTE FUNCTION co_block_posted_mutation();

-- 2.3 C2: lines of a posted journal are frozen ------------------------
CREATE OR REPLACE FUNCTION co_block_posted_lines() RETURNS TRIGGER AS $$
DECLARE st journal_st;
BEGIN
  SELECT status INTO st FROM co_journal
   WHERE journal_id = COALESCE(NEW.journal_id, OLD.journal_id)
     AND fy = COALESCE(NEW.fy, OLD.fy);
  IF st IN ('posted','reversed') THEN
    RAISE EXCEPTION 'Lines of posted journal % are immutable (use a reversal)',
      COALESCE(NEW.journal_id, OLD.journal_id);
  END IF;
  RETURN COALESCE(NEW, OLD);
END; $$ LANGUAGE plpgsql SET search_path TO company, public;

DROP TRIGGER IF EXISTS trg_block_posted_lines ON co_journal_line;
CREATE TRIGGER trg_block_posted_lines
  BEFORE INSERT OR UPDATE OR DELETE ON co_journal_line
  FOR EACH ROW EXECUTE FUNCTION co_block_posted_lines();

-- =====================================================================
-- 3. TRANSACTION CAPTURE (business documents -> generate journals)
-- =====================================================================

CREATE TABLE IF NOT EXISTS co_sales_invoice (
    invoice_id      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    gstin_id        BIGINT      NOT NULL REFERENCES co_gstin(gstin_id),
    invoice_no      TEXT        NOT NULL,
    invoice_date    DATE        NOT NULL,
    party_id        BIGINT      NOT NULL REFERENCES co_party(party_id),
    supply_type     supply_t    NOT NULL,
    place_of_supply CHAR(2)     NOT NULL,
    taxable_value   NUMERIC(18,2) NOT NULL,
    cgst            NUMERIC(18,2) DEFAULT 0,
    sgst            NUMERIC(18,2) DEFAULT 0,
    igst            NUMERIC(18,2) DEFAULT 0,
    cess            NUMERIC(18,2) DEFAULT 0,
    total_value     NUMERIC(18,2) NOT NULL,
    irn             CHAR(64),                           -- e-invoice ref no.
    ewb_no          VARCHAR(15),                        -- e-way bill
    source_hash     TEXT        UNIQUE,                 -- idempotent ingestion
    journal_id      BIGINT,
    journal_fy      CHAR(7),                            -- N2: enforced audit trail
    FOREIGN KEY (journal_id, journal_fy) REFERENCES co_journal(journal_id, fy),
    UNIQUE (gstin_id, invoice_no)
);
CREATE TABLE IF NOT EXISTS co_sales_line (
    line_id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    invoice_id      BIGINT      NOT NULL REFERENCES co_sales_invoice(invoice_id) ON DELETE CASCADE,
    item_id         BIGINT      REFERENCES co_item(item_id),
    hsn_sac         VARCHAR(8)  NOT NULL,
    qty             NUMERIC(15,3),
    rate            NUMERIC(18,4),
    taxable_value   NUMERIC(18,2) NOT NULL,
    tax_rate_id     BIGINT      REFERENCES co_tax_rate(tax_rate_id)
);

CREATE TABLE IF NOT EXISTS co_purchase_bill (
    bill_id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    gstin_id        BIGINT      NOT NULL REFERENCES co_gstin(gstin_id),
    vendor_id       BIGINT      NOT NULL REFERENCES co_party(party_id),
    bill_no         TEXT        NOT NULL,
    bill_date       DATE        NOT NULL,
    place_of_supply CHAR(2),
    taxable_value   NUMERIC(18,2) NOT NULL,
    cgst            NUMERIC(18,2) DEFAULT 0,
    sgst            NUMERIC(18,2) DEFAULT 0,
    igst            NUMERIC(18,2) DEFAULT 0,
    cess            NUMERIC(18,2) DEFAULT 0,
    total_value     NUMERIC(18,2) NOT NULL,
    itc_eligible    BOOLEAN     DEFAULT TRUE,
    gstr2b_matched  BOOLEAN     DEFAULT FALSE,          -- ITC reconciliation
    source_hash     TEXT        UNIQUE,                 -- idempotent ingestion
    journal_id      BIGINT,
    journal_fy      CHAR(7),
    FOREIGN KEY (journal_id, journal_fy) REFERENCES co_journal(journal_id, fy),
    UNIQUE (gstin_id, vendor_id, bill_no)
);
CREATE TABLE IF NOT EXISTS co_purchase_line (
    line_id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    bill_id         BIGINT      NOT NULL REFERENCES co_purchase_bill(bill_id) ON DELETE CASCADE,
    item_id         BIGINT      REFERENCES co_item(item_id),
    hsn_sac         VARCHAR(8),
    taxable_value   NUMERIC(18,2) NOT NULL,
    tax_rate_id     BIGINT      REFERENCES co_tax_rate(tax_rate_id)
);

-- Bank statement lines (for BRS / bank sub-ledger reconciliation) -----
CREATE TABLE IF NOT EXISTS co_bank_txn (
    bank_txn_id     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    bank_account_id BIGINT      NOT NULL REFERENCES co_bank_account(bank_account_id),
    txn_date        DATE        NOT NULL,
    value_date      DATE,
    description     TEXT,
    debit           NUMERIC(18,2) DEFAULT 0,
    credit          NUMERIC(18,2) DEFAULT 0,
    running_balance NUMERIC(18,2),
    matched_journal_id BIGINT,
    matched_journal_fy CHAR(7),
    FOREIGN KEY (matched_journal_id, matched_journal_fy) REFERENCES co_journal(journal_id, fy),
    source_hash     TEXT        UNIQUE                  -- idempotent import
);

-- Payroll -------------------------------------------------------------
CREATE TABLE IF NOT EXISTS co_payroll_run (
    payroll_run_id  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    gstin_id        BIGINT      REFERENCES co_gstin(gstin_id),
    period          CHAR(6)     NOT NULL,               -- MMYYYY
    journal_id      BIGINT,
    journal_fy      CHAR(7),
    FOREIGN KEY (journal_id, journal_fy) REFERENCES co_journal(journal_id, fy)
);
CREATE TABLE IF NOT EXISTS co_payslip (
    payslip_id      BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    payroll_run_id  BIGINT      NOT NULL REFERENCES co_payroll_run(payroll_run_id) ON DELETE CASCADE,
    employee_id     BIGINT      NOT NULL REFERENCES co_employee(employee_id),
    gross           NUMERIC(15,2) NOT NULL,
    pf              NUMERIC(15,2) DEFAULT 0,
    esi             NUMERIC(15,2) DEFAULT 0,
    tds             NUMERIC(15,2) DEFAULT 0,            -- section 192
    net_pay         NUMERIC(15,2) NOT NULL
);

-- Fixed assets (dual: Companies Act Sch II + Income-tax WDV block) -----
CREATE TABLE IF NOT EXISTS co_fixed_asset (
    asset_id        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    asset_name      TEXT        NOT NULL,
    account_id      BIGINT      REFERENCES co_account(account_id),
    capitalised_on  DATE        NOT NULL,
    cost            NUMERIC(18,2) NOT NULL,
    useful_life_yrs NUMERIC(5,2),                       -- Schedule II
    it_block_rate   NUMERIC(5,2),                       -- Income-tax WDV %
    active          BOOLEAN     DEFAULT TRUE
);

-- =====================================================================
-- 4. COMPLIANCE / OUTPUT TABLES (versioned statutory artefacts)
-- =====================================================================

CREATE TABLE IF NOT EXISTS co_gstr1 (
    gstr1_id        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    gstin_id        BIGINT      NOT NULL REFERENCES co_gstin(gstin_id),
    gst_period      CHAR(6)     NOT NULL,
    generated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    status          TEXT        DEFAULT 'draft',        -- draft/filed
    payload         JSONB,                              -- full GSTN-schema JSON
    UNIQUE (gstin_id, gst_period)
);
CREATE TABLE IF NOT EXISTS co_gstr3b_summary (
    gstr3b_id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    gstin_id        BIGINT      NOT NULL REFERENCES co_gstin(gstin_id),
    gst_period      CHAR(6)     NOT NULL,
    outward_taxable NUMERIC(18,2) DEFAULT 0,
    output_tax      NUMERIC(18,2) DEFAULT 0,
    itc_available   NUMERIC(18,2) DEFAULT 0,
    net_payable     NUMERIC(18,2) DEFAULT 0,
    UNIQUE (gstin_id, gst_period)
);
CREATE TABLE IF NOT EXISTS co_itc_register (
    itc_id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    gstin_id        BIGINT      NOT NULL REFERENCES co_gstin(gstin_id),
    gst_period      CHAR(6)     NOT NULL,
    bill_id         BIGINT      REFERENCES co_purchase_bill(bill_id),
    itc_amount      NUMERIC(18,2) NOT NULL,
    status          TEXT        DEFAULT 'eligible',     -- eligible/ineligible/deferred
    UNIQUE (gstin_id, gst_period, bill_id)
);
CREATE TABLE IF NOT EXISTS co_tds_ledger (
    tds_id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    section         VARCHAR(8)  NOT NULL,               -- 192/194C/194J...
    deductee_party_id BIGINT    REFERENCES co_party(party_id),
    deductee_emp_id BIGINT      REFERENCES co_employee(employee_id),
    fy              CHAR(7)     NOT NULL,
    quarter         CHAR(2)     NOT NULL,
    amount_paid     NUMERIC(18,2) NOT NULL,
    tds_amount      NUMERIC(18,2) NOT NULL,
    challan_no      TEXT,
    return_form     VARCHAR(4)                          -- 24Q/26Q/27Q
);
CREATE TABLE IF NOT EXISTS co_financial_statement_line (
    fsl_id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    fy              CHAR(7)     NOT NULL,
    statement       TEXT        NOT NULL,               -- 'PL'/'BS'/'CF'
    schedule_iii_group TEXT     NOT NULL,
    amount          NUMERIC(18,2) NOT NULL,
    version         INT         NOT NULL DEFAULT 1,     -- 'as CA signed it'
    generated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS co_roc_filing (
    roc_id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    company_id      BIGINT      NOT NULL REFERENCES co_company(company_id),
    form_name       TEXT        NOT NULL,               -- AOC-4/MGT-7/DPT-3...
    fy              CHAR(7)     NOT NULL,
    due_date        DATE        NOT NULL,
    filed_date      DATE,
    srn             TEXT,                               -- MCA service request no.
    status          TEXT        DEFAULT 'pending'
);
CREATE TABLE IF NOT EXISTS co_statutory_register (
    reg_id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    company_id      BIGINT      NOT NULL REFERENCES co_company(company_id),
    register_type   TEXT        NOT NULL,               -- members/directors/charges
    payload         JSONB,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =====================================================================
-- 5. RECONCILIATION (internal Kailash  <->  CA / Tally)
-- =====================================================================

CREATE TABLE IF NOT EXISTS co_recon_control_point (
    cp_id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code            TEXT        NOT NULL UNIQUE,        -- 'FY_SALES','OUTPUT_TAX'...
    description     TEXT        NOT NULL,
    source_a        TEXT        NOT NULL,               -- internal definition
    source_b        TEXT        NOT NULL,               -- CA/Tally/GSTN definition
    tolerance_abs   NUMERIC(18,2) DEFAULT 0,
    tolerance_pct   NUMERIC(6,3)  DEFAULT 0,
    active          BOOLEAN     DEFAULT TRUE
);
CREATE TABLE IF NOT EXISTS co_recon_run (
    run_id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cp_id           BIGINT      NOT NULL REFERENCES co_recon_control_point(cp_id),
    period_label    TEXT        NOT NULL,               -- FY or MMYYYY
    value_internal  NUMERIC(18,2),
    value_external  NUMERIC(18,2),
    ref_internal    TEXT,
    ref_external    TEXT,
    run_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS co_recon_variance (
    variance_id     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    run_id          BIGINT      NOT NULL REFERENCES co_recon_run(run_id) ON DELETE CASCADE,
    variance_amt    NUMERIC(18,2) NOT NULL,
    variance_pct    NUMERIC(8,3),
    severity        recon_sev   NOT NULL,
    owner           TEXT,
    root_cause      TEXT,
    status          recon_st    NOT NULL DEFAULT 'open',
    note            TEXT,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- =====================================================================
-- 6. AUDIT LOG (immutable, append-only)
-- =====================================================================
CREATE TABLE IF NOT EXISTS co_audit_log (
    audit_id        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    actor           TEXT        NOT NULL,
    action          TEXT        NOT NULL,               -- post/reverse/edit_master...
    entity          TEXT        NOT NULL,
    entity_id       TEXT,
    before_val      JSONB,
    after_val       JSONB,
    at              TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- N7: append-only is a trigger-enforced fact, not a convention.
CREATE OR REPLACE FUNCTION co_block_audit_mutation() RETURNS TRIGGER AS $$
BEGIN
  RAISE EXCEPTION 'co_audit_log is append-only';
END; $$ LANGUAGE plpgsql SET search_path TO company, public;

DROP TRIGGER IF EXISTS trg_audit_immutable ON co_audit_log;
CREATE TRIGGER trg_audit_immutable BEFORE UPDATE OR DELETE ON co_audit_log
  FOR EACH ROW EXECUTE FUNCTION co_block_audit_mutation();

-- =====================================================================
-- 7. INGESTION STAGING + ERROR QUEUE
-- =====================================================================
CREATE TABLE IF NOT EXISTS co_ingest_error (
    error_id        BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source          TEXT        NOT NULL,               -- TALLY/SALES/BANK...
    payload         JSONB,
    reason_code     TEXT        NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved        BOOLEAN     DEFAULT FALSE
);
CREATE TABLE IF NOT EXISTS co_map_tally (
    map_id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tally_name      TEXT        NOT NULL,               -- Tally ledger/party/item
    entity          TEXT        NOT NULL,               -- account/party/item
    kailash_id      BIGINT      NOT NULL,
    UNIQUE (tally_name, entity)
);

-- =====================================================================
-- 8. REPORTING VIEWS (L4 projections — read-only)
-- =====================================================================

-- 8.1 Trial balance per FY -------------------------------------------
CREATE OR REPLACE VIEW co_v_trial_balance AS
SELECT l.fy, a.account_code, a.account_name, a.schedule_iii_group, a.normal_balance,
       a.fin_class,
       SUM(l.debit)  AS total_debit,
       SUM(l.credit) AS total_credit,
       SUM(l.debit) - SUM(l.credit) AS net_movement
FROM   co_journal_line l
JOIN   co_journal j ON j.journal_id = l.journal_id AND j.fy = l.fy
JOIN   co_account a ON a.account_id = l.account_id
WHERE  j.status IN ('posted','reversed')
GROUP  BY l.fy, a.account_code, a.account_name, a.schedule_iii_group,
          a.normal_balance, a.fin_class;

-- 8.2 Schedule III rollup (P&L + BS by group) ------------------------
CREATE OR REPLACE VIEW co_v_schedule_iii AS
SELECT l.fy,
       CASE WHEN a.fin_class IN ('INCOME','EXPENSE') THEN 'PL' ELSE 'BS' END AS statement,
       a.schedule_iii_group,
       SUM( CASE WHEN a.normal_balance='C' THEN (l.credit - l.debit)
                 ELSE (l.debit - l.credit) END ) AS amount
FROM   co_journal_line l
JOIN   co_journal j ON j.journal_id = l.journal_id AND j.fy = l.fy
JOIN   co_account a ON a.account_id = l.account_id
WHERE  j.status IN ('posted','reversed')
GROUP  BY l.fy,
         CASE WHEN a.fin_class IN ('INCOME','EXPENSE') THEN 'PL' ELSE 'BS' END,
         a.schedule_iii_group;

-- 8.3 Accounting-equation probe (assets = liabilities + equity + P&L) -
CREATE OR REPLACE VIEW co_v_accounting_equation AS
SELECT l.fy,
       SUM(CASE WHEN a.fin_class = 'ASSET'     THEN l.debit - l.credit ELSE 0 END) AS assets,
       SUM(CASE WHEN a.fin_class = 'LIABILITY' THEN l.credit - l.debit ELSE 0 END) AS liabilities,
       SUM(CASE WHEN a.fin_class = 'EQUITY'    THEN l.credit - l.debit ELSE 0 END) AS equity,
       SUM(CASE WHEN a.fin_class = 'INCOME'    THEN l.credit - l.debit ELSE 0 END)
     - SUM(CASE WHEN a.fin_class = 'EXPENSE'   THEN l.debit - l.credit ELSE 0 END) AS profit
FROM   co_journal_line l
JOIN   co_journal j ON j.journal_id = l.journal_id AND j.fy = l.fy
JOIN   co_account a ON a.account_id = l.account_id
WHERE  j.status IN ('posted','reversed')
GROUP  BY l.fy;

-- 8.4 Outward supplies feed for GSTR-1 -------------------------------
CREATE OR REPLACE VIEW co_v_gstr1_feed AS
SELECT s.gstin_id, to_char(s.invoice_date,'MMYYYY') AS gst_period,
       s.supply_type, s.place_of_supply, p.gstin AS counterparty_gstin,
       s.invoice_no, s.invoice_date, s.taxable_value, s.cgst, s.sgst, s.igst, s.cess,
       s.total_value
FROM   co_sales_invoice s JOIN co_party p ON p.party_id = s.party_id;

-- 8.5 Open reconciliation variances (RAG matrix source) --------------
CREATE OR REPLACE VIEW co_v_open_variances AS
SELECT cp.code, cp.description, rr.period_label,
       rr.value_internal, rr.value_external, v.variance_amt, v.variance_pct,
       v.severity, v.status, v.owner
FROM   co_recon_variance v
JOIN   co_recon_run rr ON rr.run_id = v.run_id
JOIN   co_recon_control_point cp ON cp.cp_id = rr.cp_id
WHERE  v.status <> 'resolved';

-- =====================================================================
--  END OF SCHEMA
--  Surrogate PKs use IDENTITY columns (PostgreSQL 10+). The two ledger
--  tables (co_journal, co_journal_line) are LIST-partitioned by fy and
--  therefore carry composite PKs that include fy. Partitions exist for
--  2025-26 and 2026-27 plus a DEFAULT partition for historical FYs.
--  Connections must SET search_path TO company, public (the service's
--  DB layer does this on every connection).
-- =====================================================================
