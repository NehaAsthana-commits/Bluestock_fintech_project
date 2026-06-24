"""
Day 1 — Data Ingestion
Loads all 10 raw CSVs, inspects shape/dtypes/head, explores the fund master,
and validates AMFI scheme codes across files.
"""
import pandas as pd

RAW_DIR = "data/raw"

FILES = [
    "01_fund_master.csv",
    "02_nav_history.csv",
    "03_aum_by_fund_house.csv",
    "04_monthly_sip_inflows.csv",
    "05_category_inflows.csv",
    "06_industry_folio_count.csv",
    "07_scheme_performance.csv",
    "08_investor_transactions.csv",
    "09_portfolio_holdings.csv",
    "10_benchmark_indices.csv",
]


def load_all():
    frames = {}
    for filename in FILES:
        name = filename.split("_", 1)[1].replace(".csv", "")
        df = pd.read_csv(f"{RAW_DIR}/{filename}")
        frames[name] = df

        print(f"\n=== {filename} ===")
        print(f"Shape: {df.shape}")
        print("Dtypes:")
        print(df.dtypes)
        print("Head:")
        print(df.head())

    return frames


def explore_fund_master(fund_master):
    print("\n=== Fund Master Exploration ===")
    print(f"Unique fund houses ({fund_master['fund_house'].nunique()}):")
    print(sorted(fund_master["fund_house"].unique()))

    print(f"\nUnique categories ({fund_master['category'].nunique()}):")
    print(sorted(fund_master["category"].unique()))

    print(f"\nUnique sub-categories ({fund_master['sub_category'].nunique()}):")
    print(sorted(fund_master["sub_category"].unique()))

    print(f"\nUnique risk categories ({fund_master['risk_category'].nunique()}):")
    print(sorted(fund_master["risk_category"].unique()))

    print("\nAMFI code structure: numeric scheme codes assigned by AMFI; "
          "Regular and Direct plans of the same scheme get distinct codes "
          "(e.g. 119551 Regular / 119552 Direct for SBI Bluechip Fund).")


def validate_amfi_codes(fund_master, nav_history, transactions, holdings):
    print("\n=== AMFI Code Validation ===")
    master_codes = set(fund_master["amfi_code"])

    nav_codes = set(nav_history["amfi_code"])
    missing_in_nav = master_codes - nav_codes
    extra_in_nav = nav_codes - master_codes
    print(f"fund_master codes: {len(master_codes)} | nav_history codes: {len(nav_codes)}")
    print(f"fund_master codes missing from nav_history: {len(missing_in_nav)} {missing_in_nav or ''}")
    print(f"nav_history codes not in fund_master: {len(extra_in_nav)} {extra_in_nav or ''}")

    txn_codes = set(transactions["amfi_code"])
    invalid_txn = txn_codes - master_codes
    print(f"\ninvestor_transactions codes: {len(txn_codes)} | invalid (not in fund_master): {len(invalid_txn)}")

    holding_codes = set(holdings["amfi_code"])
    invalid_holdings = holding_codes - master_codes
    funds_without_holdings = master_codes - holding_codes
    print(f"portfolio_holdings codes: {len(holding_codes)} | invalid (not in fund_master): {len(invalid_holdings)}")
    print(f"funds in fund_master with no holdings data: {len(funds_without_holdings)}")


def write_quality_summary(frames):
    lines = ["# Day 1 Data Quality Summary\n"]
    for name, df in frames.items():
        lines.append(f"- **{name}**: {df.shape[0]} rows x {df.shape[1]} cols, "
                      f"{df.isna().sum().sum()} total missing values")
    with open("notebooks/day1_quality_summary.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\nWrote notebooks/day1_quality_summary.md")


if __name__ == "__main__":
    frames = load_all()
    explore_fund_master(frames["fund_master"])
    validate_amfi_codes(
        frames["fund_master"],
        frames["nav_history"],
        frames["investor_transactions"],
        frames["portfolio_holdings"],
    )
    write_quality_summary(frames)
