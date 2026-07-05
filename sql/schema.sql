-- ============================================================
-- Bluestock MF Analytics — SQLite Star Schema
-- Day 2: Data Cleaning + SQL Database Design
-- ============================================================

PRAGMA foreign_keys = ON;

-- ── Dimension: Fund ────────────────────────────────────────
-- One row per AMFI scheme code (Regular and Direct are separate rows)

CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code          INTEGER PRIMARY KEY,
    fund_house         TEXT    NOT NULL,
    scheme_name        TEXT    NOT NULL,
    category           TEXT    NOT NULL,
    sub_category       TEXT    NOT NULL,
    plan               TEXT    NOT NULL,
    launch_date        TEXT,
    benchmark          TEXT,
    expense_ratio_pct  REAL,
    exit_load_pct      REAL,
    min_sip_amount     INTEGER,
    min_lumpsum_amount INTEGER,
    fund_manager       TEXT,
    risk_category      TEXT,
    sebi_category_code TEXT
);

-- ── Dimension: Date ────────────────────────────────────────
-- One row per calendar day — drives time-based joins on all fact tables

CREATE TABLE IF NOT EXISTS dim_date (
    date        TEXT    PRIMARY KEY,   -- YYYY-MM-DD
    year        INTEGER NOT NULL,
    quarter     INTEGER NOT NULL,
    month       INTEGER NOT NULL,
    month_name  TEXT    NOT NULL,
    week        INTEGER NOT NULL,
    day         INTEGER NOT NULL,
    weekday     TEXT    NOT NULL,
    is_weekend  INTEGER NOT NULL       -- 1 = Sat/Sun, 0 = weekday
);

-- ── Fact: NAV History ──────────────────────────────────────
-- One row per fund per calendar day (weekends forward-filled in cleaning)

CREATE TABLE IF NOT EXISTS fact_nav (
    nav_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code INTEGER NOT NULL REFERENCES dim_fund(amfi_code),
    date      TEXT    NOT NULL REFERENCES dim_date(date),
    nav       REAL    NOT NULL,
    UNIQUE(amfi_code, date)
);

-- ── Fact: Investor Transactions ────────────────────────────
-- One row per investor purchase / redemption event

CREATE TABLE IF NOT EXISTS fact_transactions (
    transaction_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id        TEXT    NOT NULL,
    transaction_date   TEXT    NOT NULL REFERENCES dim_date(date),
    amfi_code          INTEGER NOT NULL REFERENCES dim_fund(amfi_code),
    transaction_type   TEXT    NOT NULL,   -- SIP | Lumpsum | Redemption
    amount_inr         INTEGER NOT NULL,
    state              TEXT,
    city               TEXT,
    city_tier          TEXT,               -- T30 | B30
    age_group          TEXT,
    gender             TEXT,
    annual_income_lakh REAL,
    payment_mode       TEXT,
    kyc_status         TEXT                -- Verified | Pending
);

-- ── Fact: Scheme Performance ───────────────────────────────
-- One row per fund — point-in-time performance snapshot

CREATE TABLE IF NOT EXISTS fact_performance (
    amfi_code          INTEGER PRIMARY KEY REFERENCES dim_fund(amfi_code),
    return_1yr_pct     REAL,
    return_3yr_pct     REAL,
    return_5yr_pct     REAL,
    benchmark_3yr_pct  REAL,
    alpha              REAL,
    beta               REAL,
    sharpe_ratio       REAL,
    sortino_ratio      REAL,
    std_dev_ann_pct    REAL,
    max_drawdown_pct   REAL,
    aum_crore          REAL,
    expense_ratio_pct  REAL,
    morningstar_rating INTEGER,
    risk_grade         TEXT
);

-- ── Fact: AUM by Fund House ────────────────────────────────
-- Semi-annual AUM snapshots per fund house

CREATE TABLE IF NOT EXISTS fact_aum (
    aum_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    date        TEXT    NOT NULL REFERENCES dim_date(date),
    fund_house  TEXT    NOT NULL,
    aum_crore   REAL    NOT NULL,
    num_schemes INTEGER,
    UNIQUE(date, fund_house)
);