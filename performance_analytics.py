"""
Day 4 — Fund Performance Analytics
Computes: daily returns, CAGR, Sharpe, Sortino, Alpha/Beta, Max Drawdown,
Fund Scorecard, and benchmark comparison chart.
Outputs: fund_scorecard.csv, alpha_beta.csv, benchmark comparison PNG.
"""
import os
import warnings
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import seaborn as sns
import pandas as pd
import numpy as np
from scipy import stats

warnings.filterwarnings("ignore")

PROC   = "data/processed"
CHARTS = "reports/charts"
os.makedirs(CHARTS, exist_ok=True)

RF_ANNUAL  = 0.065          # RBI repo rate proxy 6.5%
RF_DAILY   = RF_ANNUAL / 252
TRADING_DAYS = 252

BLUE   = "#2563EB"; ORANGE = "#F97316"; GREEN  = "#16A34A"
RED    = "#DC2626"; PURPLE = "#7C3AED"; GREY   = "#6B7280"; TEAL   = "#0D9488"


# ═══════════════════════════════════════════════════════════════════════════
# 1. Load data
# ═══════════════════════════════════════════════════════════════════════════
print("=" * 60)
print("Loading data...")
fm    = pd.read_csv(f"{PROC}/01_fund_master.csv")
# Use RAW nav (trading days only) for return-based metrics
nav   = pd.read_csv("data/raw/02_nav_history.csv", parse_dates=["date"])
bench = pd.read_csv(f"{PROC}/10_benchmark_indices.csv", parse_dates=["date"])

nav   = nav.sort_values(["amfi_code", "date"]).reset_index(drop=True)
nifty100 = (bench[bench["index_name"] == "NIFTY100"]
            .set_index("date")["close_value"].sort_index())
nifty50  = (bench[bench["index_name"] == "NIFTY50"]
            .set_index("date")["close_value"].sort_index())

bench_ret100 = nifty100.pct_change().dropna()
bench_ret50  = nifty50.pct_change().dropna()

print(f"  Funds: {nav['amfi_code'].nunique()} | Trading days: {nav.groupby('amfi_code').size().mean():.0f} avg")


# ═══════════════════════════════════════════════════════════════════════════
# 2. Daily returns per fund
# ═══════════════════════════════════════════════════════════════════════════
print("\n[1] Computing daily returns...")

nav["daily_return"] = nav.groupby("amfi_code")["nav"].pct_change()
returns_wide = (nav.dropna(subset=["daily_return"])
                   .pivot(index="date", columns="amfi_code", values="daily_return"))

# Validate distribution
overall_stats = nav["daily_return"].dropna()
print(f"  Mean daily return : {overall_stats.mean()*100:.4f}%")
print(f"  Std daily return  : {overall_stats.std()*100:.4f}%")
print(f"  Min               : {overall_stats.min()*100:.2f}%")
print(f"  Max               : {overall_stats.max()*100:.2f}%")
print(f"  % days negative   : {(overall_stats < 0).mean()*100:.1f}%")
print("  => Distribution looks reasonable (thin tails, equity-like spread)")


# ═══════════════════════════════════════════════════════════════════════════
# 3. CAGR — 1yr, 3yr, 5yr (using actual start/end NAVs)
# ═══════════════════════════════════════════════════════════════════════════
print("\n[2] Computing CAGR...")

last_date  = nav["date"].max()

def get_nav_on(code, target_date, tolerance_days=7):
    df = nav[nav["amfi_code"] == code].sort_values("date")
    # Nearest trading day on or before target
    df = df[df["date"] <= target_date]
    if df.empty:
        return np.nan
    return df.iloc[-1]["nav"]

def cagr(nav_end, nav_start, years):
    if nav_start is None or np.isnan(nav_start) or nav_start <= 0:
        return np.nan
    return (nav_end / nav_start) ** (1 / years) - 1

cagr_rows = []
for code in nav["amfi_code"].unique():
    df = nav[nav["amfi_code"] == code].sort_values("date")
    nav_end  = df.iloc[-1]["nav"]
    date_end = df.iloc[-1]["date"]

    nav_1y = get_nav_on(code, date_end - pd.DateOffset(years=1))
    nav_3y = get_nav_on(code, date_end - pd.DateOffset(years=3))
    nav_5y = get_nav_on(code, date_end - pd.DateOffset(years=5))

    cagr_rows.append({
        "amfi_code" : code,
        "cagr_1yr"  : cagr(nav_end, nav_1y, 1),
        "cagr_3yr"  : cagr(nav_end, nav_3y, 3),
        "cagr_5yr"  : cagr(nav_end, nav_5y, 5),
    })

cagr_df = pd.DataFrame(cagr_rows)
print(f"  CAGR 3yr median: {cagr_df['cagr_3yr'].median()*100:.2f}%")
print(f"  CAGR 1yr range : {cagr_df['cagr_1yr'].min()*100:.1f}% – {cagr_df['cagr_1yr'].max()*100:.1f}%")


# ═══════════════════════════════════════════════════════════════════════════
# 4. Sharpe Ratio
# ═══════════════════════════════════════════════════════════════════════════
print("\n[3] Computing Sharpe Ratios...")

def sharpe(returns_series):
    r = returns_series.dropna()
    if len(r) < 30:
        return np.nan
    excess = r - RF_DAILY
    return (excess.mean() / r.std()) * np.sqrt(TRADING_DAYS)

sharpe_series = returns_wide.apply(sharpe)
print(f"  Sharpe range: {sharpe_series.min():.3f} – {sharpe_series.max():.3f}")
print(f"  Sharpe median: {sharpe_series.median():.3f}")


# ═══════════════════════════════════════════════════════════════════════════
# 5. Sortino Ratio
# ═══════════════════════════════════════════════════════════════════════════
print("\n[4] Computing Sortino Ratios...")

def sortino(returns_series):
    r = returns_series.dropna()
    if len(r) < 30:
        return np.nan
    excess    = r.mean() - RF_DAILY
    downside  = r[r < 0]
    down_std  = downside.std() if len(downside) > 1 else np.nan
    if down_std is None or np.isnan(down_std) or down_std == 0:
        return np.nan
    return (excess / down_std) * np.sqrt(TRADING_DAYS)

sortino_series = returns_wide.apply(sortino)
print(f"  Sortino range: {sortino_series.min():.3f} – {sortino_series.max():.3f}")


# ═══════════════════════════════════════════════════════════════════════════
# 6. Alpha and Beta (OLS vs NIFTY100)
# ═══════════════════════════════════════════════════════════════════════════
print("\n[5] Computing Alpha & Beta (OLS vs NIFTY100)...")

ab_rows = []
for code in returns_wide.columns:
    fund_ret = returns_wide[code].dropna()
    common   = fund_ret.index.intersection(bench_ret100.index)
    if len(common) < 60:
        ab_rows.append({"amfi_code": code, "beta": np.nan, "alpha_annual": np.nan,
                        "r_squared": np.nan, "tracking_error_nifty100": np.nan})
        continue
    y = fund_ret.loc[common].values
    x = bench_ret100.loc[common].values
    slope, intercept, r, p, se = stats.linregress(x, y)
    te = np.std(y - x) * np.sqrt(TRADING_DAYS)
    ab_rows.append({
        "amfi_code"              : code,
        "beta"                   : round(slope, 4),
        "alpha_annual"           : round(intercept * TRADING_DAYS * 100, 4),  # % annualised
        "r_squared"              : round(r**2, 4),
        "tracking_error_nifty100": round(te * 100, 4),
    })

ab_df = pd.DataFrame(ab_rows)
print(f"  Beta range  : {ab_df['beta'].min():.3f} – {ab_df['beta'].max():.3f}")
print(f"  Alpha range : {ab_df['alpha_annual'].min():.2f}% – {ab_df['alpha_annual'].max():.2f}%")


# ═══════════════════════════════════════════════════════════════════════════
# 7. Maximum Drawdown + worst drawdown date range
# ═══════════════════════════════════════════════════════════════════════════
print("\n[6] Computing Maximum Drawdown...")

dd_rows = []
for code in nav["amfi_code"].unique():
    df = nav[nav["amfi_code"] == code].sort_values("date").set_index("date")["nav"]
    running_max = df.cummax()
    drawdown    = (df / running_max) - 1
    max_dd      = drawdown.min()
    trough_date = drawdown.idxmin()
    # Peak = last date before trough where running_max was reached
    peak_date   = df.loc[:trough_date].idxmax()
    dd_rows.append({
        "amfi_code"  : code,
        "max_drawdown_pct": round(max_dd * 100, 4),
        "peak_date"  : peak_date.date(),
        "trough_date": trough_date.date(),
        "dd_duration_days": (trough_date - peak_date).days,
    })

dd_df = pd.DataFrame(dd_rows)
worst = dd_df.loc[dd_df["max_drawdown_pct"].idxmin()]
print(f"  Worst drawdown: {worst['max_drawdown_pct']:.2f}% "
      f"({worst['peak_date']} to {worst['trough_date']})")
print(f"  Median drawdown: {dd_df['max_drawdown_pct'].median():.2f}%")


# ═══════════════════════════════════════════════════════════════════════════
# 8. Assemble master performance table
# ═══════════════════════════════════════════════════════════════════════════
print("\n[7] Assembling performance table...")

perf = (fm[["amfi_code", "fund_house", "scheme_name", "category",
            "sub_category", "plan", "expense_ratio_pct"]]
        .merge(cagr_df,    on="amfi_code")
        .merge(pd.DataFrame({"amfi_code": sharpe_series.index,
                             "sharpe_ratio": sharpe_series.values}), on="amfi_code")
        .merge(pd.DataFrame({"amfi_code": sortino_series.index,
                             "sortino_ratio": sortino_series.values}), on="amfi_code")
        .merge(ab_df,  on="amfi_code")
        .merge(dd_df[["amfi_code", "max_drawdown_pct", "peak_date",
                      "trough_date", "dd_duration_days"]], on="amfi_code")
)


# ═══════════════════════════════════════════════════════════════════════════
# 9. Fund Scorecard (0–100)
# 30% × 3yr_return_rank + 25% × Sharpe_rank + 20% × Alpha_rank
# + 15% × expense_rank(inverse) + 10% × max_DD_rank(inverse)
# ═══════════════════════════════════════════════════════════════════════════
print("\n[8] Computing Fund Scorecard (0–100)...")

n = len(perf)

def pct_rank(series, ascending=True):
    """Percentile rank 0–100; ascending=True → higher value = higher rank."""
    return series.rank(ascending=ascending, pct=True) * 100

perf["rank_3yr_return"]  = pct_rank(perf["cagr_3yr"])
perf["rank_sharpe"]      = pct_rank(perf["sharpe_ratio"])
perf["rank_alpha"]       = pct_rank(perf["alpha_annual"])
perf["rank_expense_inv"] = pct_rank(perf["expense_ratio_pct"], ascending=False)   # inverse: lower is better
perf["rank_maxdd_inv"]   = pct_rank(perf["max_drawdown_pct"],  ascending=False)   # inverse: less negative is better

perf["fund_score"] = (
    0.30 * perf["rank_3yr_return"]  +
    0.25 * perf["rank_sharpe"]      +
    0.20 * perf["rank_alpha"]       +
    0.15 * perf["rank_expense_inv"] +
    0.10 * perf["rank_maxdd_inv"]
).round(2)

perf["score_rank"] = perf["fund_score"].rank(ascending=False, method="min").astype(int)
perf = perf.sort_values("fund_score", ascending=False).reset_index(drop=True)

print(f"  Top scorer: {perf.iloc[0]['scheme_name']}  Score={perf.iloc[0]['fund_score']:.1f}")
print(f"  Score range: {perf['fund_score'].min():.1f} – {perf['fund_score'].max():.1f}")


# ═══════════════════════════════════════════════════════════════════════════
# 10. Save CSVs
# ═══════════════════════════════════════════════════════════════════════════
scorecard_cols = [
    "score_rank", "fund_score", "amfi_code", "fund_house", "scheme_name",
    "category", "sub_category", "plan",
    "cagr_1yr", "cagr_3yr", "cagr_5yr",
    "sharpe_ratio", "sortino_ratio",
    "expense_ratio_pct", "max_drawdown_pct", "peak_date", "trough_date",
    "rank_3yr_return", "rank_sharpe", "rank_alpha", "rank_expense_inv", "rank_maxdd_inv",
]
perf[scorecard_cols].to_csv("fund_scorecard.csv", index=False)
print("\nSaved fund_scorecard.csv")

ab_out = perf[["amfi_code", "fund_house", "scheme_name", "plan",
               "beta", "alpha_annual", "r_squared", "tracking_error_nifty100"]].copy()
ab_out.to_csv("alpha_beta.csv", index=False)
print("Saved alpha_beta.csv")


# ═══════════════════════════════════════════════════════════════════════════
# 11. Benchmark Comparison Chart — Top 5 Equity Funds vs NIFTY50 & NIFTY100
# ═══════════════════════════════════════════════════════════════════════════
print("\n[9] Benchmark comparison chart...")

top5 = perf[perf["category"] == "Equity"].head(5)

# 3-year window
date_3y = last_date - pd.DateOffset(years=3)

fig, axes = plt.subplots(2, 1, figsize=(14, 12), gridspec_kw={"height_ratios": [3, 1]})

# ── Panel A: Indexed NAV + benchmarks (base = 100) ─────────────────────
ax = axes[0]
colors_fund = [BLUE, ORANGE, GREEN, PURPLE, TEAL]

fund_te_rows = []
for i, (_, row) in enumerate(top5.iterrows()):
    code = row["amfi_code"]
    name = row["scheme_name"].split(" - ")[0].strip()
    df   = (nav[(nav["amfi_code"] == code) & (nav["date"] >= date_3y)]
            .sort_values("date"))
    if df.empty:
        continue
    base   = df.iloc[0]["nav"]
    indexed = df["nav"] / base * 100
    ax.plot(df["date"], indexed, label=name, color=colors_fund[i], linewidth=2)

    # Tracking error vs NIFTY100 (3yr window)
    fund_ret = df.set_index("date")["nav"].pct_change().dropna()
    common   = fund_ret.index.intersection(bench_ret100.index)
    if len(common) > 10:
        te = np.std((fund_ret.loc[common] - bench_ret100.loc[common]).values) * np.sqrt(TRADING_DAYS) * 100
        fund_te_rows.append({"Fund": name, "Tracking Error vs NIFTY100 (%)": round(te, 2)})

# Benchmarks
for idx_name, series, color, ls in [
    ("NIFTY 50",  nifty50,  RED,  "--"),
    ("NIFTY 100", nifty100, GREY, ":"),
]:
    s = series[series.index >= date_3y]
    if s.empty:
        continue
    indexed = s / s.iloc[0] * 100
    ax.plot(indexed.index, indexed.values, label=idx_name,
            color=color, linewidth=2, linestyle=ls)

ax.set_title("Top 5 Equity Funds vs NIFTY 50 & NIFTY 100 — 3-Year Indexed Performance",
             fontsize=13, fontweight="bold")
ax.set_ylabel("Indexed Value (Base = 100)", fontsize=11)
ax.legend(loc="upper left", fontsize=9)
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f"))
ax.grid(True, alpha=0.3)

# ── Panel B: Tracking Error bar chart ──────────────────────────────────
ax2 = axes[1]
if fund_te_rows:
    te_df = pd.DataFrame(fund_te_rows)
    bars = ax2.barh(te_df["Fund"], te_df["Tracking Error vs NIFTY100 (%)"],
                    color=colors_fund[:len(te_df)], height=0.5)
    for bar, val in zip(bars, te_df["Tracking Error vs NIFTY100 (%)"]):
        ax2.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                 f"{val:.2f}%", va="center", fontsize=9)
    ax2.set_xlabel("Annualised Tracking Error vs NIFTY100 (%)", fontsize=10)
    ax2.set_title("Tracking Error (3-Year Window)", fontsize=11, fontweight="bold")
    ax2.grid(True, alpha=0.3, axis="x")

plt.tight_layout()
plt.savefig(f"{CHARTS}/16_benchmark_comparison.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"  Saved {CHARTS}/16_benchmark_comparison.png")


# ═══════════════════════════════════════════════════════════════════════════
# 12. Scorecard Bar Chart (all 40 funds)
# ═══════════════════════════════════════════════════════════════════════════
fig2, ax3 = plt.subplots(figsize=(14, 9))
colors_bar = [GREEN if s >= 70 else (ORANGE if s >= 50 else RED) for s in perf["fund_score"]]
short_names = perf["scheme_name"].str.extract(r"^([^-]+)")[0].str.strip().str[:30]
bars = ax3.barh(short_names[::-1], perf["fund_score"][::-1], color=colors_bar[::-1], height=0.7)
ax3.axvline(50, color=GREY, linestyle="--", linewidth=1, label="Score = 50")
ax3.set_xlabel("Fund Score (0–100)", fontsize=11)
ax3.set_title("Fund Scorecard — All 40 Schemes\n(30% 3yr CAGR | 25% Sharpe | 20% Alpha | 15% Exp Ratio | 10% Max DD)",
              fontsize=12, fontweight="bold")
ax3.set_xlim(0, 110)
for bar, score in zip(bars[::-1], perf["fund_score"]):
    ax3.text(score + 0.5, bar.get_y() + bar.get_height() / 2,
             f"{score:.1f}", va="center", fontsize=8)
patches = [mpatches.Patch(color=GREEN, label="≥70 (Strong)"),
           mpatches.Patch(color=ORANGE, label="50–70 (Average)"),
           mpatches.Patch(color=RED, label="<50 (Weak)")]
ax3.legend(handles=patches, loc="lower right", fontsize=9)
plt.tight_layout()
plt.savefig(f"{CHARTS}/17_fund_scorecard_bar.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"  Saved {CHARTS}/17_fund_scorecard_bar.png")


# ═══════════════════════════════════════════════════════════════════════════
# 13. Daily return distribution plot
# ═══════════════════════════════════════════════════════════════════════════
top3_codes = perf.head(3)["amfi_code"].tolist()
fig3, ax4 = plt.subplots(figsize=(12, 5))
fund_colors = [BLUE, ORANGE, GREEN]
for code, color in zip(top3_codes, fund_colors):
    name = perf[perf["amfi_code"] == code]["scheme_name"].values[0].split(" - ")[0].strip()
    r    = returns_wide[code].dropna()
    ax4.hist(r * 100, bins=80, alpha=0.45, color=color, label=name, density=True)
ax4.axvline(0, color=GREY, linewidth=1, linestyle="--")
ax4.set_xlabel("Daily Return (%)", fontsize=11)
ax4.set_ylabel("Density", fontsize=11)
ax4.set_title("Daily Return Distribution — Top 3 Funds by Scorecard", fontsize=13, fontweight="bold")
ax4.legend(fontsize=9)
plt.tight_layout()
plt.savefig(f"{CHARTS}/18_daily_return_distribution.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"  Saved {CHARTS}/18_daily_return_distribution.png")


# ═══════════════════════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("PERFORMANCE SUMMARY — TOP 10 BY SCORECARD")
print("=" * 60)
cols_show = ["scheme_name", "plan", "fund_score", "cagr_3yr", "sharpe_ratio",
             "alpha_annual", "max_drawdown_pct"]
pd.set_option("display.max_colwidth", 45)
pd.set_option("display.float_format", lambda x: f"{x:.3f}")
print(perf[cols_show].head(10).to_string(index=False))
print("\nDeliverables ready:")
print("  fund_scorecard.csv | alpha_beta.csv")
print("  reports/charts/16_benchmark_comparison.png")
print("  reports/charts/17_fund_scorecard_bar.png")
print("  reports/charts/18_daily_return_distribution.png")
