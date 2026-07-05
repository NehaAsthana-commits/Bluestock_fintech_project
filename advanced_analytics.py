"""
Day 5 -- Advanced Analytics + Risk Metrics
Computes: VaR/CVaR, Rolling Sharpe, Investor Cohort Analysis,
SIP Continuity, Fund Recommender, Sector HHI Concentration.
Outputs: var_cvar_report.csv, rolling_sharpe_chart.png
"""
import os
import warnings
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import pandas as pd
import numpy as np

warnings.filterwarnings("ignore")

PROC   = "data/processed"
RAW    = "data/raw"
CHARTS = "reports/charts"
os.makedirs(CHARTS, exist_ok=True)

RF_DAILY     = 0.065 / 252
TRADING_DAYS = 252

BLUE   = "#2563EB"; ORANGE = "#F97316"; GREEN  = "#16A34A"
RED    = "#DC2626"; PURPLE = "#7C3AED"; GREY   = "#6B7280"; TEAL   = "#0D9488"

sns.set_theme(style="whitegrid", font_scale=1.1)


# ==========================================================================
# Load data
# ==========================================================================
print("Loading data...")
fm    = pd.read_csv(f"{PROC}/01_fund_master.csv")
nav   = pd.read_csv(f"{RAW}/02_nav_history.csv", parse_dates=["date"])
txn   = pd.read_csv(f"{PROC}/08_investor_transactions.csv",
                    parse_dates=["transaction_date"])
hld   = pd.read_csv(f"{PROC}/09_portfolio_holdings.csv")
score = pd.read_csv("fund_scorecard.csv")

nav   = nav.sort_values(["amfi_code", "date"]).reset_index(drop=True)
nav["daily_return"] = nav.groupby("amfi_code")["nav"].pct_change()
returns_wide = (nav.dropna(subset=["daily_return"])
                   .pivot(index="date", columns="amfi_code", values="daily_return"))


# ==========================================================================
# 1. Historical VaR (95%) and CVaR for all 40 schemes
# ==========================================================================
print("\n[1] VaR (95%) and CVaR...")

var_rows = []
for code in returns_wide.columns:
    r = returns_wide[code].dropna()
    if len(r) < 30:
        continue
    var_95   = np.percentile(r, 5)           # 5th percentile = 95% VaR
    cvar_95  = r[r <= var_95].mean()          # CVaR = mean of returns below VaR
    var_rows.append({
        "amfi_code"  : code,
        "var_95_pct" : round(var_95  * 100, 4),
        "cvar_95_pct": round(cvar_95 * 100, 4),
        "n_days"     : len(r),
    })

var_df = pd.DataFrame(var_rows)
var_report = (var_df
              .merge(fm[["amfi_code", "fund_house", "scheme_name",
                         "category", "sub_category", "plan"]], on="amfi_code")
              .sort_values("var_95_pct"))   # most negative = highest risk

var_report.to_csv("var_cvar_report.csv", index=False)
print(f"  Saved var_cvar_report.csv ({len(var_report)} rows)")
print(f"  Worst VaR  : {var_report.iloc[0]['scheme_name'][:50]}  "
      f"VaR={var_report.iloc[0]['var_95_pct']:.2f}%")
print(f"  Best  VaR  : {var_report.iloc[-1]['scheme_name'][:50]}  "
      f"VaR={var_report.iloc[-1]['var_95_pct']:.2f}%")
print(f"  Avg CVaR   : {var_report['cvar_95_pct'].mean():.2f}%")


# ==========================================================================
# 2. Rolling 90-day Sharpe -- plot for top 5 equity funds by scorecard
# ==========================================================================
print("\n[2] Rolling 90-day Sharpe (top 5 equity funds)...")

top5_codes = (score[score["category"] == "Equity"]
              .head(5)[["amfi_code", "scheme_name"]].values)

fig, ax = plt.subplots(figsize=(14, 6))
colors = [BLUE, ORANGE, GREEN, PURPLE, TEAL]

for (code, name), color in zip(top5_codes, colors):
    r = returns_wide[code].dropna()
    roll_mean = r.rolling(90).mean()
    roll_std  = r.rolling(90).std()
    roll_sharpe = ((roll_mean - RF_DAILY) / roll_std) * np.sqrt(TRADING_DAYS)
    label = name.split(" - ")[0].strip()
    ax.plot(roll_sharpe.index, roll_sharpe.values,
            label=label, color=color, linewidth=1.8)

ax.axhline(0,   color=GREY, linewidth=1,   linestyle="--", alpha=0.7)
ax.axhline(0.5, color=GREEN, linewidth=0.8, linestyle=":",  alpha=0.6, label="Sharpe=0.5 threshold")

# Shade 2024 correction period
ax.axvspan(pd.Timestamp("2024-01-01"), pd.Timestamp("2024-06-30"),
           alpha=0.08, color=RED, label="2024 Correction")

ax.set_title("Rolling 90-Day Sharpe Ratio -- Top 5 Equity Funds (2022-2026)",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Date", fontsize=11)
ax.set_ylabel("Rolling Sharpe Ratio", fontsize=11)
ax.legend(loc="lower right", fontsize=9, ncol=2)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(f"{CHARTS}/19_rolling_sharpe.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"  Saved {CHARTS}/19_rolling_sharpe.png")


# ==========================================================================
# 3. Investor Cohort Analysis -- group by first transaction year
# ==========================================================================
print("\n[3] Investor cohort analysis...")

cohort_year = (txn.groupby("investor_id")["transaction_date"]
               .min().dt.year.rename("cohort_year"))
txn = txn.join(cohort_year, on="investor_id")
sip_txn = txn[txn["transaction_type"] == "SIP"]

# Avg SIP amount per cohort
cohort_sip_avg = (sip_txn.groupby("cohort_year")["amount_inr"]
                  .mean().round(0).rename("avg_sip_amount"))

# Total invested per cohort
cohort_total = (txn[txn["transaction_type"].isin(["SIP", "Lumpsum"])]
                .groupby("cohort_year")["amount_inr"]
                .sum().rename("total_invested_inr"))

# Top fund per cohort (by transaction count)
top_fund_per_cohort = (txn.groupby(["cohort_year", "amfi_code"])
                       .size().reset_index(name="count")
                       .sort_values("count", ascending=False)
                       .drop_duplicates("cohort_year")
                       .merge(fm[["amfi_code", "scheme_name"]], on="amfi_code")
                       [["cohort_year", "scheme_name", "count"]]
                       .rename(columns={"scheme_name": "top_fund", "count": "top_fund_txn_count"}))

cohort_report = (cohort_sip_avg.reset_index()
                 .merge(cohort_total.reset_index(), on="cohort_year")
                 .merge(top_fund_per_cohort, on="cohort_year"))

print(cohort_report.to_string(index=False))


# ==========================================================================
# 4. SIP Continuity Analysis
# ==========================================================================
print("\n[4] SIP continuity analysis...")

sip_all = txn[txn["transaction_type"] == "SIP"].sort_values(
    ["investor_id", "transaction_date"])

# Investors with 6+ SIP transactions
sip_counts = sip_all.groupby("investor_id").size()
eligible    = sip_counts[sip_counts >= 6].index
sip_elig    = sip_all[sip_all["investor_id"].isin(eligible)].copy()

# Avg gap between consecutive SIP dates per investor
sip_elig["gap_days"] = sip_elig.groupby("investor_id")["transaction_date"].diff().dt.days
avg_gap = (sip_elig.groupby("investor_id")["gap_days"]
           .mean().round(1).rename("avg_gap_days"))

# Flag at-risk (avg gap > 35 days)
gap_df = avg_gap.reset_index()
gap_df["at_risk"] = gap_df["avg_gap_days"] > 35

total_eligible = len(gap_df)
at_risk_count  = gap_df["at_risk"].sum()
continuity_rate = 100 * (1 - at_risk_count / total_eligible)

print(f"  Investors with 6+ SIP transactions : {total_eligible:,}")
print(f"  At-risk (avg gap > 35 days)         : {at_risk_count:,} "
      f"({100*at_risk_count/total_eligible:.1f}%)")
print(f"  SIP continuity rate                 : {continuity_rate:.1f}%")
print(f"  Avg gap -- median: {gap_df['avg_gap_days'].median():.1f}d  "
      f"mean: {gap_df['avg_gap_days'].mean():.1f}d")

# Save
gap_df = gap_df.merge(
    txn[["investor_id","state","city_tier","age_group"]].drop_duplicates("investor_id"),
    on="investor_id", how="left")
gap_df.to_csv("sip_continuity_report.csv", index=False)
print("  Saved sip_continuity_report.csv")


# ==========================================================================
# 5. Sector HHI Concentration per equity fund
# ==========================================================================
print("\n[5] Sector HHI concentration...")

eq_codes = fm[fm["category"] == "Equity"]["amfi_code"].tolist()
hld_eq   = hld[hld["amfi_code"].isin(eq_codes)].copy()

def hhi(weights):
    """Herfindahl-Hirschman Index = sum of squared market shares."""
    w = weights / weights.sum()    # normalise to 100%
    return (w ** 2).sum() * 10000  # scale: max 10000 (monopoly), min ~1111 (9 equal)

hhi_rows = []
for code, grp in hld_eq.groupby("amfi_code"):
    # Aggregate by sector
    sector_wt = grp.groupby("sector")["weight_pct"].sum()
    hhi_val   = hhi(sector_wt)
    top_sector = sector_wt.idxmax()
    hhi_rows.append({
        "amfi_code"  : code,
        "hhi_score"  : round(hhi_val, 1),
        "top_sector" : top_sector,
        "n_sectors"  : sector_wt.nunique(),
    })

hhi_df = (pd.DataFrame(hhi_rows)
          .merge(fm[["amfi_code", "scheme_name", "sub_category"]], on="amfi_code")
          .sort_values("hhi_score", ascending=False))

print(f"  HHI range: {hhi_df['hhi_score'].min():.0f} -- {hhi_df['hhi_score'].max():.0f}")
print(f"  Most concentrated: {hhi_df.iloc[0]['scheme_name'][:50]}  HHI={hhi_df.iloc[0]['hhi_score']:.0f}")
print(f"  Most diversified : {hhi_df.iloc[-1]['scheme_name'][:50]}  HHI={hhi_df.iloc[-1]['hhi_score']:.0f}")

# HHI bar chart
fig2, ax2 = plt.subplots(figsize=(13, 7))
short = hhi_df["scheme_name"].str.extract(r"^([^-]+)")[0].str.strip().str[:28]
bar_colors = [RED if h > 2500 else (ORANGE if h > 1800 else GREEN)
              for h in hhi_df["hhi_score"]]
ax2.barh(short[::-1], hhi_df["hhi_score"][::-1], color=bar_colors[::-1], height=0.7)
ax2.axvline(2500, color=RED,    linestyle="--", linewidth=1, label="HHI=2500 (concentrated)")
ax2.axvline(1800, color=ORANGE, linestyle=":",  linewidth=1, label="HHI=1800 (moderate)")
ax2.set_xlabel("HHI Score (higher = more concentrated)", fontsize=11)
ax2.set_title("Sector HHI Concentration -- Equity Funds\n"
              "(Low HHI = diversified, High HHI = concentrated)",
              fontsize=12, fontweight="bold")
ax2.legend(fontsize=9)
ax2.set_xlim(0, hhi_df["hhi_score"].max() * 1.15)
for i, (h, name) in enumerate(zip(hhi_df["hhi_score"][::-1], short[::-1])):
    ax2.text(h + 20, i, f"{h:.0f}", va="center", fontsize=8)
plt.tight_layout()
plt.savefig(f"{CHARTS}/20_sector_hhi.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"  Saved {CHARTS}/20_sector_hhi.png")


# ==========================================================================
# 6. VaR / CVaR summary chart
# ==========================================================================
print("\n[6] VaR/CVaR summary chart...")

# Merge with scorecard for category
var_plot = var_report.copy()
fig3, axes = plt.subplots(1, 2, figsize=(15, 7))

# Left: VaR bar sorted worst-to-best
short_v = var_plot["scheme_name"].str.extract(r"^([^-]+)")[0].str.strip().str[:25]
bar_c   = [RED if v < -2 else (ORANGE if v < -1.5 else GREEN) for v in var_plot["var_95_pct"]]
axes[0].barh(short_v, var_plot["var_95_pct"], color=bar_c, height=0.65)
axes[0].set_xlabel("95% VaR (%/day)", fontsize=11)
axes[0].set_title("Daily VaR (95%) -- All 40 Funds", fontsize=12, fontweight="bold")
axes[0].axvline(-2, color=RED, linestyle="--", linewidth=1, label="VaR = -2%")
axes[0].legend(fontsize=9)

# Right: VaR vs CVaR scatter by category
colors_cat = {"Equity": BLUE, "Debt": ORANGE}
for cat, grp in var_plot.groupby("category"):
    axes[1].scatter(grp["var_95_pct"], grp["cvar_95_pct"],
                    color=colors_cat.get(cat, GREY), label=cat, s=60, alpha=0.8)
axes[1].set_xlabel("VaR 95% (%/day)", fontsize=11)
axes[1].set_ylabel("CVaR 95% (%/day)", fontsize=11)
axes[1].set_title("VaR vs CVaR by Category", fontsize=12, fontweight="bold")
axes[1].legend(fontsize=10)
# y=x reference line
lim = [min(var_plot["var_95_pct"].min(), var_plot["cvar_95_pct"].min()) - 0.2,
       max(var_plot["var_95_pct"].max(), var_plot["cvar_95_pct"].max()) + 0.2]
axes[1].plot(lim, lim, color=GREY, linestyle="--", linewidth=1, alpha=0.5, label="y=x")
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f"{CHARTS}/21_var_cvar_summary.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"  Saved {CHARTS}/21_var_cvar_summary.png")


# ==========================================================================
# Final summary
# ==========================================================================
print("\n" + "=" * 60)
print("Day 5 -- Advanced Analytics Summary")
print("=" * 60)
print(f"VaR/CVaR  : {len(var_report)} funds computed, saved var_cvar_report.csv")
print(f"Rolling Sharpe: 5 equity funds, saved 19_rolling_sharpe.png")
print(f"Cohorts   : {txn['cohort_year'].nunique()} cohorts analysed")
print(f"SIP Continuity: {total_eligible:,} eligible | {at_risk_count:,} at-risk "
      f"({100*at_risk_count/total_eligible:.1f}%)")
print(f"HHI       : {len(hhi_df)} equity funds scored")
print(f"Charts    : 19_rolling_sharpe, 20_sector_hhi, 21_var_cvar_summary")
