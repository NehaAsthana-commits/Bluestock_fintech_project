"""
Day 2 — Database Loader
Loads all cleaned CSVs into bluestock_mf.db (SQLite) using SQLAlchemy.
Applies the star schema and verifies row counts match source CSVs.
"""
import pandas as pd
from sqlalchemy import create_engine, text

DB_PATH = "bluestock_mf.db"
PROC = "data/processed"

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)


# ── Build dim_date from all dates in cleaned nav_history ───────────────────

def build_dim_date(nav_df):
    dates = nav_df["date"].dropna().unique()
    rows = []
    for d in pd.to_datetime(dates):
        rows.append({
            "date":       d.strftime("%Y-%m-%d"),
            "year":       d.year,
            "quarter":    d.quarter,
            "month":      d.month,
            "month_name": d.strftime("%B"),
            "week":       int(d.strftime("%W")),
            "day":        d.day,
            "weekday":    d.strftime("%A"),
            "is_weekend": int(d.weekday() >= 5),
        })
    return pd.DataFrame(rows).drop_duplicates(subset="date").sort_values("date")


# ── Load helpers ───────────────────────────────────────────────────────────

def load(df, table, source_csv_rows):
    df.to_sql(table, engine, if_exists="replace", index=False)
    with engine.connect() as conn:
        db_rows = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
    status = "OK" if db_rows == source_csv_rows else f"MISMATCH (expected {source_csv_rows})"
    print(f"  {table:25s}: {db_rows:>8,} rows  [{status}]")


def apply_schema():
    schema = open("sql/schema.sql").read()
    with engine.connect() as conn:
        for stmt in schema.split(";"):
            stmt = stmt.strip()
            if stmt:
                conn.execute(text(stmt))
        conn.commit()


# ── Main ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Applying schema...")
    apply_schema()

    # Load dimension tables first
    print("\nLoading dimension tables:")
    fund = pd.read_csv(f"{PROC}/01_fund_master.csv")
    load(fund, "dim_fund", len(fund))

    nav = pd.read_csv(f"{PROC}/02_nav_history.csv")
    dim_date = build_dim_date(nav)
    load(dim_date, "dim_date", len(dim_date))

    # Load fact tables
    print("\nLoading fact tables:")
    load(nav[["amfi_code", "date", "nav"]], "fact_nav", len(nav))

    txn = pd.read_csv(f"{PROC}/08_investor_transactions.csv",
                      dtype={"transaction_date": str})
    txn_mapped = txn.rename(columns={"transaction_date": "transaction_date"})
    load(txn_mapped, "fact_transactions", len(txn))

    perf = pd.read_csv(f"{PROC}/07_scheme_performance.csv")
    perf_cols = [
        "amfi_code", "return_1yr_pct", "return_3yr_pct", "return_5yr_pct",
        "benchmark_3yr_pct", "alpha", "beta", "sharpe_ratio", "sortino_ratio",
        "std_dev_ann_pct", "max_drawdown_pct", "aum_crore", "expense_ratio_pct",
        "morningstar_rating", "risk_grade",
    ]
    load(perf[perf_cols], "fact_performance", len(perf))

    aum = pd.read_csv(f"{PROC}/03_aum_by_fund_house.csv")
    load(aum, "fact_aum", len(aum))

    print(f"\nDatabase written to {DB_PATH}")

    # Summary
    print("\nRow count summary:")
    tables = ["dim_fund", "dim_date", "fact_nav", "fact_transactions",
              "fact_performance", "fact_aum"]
    with engine.connect() as conn:
        for t in tables:
            n = conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
            print(f"  {t:25s}: {n:>8,}")
