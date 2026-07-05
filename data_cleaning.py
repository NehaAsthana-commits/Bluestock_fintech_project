"""
Day 2 — Data Cleaning
Cleans all 10 raw CSVs and saves them to data/processed/.
"""
import pandas as pd
import os

RAW = "data/raw"
PROCESSED = "data/processed"
os.makedirs(PROCESSED, exist_ok=True)


# ── helpers ────────────────────────────────────────────────────────────────

def save(df, name):
    path = f"{PROCESSED}/{name}.csv"
    df.to_csv(path, index=False)
    print(f"  saved {path}  ({len(df):,} rows)")
    return df


def parse_date_col(df, col):
    df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


# ── 01 fund_master ─────────────────────────────────────────────────────────

def clean_fund_master():
    print("\n[01] fund_master")
    df = pd.read_csv(f"{RAW}/01_fund_master.csv")
    df = parse_date_col(df, "launch_date")
    df = df.drop_duplicates()
    print(f"  shape: {df.shape}")
    return save(df, "01_fund_master")


# ── 02 nav_history ─────────────────────────────────────────────────────────

def clean_nav_history():
    print("\n[02] nav_history")
    df = pd.read_csv(f"{RAW}/02_nav_history.csv")
    df = parse_date_col(df, "date")

    # Remove duplicates and invalid NAV
    df = df.drop_duplicates(subset=["amfi_code", "date"])
    df = df[df["nav"] > 0]

    # Forward-fill missing calendar days per fund (weekends / holidays)
    all_dates = pd.date_range(df["date"].min(), df["date"].max(), freq="D")
    codes = df["amfi_code"].unique()
    idx = pd.MultiIndex.from_product([codes, all_dates], names=["amfi_code", "date"])
    df = (df.set_index(["amfi_code", "date"])
            .reindex(idx)
            .groupby(level="amfi_code")
            .ffill()
            .reset_index())

    df = df.sort_values(["amfi_code", "date"]).reset_index(drop=True)
    print(f"  shape after ffill: {df.shape}")
    return save(df, "02_nav_history")


# ── 03 aum_by_fund_house ───────────────────────────────────────────────────

def clean_aum_by_fund_house():
    print("\n[03] aum_by_fund_house")
    df = pd.read_csv(f"{RAW}/03_aum_by_fund_house.csv")
    df = parse_date_col(df, "date")
    # Keep only aum_crore (drop redundant lakh_crore column)
    df = df.drop(columns=["aum_lakh_crore"])
    df = df.drop_duplicates()
    print(f"  shape: {df.shape}")
    return save(df, "03_aum_by_fund_house")


# ── 04 monthly_sip_inflows ─────────────────────────────────────────────────

def clean_monthly_sip_inflows():
    print("\n[04] monthly_sip_inflows")
    df = pd.read_csv(f"{RAW}/04_monthly_sip_inflows.csv")
    # month is YYYY-MM — store as period string, keep as-is for DB compatibility
    df["month"] = pd.to_datetime(df["month"] + "-01").dt.to_period("M").astype(str)
    # yoy_growth_pct: 12 NaN expected (first year), leave as-is
    df = df.drop_duplicates()
    print(f"  shape: {df.shape}, yoy NaN: {df['yoy_growth_pct'].isna().sum()} (expected)")
    return save(df, "04_monthly_sip_inflows")


# ── 05 category_inflows ────────────────────────────────────────────────────

def clean_category_inflows():
    print("\n[05] category_inflows")
    df = pd.read_csv(f"{RAW}/05_category_inflows.csv")
    df["month"] = pd.to_datetime(df["month"] + "-01").dt.to_period("M").astype(str)
    df = df.drop_duplicates()
    print(f"  shape: {df.shape}")
    return save(df, "05_category_inflows")


# ── 06 industry_folio_count ────────────────────────────────────────────────

def clean_industry_folio_count():
    print("\n[06] industry_folio_count")
    df = pd.read_csv(f"{RAW}/06_industry_folio_count.csv")
    # Column called 'month' but data is quarterly — rename for clarity
    df = df.rename(columns={"month": "quarter_start"})
    df["quarter_start"] = pd.to_datetime(df["quarter_start"] + "-01").dt.to_period("M").astype(str)
    df = df.drop_duplicates()
    print(f"  shape: {df.shape}")
    return save(df, "06_industry_folio_count")


# ── 07 scheme_performance ──────────────────────────────────────────────────

def clean_scheme_performance():
    print("\n[07] scheme_performance")
    df = pd.read_csv(f"{RAW}/07_scheme_performance.csv")

    return_cols = ["return_1yr_pct", "return_3yr_pct", "return_5yr_pct", "benchmark_3yr_pct"]
    for col in return_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Flag anomalies
    anomalies = df[
        (df["expense_ratio_pct"] < 0.1) | (df["expense_ratio_pct"] > 2.5)
    ]
    if len(anomalies):
        print(f"  expense_ratio out of [0.1, 2.5]: {len(anomalies)} rows")
        print(anomalies[["amfi_code", "scheme_name", "expense_ratio_pct"]])
    else:
        print("  expense_ratio: all within [0.1, 2.5] — OK")

    return_anomalies = df[df[return_cols].isnull().any(axis=1)]
    if len(return_anomalies):
        print(f"  non-numeric return values flagged: {len(return_anomalies)} rows")
    else:
        print("  return values: all numeric — OK")

    df = df.drop_duplicates()
    print(f"  shape: {df.shape}")
    return save(df, "07_scheme_performance")


# ── 08 investor_transactions ───────────────────────────────────────────────

def clean_investor_transactions():
    print("\n[08] investor_transactions")
    df = pd.read_csv(f"{RAW}/08_investor_transactions.csv")
    df = parse_date_col(df, "transaction_date")

    # Standardise transaction_type to consistent casing
    type_map = {"SIP": "SIP", "Lumpsum": "Lumpsum", "Redemption": "Redemption"}
    df["transaction_type"] = df["transaction_type"].str.strip().map(type_map)

    # Validate amount > 0
    neg = df[df["amount_inr"] <= 0]
    if len(neg):
        print(f"  invalid amount_inr <= 0: {len(neg)} rows — dropping")
        df = df[df["amount_inr"] > 0]
    else:
        print("  amount_inr: all > 0 — OK")

    # Validate KYC enum
    valid_kyc = {"Verified", "Pending"}
    bad_kyc = df[~df["kyc_status"].isin(valid_kyc)]
    if len(bad_kyc):
        print(f"  unexpected kyc_status values: {bad_kyc['kyc_status'].unique()}")
    else:
        print("  kyc_status: ['Verified', 'Pending'] — OK")

    df = df.drop_duplicates()
    print(f"  shape: {df.shape}")
    return save(df, "08_investor_transactions")


# ── 09 portfolio_holdings ──────────────────────────────────────────────────

def clean_portfolio_holdings():
    print("\n[09] portfolio_holdings")
    df = pd.read_csv(f"{RAW}/09_portfolio_holdings.csv")
    df = parse_date_col(df, "portfolio_date")
    df = df.drop_duplicates()
    print(f"  shape: {df.shape}")
    return save(df, "09_portfolio_holdings")


# ── 10 benchmark_indices ───────────────────────────────────────────────────

def clean_benchmark_indices():
    print("\n[10] benchmark_indices")
    df = pd.read_csv(f"{RAW}/10_benchmark_indices.csv")
    df = parse_date_col(df, "date")
    df = df.drop_duplicates(subset=["date", "index_name"])
    df = df.sort_values(["index_name", "date"]).reset_index(drop=True)
    print(f"  shape: {df.shape}")
    return save(df, "10_benchmark_indices")


# ── main ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    clean_fund_master()
    clean_nav_history()
    clean_aum_by_fund_house()
    clean_monthly_sip_inflows()
    clean_category_inflows()
    clean_industry_folio_count()
    clean_scheme_performance()
    clean_investor_transactions()
    clean_portfolio_holdings()
    clean_benchmark_indices()
    print("\nAll 10 files cleaned and saved to data/processed/")
