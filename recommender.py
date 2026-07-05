"""
Simple Fund Recommender
Input : risk appetite -- Low | Moderate | High
Output: top 3 funds by Sharpe ratio within matching risk_grade

Usage:
    python recommender.py
    python recommender.py --risk Low
    python recommender.py --risk Moderate
    python recommender.py --risk High
"""
import argparse
import pandas as pd

# Risk appetite -> fund master risk_category mapping
RISK_MAP = {
    "Low"      : ["Low"],
    "Moderate" : ["Moderate", "Moderately High"],
    "High"     : ["High", "Very High"],
}


def recommend(risk_appetite: str, top_n: int = 3) -> pd.DataFrame:
    fm    = pd.read_csv("data/processed/01_fund_master.csv")
    score = pd.read_csv("fund_scorecard.csv")

    # score already has expense_ratio_pct; merge only risk_category from fm
    merged = score.merge(fm[["amfi_code", "risk_category"]], on="amfi_code")

    # Filter by risk grade
    risk_grades = RISK_MAP.get(risk_appetite)
    if risk_grades is None:
        raise ValueError(f"risk_appetite must be one of: {list(RISK_MAP.keys())}")

    filtered = merged[merged["risk_category"].isin(risk_grades)].copy()
    if filtered.empty:
        return pd.DataFrame()

    top = (filtered
           .sort_values("sharpe_ratio", ascending=False)
           .head(top_n)
           [["scheme_name", "fund_house", "plan", "risk_category",
             "sharpe_ratio", "cagr_3yr", "max_drawdown_pct",
             "expense_ratio_pct", "fund_score"]])

    top["cagr_3yr_pct"]       = (top["cagr_3yr"] * 100).round(2)
    top["max_drawdown_pct"]   = top["max_drawdown_pct"].round(2)
    top["sharpe_ratio"]       = top["sharpe_ratio"].round(3)

    return top.reset_index(drop=True)


def print_recommendation(risk_appetite: str) -> None:
    print(f"\nFund Recommendation -- Risk Appetite: {risk_appetite}")
    print("=" * 70)

    df = recommend(risk_appetite)
    if df.empty:
        print("No funds found for this risk appetite.")
        return

    display_cols = ["scheme_name", "plan", "risk_category",
                    "sharpe_ratio", "cagr_3yr_pct", "max_drawdown_pct", "expense_ratio_pct"]

    for i, row in df.iterrows():
        print(f"\n  Rank #{i+1}")
        print(f"    Fund     : {row['scheme_name']}")
        print(f"    House    : {row['fund_house']}")
        print(f"    Plan     : {row['plan']}")
        print(f"    Risk     : {row['risk_category']}")
        print(f"    Sharpe   : {row['sharpe_ratio']:.3f}")
        print(f"    3yr CAGR : {row['cagr_3yr_pct']:.2f}%")
        print(f"    Max DD   : {row['max_drawdown_pct']:.2f}%")
        print(f"    Exp Ratio: {row['expense_ratio_pct']:.2f}%")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mutual Fund Recommender")
    parser.add_argument("--risk", choices=["Low", "Moderate", "High"],
                        default=None, help="Investor risk appetite")
    args = parser.parse_args()

    if args.risk:
        print_recommendation(args.risk)
    else:
        # Print all three
        for appetite in ["Low", "Moderate", "High"]:
            print_recommendation(appetite)
