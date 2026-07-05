"""
Day 3 — Exploratory Data Analysis (EDA)
Generates 15+ charts and saves PNGs to reports/charts/.
Run this script directly, or execute cells in EDA_Analysis.ipynb.
"""
import os
import warnings
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

warnings.filterwarnings("ignore")

CHARTS = "reports/charts"
PROC   = "data/processed"
os.makedirs(CHARTS, exist_ok=True)

# ── palette ────────────────────────────────────────────────────────────────
BLUE   = "#2563EB"
ORANGE = "#F97316"
GREEN  = "#16A34A"
RED    = "#DC2626"
PURPLE = "#7C3AED"
GREY   = "#6B7280"
TEAL   = "#0D9488"

sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)

# ── load data ──────────────────────────────────────────────────────────────
print("Loading data...")
fm   = pd.read_csv(f"{PROC}/01_fund_master.csv")
nav  = pd.read_csv(f"{PROC}/02_nav_history.csv", parse_dates=["date"])
aum  = pd.read_csv(f"{PROC}/03_aum_by_fund_house.csv", parse_dates=["date"])
sip  = pd.read_csv(f"{PROC}/04_monthly_sip_inflows.csv")
cat  = pd.read_csv(f"{PROC}/05_category_inflows.csv")
fol  = pd.read_csv(f"{PROC}/06_industry_folio_count.csv")
txn  = pd.read_csv(f"{PROC}/08_investor_transactions.csv", parse_dates=["transaction_date"])
hld  = pd.read_csv(f"{PROC}/09_portfolio_holdings.csv")

sip["month_dt"]      = pd.to_datetime(sip["month"] + "-01")
cat["month_dt"]      = pd.to_datetime(cat["month"] + "-01")
fol["quarter_dt"]    = pd.to_datetime(fol["quarter_start"] + "-01")


# ══════════════════════════════════════════════════════════════════════════
# CHART 1 — NAV Trend: large-cap equity funds 2022-2026 (Plotly → PNG)
# ══════════════════════════════════════════════════════════════════════════
print("\n[1] NAV trend analysis...")

large_cap_codes = fm[(fm["sub_category"] == "Large Cap") & (fm["plan"] == "Regular")]["amfi_code"].tolist()
nav_lc = nav[nav["amfi_code"].isin(large_cap_codes)].merge(
    fm[["amfi_code", "scheme_name"]], on="amfi_code"
)
# Shorten names
nav_lc["short_name"] = nav_lc["scheme_name"].str.extract(r"^([^-]+)")[0].str.strip()

fig = go.Figure()
for code in large_cap_codes:
    df_ = nav_lc[nav_lc["amfi_code"] == code].sort_values("date")
    name = df_["short_name"].iloc[0] if len(df_) else str(code)
    fig.add_trace(go.Scatter(x=df_["date"], y=df_["nav"], mode="lines",
                             name=name, line=dict(width=1.5)))

# Highlight 2023 bull run (Jan–Dec 2023) and 2024 corrections (Jan–Jun 2024)
fig.add_vrect(x0="2023-01-01", x1="2023-12-31",
              fillcolor="rgba(22,163,74,0.10)", line_width=0,
              annotation_text="2023 Bull Run", annotation_position="top left",
              annotation_font_color=GREEN)
fig.add_vrect(x0="2024-01-01", x1="2024-06-30",
              fillcolor="rgba(220,38,38,0.10)", line_width=0,
              annotation_text="2024 Correction", annotation_position="top left",
              annotation_font_color=RED)

fig.update_layout(
    title="Daily NAV — Large Cap Equity Funds (2022–2026)",
    xaxis_title="Date", yaxis_title="NAV (₹)",
    legend=dict(orientation="h", y=-0.25, font_size=10),
    height=500, width=1100,
    plot_bgcolor="white", paper_bgcolor="white",
    font=dict(family="Arial", size=12),
)
fig.write_image(f"{CHARTS}/01_nav_trend_largecap.png", scale=2)
print("  saved 01_nav_trend_largecap.png")


# ══════════════════════════════════════════════════════════════════════════
# CHART 2 — NAV trend for all 40 funds — top 10 by final NAV (Plotly)
# ══════════════════════════════════════════════════════════════════════════
print("[2] NAV trend all funds...")

final_nav = nav.groupby("amfi_code").last().reset_index()
top10_codes = final_nav.nlargest(10, "nav")["amfi_code"].tolist()

nav_top = nav[nav["amfi_code"].isin(top10_codes)].merge(
    fm[["amfi_code", "scheme_name"]], on="amfi_code"
)
nav_top["short_name"] = nav_top["scheme_name"].str.extract(r"^([^-]+)")[0].str.strip()

fig2 = go.Figure()
for code in top10_codes:
    d = nav_top[nav_top["amfi_code"] == code].sort_values("date")
    fig2.add_trace(go.Scatter(x=d["date"], y=d["nav"], mode="lines",
                              name=d["short_name"].iloc[0], line=dict(width=1.5)))

fig2.add_vrect(x0="2023-01-01", x1="2023-12-31",
               fillcolor="rgba(22,163,74,0.10)", line_width=0,
               annotation_text="2023 Bull Run", annotation_position="top left",
               annotation_font_color=GREEN)
fig2.add_vrect(x0="2024-01-01", x1="2024-06-30",
               fillcolor="rgba(220,38,38,0.10)", line_width=0,
               annotation_text="2024 Correction", annotation_position="top left",
               annotation_font_color=RED)

fig2.update_layout(
    title="Daily NAV — Top 10 Funds by NAV Value (2022–2026)",
    xaxis_title="Date", yaxis_title="NAV (₹)",
    legend=dict(orientation="h", y=-0.3, font_size=9),
    height=520, width=1100,
    plot_bgcolor="white", paper_bgcolor="white",
)
fig2.write_image(f"{CHARTS}/02_nav_trend_top10.png", scale=2)
print("  saved 02_nav_trend_top10.png")


# ══════════════════════════════════════════════════════════════════════════
# CHART 3 — AUM Growth: grouped bar by fund house (Seaborn)
# ══════════════════════════════════════════════════════════════════════════
print("[3] AUM growth bar chart...")

# Use Mar year-end snapshots to represent each year
aum["year"] = aum["date"].dt.year
aum_annual = aum[aum["date"].dt.month.isin([3, 12])].copy()
aum_annual = aum_annual.sort_values("date").drop_duplicates(["fund_house", "year"], keep="last")

# Short labels
short = {
    "Aditya Birla Sun Life MF": "ABSL",
    "Axis Mutual Fund": "Axis",
    "DSP Mutual Fund": "DSP",
    "HDFC Mutual Fund": "HDFC",
    "ICICI Prudential MF": "ICICI",
    "Kotak Mahindra MF": "Kotak",
    "Mirae Asset MF": "Mirae",
    "Nippon India MF": "Nippon",
    "SBI Mutual Fund": "SBI",
    "UTI Mutual Fund": "UTI",
}
aum_annual["fh_short"] = aum_annual["fund_house"].map(short)
aum_annual["aum_lakh_crore"] = aum_annual["aum_crore"] / 1e5

fig3, ax3 = plt.subplots(figsize=(14, 6))
palette = {y: c for y, c in zip(sorted(aum_annual["year"].unique()),
                                  [BLUE, TEAL, GREEN, ORANGE, PURPLE])}
bar = sns.barplot(data=aum_annual, x="fh_short", y="aum_lakh_crore",
                  hue="year", palette=palette, ax=ax3, width=0.7)

# Highlight SBI
sbi_patch = [p for p in ax3.patches
             if ax3.get_xticklabels() and True]
ax3.set_xlabel("")
ax3.set_ylabel("AUM (₹ Lakh Crore)", fontsize=12)
ax3.set_title("AUM Growth by Fund House (2022–2025)", fontsize=14, fontweight="bold")
ax3.legend(title="Year", bbox_to_anchor=(1.01, 1), loc="upper left")

# Annotate SBI max
sbi_max = aum_annual[aum_annual["fund_house"] == "SBI Mutual Fund"]["aum_lakh_crore"].max()
ax3.annotate(f"SBI ₹{sbi_max:.1f}L Cr\n(Market Leader)",
             xy=(8, sbi_max), xytext=(7.2, sbi_max + 0.8),
             arrowprops=dict(arrowstyle="->", color=RED), color=RED, fontsize=10, fontweight="bold")

plt.tight_layout()
plt.savefig(f"{CHARTS}/03_aum_growth_bar.png", dpi=150, bbox_inches="tight")
plt.close()
print("  saved 03_aum_growth_bar.png")


# ══════════════════════════════════════════════════════════════════════════
# CHART 4 — SIP Inflow Time-Series (Plotly)
# ══════════════════════════════════════════════════════════════════════════
print("[4] SIP inflow time-series...")

fig4 = go.Figure()
fig4.add_trace(go.Scatter(
    x=sip["month_dt"], y=sip["sip_inflow_crore"],
    mode="lines+markers", name="Monthly SIP Inflow",
    line=dict(color=BLUE, width=2),
    marker=dict(size=4),
))

# Annotate Dec-2025 ATH
ath_row = sip.loc[sip["sip_inflow_crore"].idxmax()]
fig4.add_annotation(
    x=str(ath_row["month_dt"])[:10], y=ath_row["sip_inflow_crore"],
    text=f"₹{int(ath_row['sip_inflow_crore']):,} Cr<br>All-Time High<br>(Dec 2025)",
    showarrow=True, arrowhead=2, arrowcolor=RED,
    font=dict(color=RED, size=11, family="Arial Bold"),
    bgcolor="white", bordercolor=RED, borderwidth=1,
    ax=40, ay=-60,
)

# Shade pandemic recovery
fig4.add_vrect(x0="2022-01-01", x1="2022-12-31",
               fillcolor="rgba(249,115,22,0.08)", line_width=0,
               annotation_text="Recovery Phase", annotation_font_color=ORANGE)

fig4.update_layout(
    title="Monthly SIP Inflow Trend — Industry (Jan 2022 – Dec 2025)",
    xaxis_title="Month", yaxis_title="SIP Inflow (₹ Crore)",
    height=450, width=1000,
    plot_bgcolor="white", paper_bgcolor="white",
    font=dict(family="Arial", size=12),
)
fig4.write_image(f"{CHARTS}/04_sip_inflow_timeseries.png", scale=2)
print("  saved 04_sip_inflow_timeseries.png")


# ══════════════════════════════════════════════════════════════════════════
# CHART 5 — Category Inflow Heatmap (Seaborn)
# ══════════════════════════════════════════════════════════════════════════
print("[5] Category inflow heatmap...")

pivot = cat.pivot_table(index="category", columns="month", values="net_inflow_crore")
pivot.columns = [m[-5:] for m in pivot.columns]  # show MM only

fig5, ax5 = plt.subplots(figsize=(14, 7))
sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlOrRd",
            linewidths=0.5, ax=ax5,
            annot_kws={"size": 9},
            cbar_kws={"label": "Net Inflow (₹ Cr)"})
ax5.set_title("Category-wise Net Inflow Heatmap (Apr 2024 – Mar 2025)",
              fontsize=14, fontweight="bold")
ax5.set_xlabel("Month", fontsize=11)
ax5.set_ylabel("Fund Category", fontsize=11)
plt.xticks(rotation=45, ha="right")
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig(f"{CHARTS}/05_category_inflow_heatmap.png", dpi=150, bbox_inches="tight")
plt.close()
print("  saved 05_category_inflow_heatmap.png")


# ══════════════════════════════════════════════════════════════════════════
# CHART 6 — Investor Demographics: Age Group Pie + Gender Pie (Matplotlib)
# ══════════════════════════════════════════════════════════════════════════
print("[6] Investor demographics...")

age_counts = txn["age_group"].value_counts().sort_index()
gender_counts = txn["gender"].value_counts()

fig6, axes = plt.subplots(1, 2, figsize=(13, 6))

age_colors = [BLUE, TEAL, GREEN, ORANGE, PURPLE]
axes[0].pie(age_counts.values, labels=age_counts.index,
            autopct="%1.1f%%", colors=age_colors,
            startangle=90, pctdistance=0.82,
            wedgeprops=dict(width=0.55))
axes[0].set_title("Investor Age Group Distribution", fontsize=13, fontweight="bold")

gender_colors = [BLUE, ORANGE]
axes[1].pie(gender_counts.values, labels=gender_counts.index,
            autopct="%1.1f%%", colors=gender_colors,
            startangle=90, pctdistance=0.82,
            wedgeprops=dict(width=0.55))
axes[1].set_title("Investor Gender Split", fontsize=13, fontweight="bold")

plt.suptitle("Investor Demographics", fontsize=15, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig(f"{CHARTS}/06_investor_demographics_pie.png", dpi=150, bbox_inches="tight")
plt.close()
print("  saved 06_investor_demographics_pie.png")


# ══════════════════════════════════════════════════════════════════════════
# CHART 7 — SIP Amount Box Plot by Age Group (Seaborn)
# ══════════════════════════════════════════════════════════════════════════
print("[7] SIP box plot by age group...")

sip_txn = txn[txn["transaction_type"] == "SIP"].copy()
age_order = ["18-25", "26-35", "36-45", "46-55", "56+"]

fig7, ax7 = plt.subplots(figsize=(11, 6))
sns.boxplot(data=sip_txn, x="age_group", y="amount_inr",
            order=age_order, palette="Blues", ax=ax7,
            showfliers=False, width=0.55)
ax7.set_title("SIP Investment Amount by Age Group", fontsize=14, fontweight="bold")
ax7.set_xlabel("Age Group", fontsize=12)
ax7.set_ylabel("SIP Amount (₹)", fontsize=12)
ax7.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
plt.tight_layout()
plt.savefig(f"{CHARTS}/07_sip_boxplot_agegroup.png", dpi=150, bbox_inches="tight")
plt.close()
print("  saved 07_sip_boxplot_agegroup.png")


# ══════════════════════════════════════════════════════════════════════════
# CHART 8 — Geographic: SIP by State (horizontal bar) + T30 vs B30 Pie
# ══════════════════════════════════════════════════════════════════════════
print("[8] Geographic distribution...")

sip_state = (sip_txn.groupby("state")["amount_inr"]
             .sum().sort_values(ascending=True) / 1e7)

fig8, axes = plt.subplots(1, 2, figsize=(16, 7))

# Horizontal bar
colors_bar = [RED if v == sip_state.max() else BLUE for v in sip_state.values]
axes[0].barh(sip_state.index, sip_state.values, color=colors_bar)
axes[0].set_xlabel("Total SIP Amount (₹ Crore)", fontsize=11)
axes[0].set_title("SIP Amount by State", fontsize=13, fontweight="bold")
axes[0].xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"₹{x:.0f} Cr"))

# T30 vs B30 pie
tier_sip = sip_txn.groupby("city_tier")["amount_inr"].sum()
axes[1].pie(tier_sip.values, labels=tier_sip.index,
            autopct="%1.1f%%", colors=[BLUE, ORANGE],
            startangle=90, pctdistance=0.75,
            wedgeprops=dict(width=0.5))
axes[1].set_title("SIP Amount: T30 vs B30 Cities", fontsize=13, fontweight="bold")

plt.suptitle("Geographic Distribution of SIP Investments", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{CHARTS}/08_geographic_distribution.png", dpi=150, bbox_inches="tight")
plt.close()
print("  saved 08_geographic_distribution.png")


# ══════════════════════════════════════════════════════════════════════════
# CHART 9 — Folio Count Growth (Plotly line with milestones)
# ══════════════════════════════════════════════════════════════════════════
print("[9] Folio count growth...")

fig9 = go.Figure()
fig9.add_trace(go.Scatter(
    x=fol["quarter_dt"].astype(str), y=fol["total_folios_crore"],
    mode="lines+markers+text",
    line=dict(color=PURPLE, width=2.5),
    marker=dict(size=8, color=PURPLE),
    name="Total Folios",
))

# Milestone annotations
milestones = [
    ("2022-01-01", 13.26, "13.26 Cr\nStart"),
    ("2023-01-01", 14.81, "14.81 Cr"),
    ("2024-01-01", 17.78, "18 Cr"),
    ("2025-12-01", 26.12, "26.12 Cr\nAll-time high"),
]
for x, y, label in milestones:
    xd = pd.to_datetime(x)
    row = fol.iloc[(fol["quarter_dt"] - xd).abs().argsort()[:1]]
    fig9.add_annotation(
        x=str(row["quarter_dt"].values[0])[:10], y=float(row["total_folios_crore"].values[0]),
        text=label, showarrow=True, arrowhead=2,
        font=dict(size=10, color=PURPLE), ax=30, ay=-45,
    )

fig9.update_layout(
    title="Industry Folio Count Growth (Jan 2022 – Dec 2025)",
    xaxis_title="Quarter", yaxis_title="Total Folios (Crore)",
    height=450, width=1000,
    plot_bgcolor="white", paper_bgcolor="white",
    showlegend=False,
    font=dict(family="Arial", size=12),
)
fig9.write_image(f"{CHARTS}/09_folio_count_growth.png", scale=2)
print("  saved 09_folio_count_growth.png")


# ══════════════════════════════════════════════════════════════════════════
# CHART 10 — NAV Return Correlation Matrix (Seaborn heatmap)
# ══════════════════════════════════════════════════════════════════════════
print("[10] NAV return correlation matrix...")

# Select 10 equity funds (5 Regular, 5 Direct) across categories
eq_funds = fm[fm["category"] == "Equity"].copy()
sel_regular = eq_funds[eq_funds["plan"] == "Regular"].groupby("sub_category").first().reset_index()
sel_codes = sel_regular["amfi_code"].head(10).tolist()

nav_sel = nav[nav["amfi_code"].isin(sel_codes)].merge(
    fm[["amfi_code", "scheme_name"]], on="amfi_code"
)
nav_sel["short"] = (nav_sel["scheme_name"]
                    .str.extract(r"^([^-]+)")[0].str.strip()
                    .str.replace("Fund", "F.", regex=False))

# Pivot to wide, compute daily returns
nav_wide = nav_sel.pivot_table(index="date", columns="short", values="nav")
returns  = nav_wide.pct_change().dropna()
corr     = returns.corr()

fig10, ax10 = plt.subplots(figsize=(11, 9))
mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm",
            center=0, vmin=-1, vmax=1,
            linewidths=0.5, ax=ax10, annot_kws={"size": 9},
            cbar_kws={"label": "Pearson Correlation"})
ax10.set_title("NAV Daily Return Correlation Matrix (10 Equity Funds)",
               fontsize=13, fontweight="bold")
plt.xticks(rotation=45, ha="right", fontsize=9)
plt.yticks(rotation=0, fontsize=9)
plt.tight_layout()
plt.savefig(f"{CHARTS}/10_nav_correlation_matrix.png", dpi=150, bbox_inches="tight")
plt.close()
print("  saved 10_nav_correlation_matrix.png")


# ══════════════════════════════════════════════════════════════════════════
# CHART 11 — Sector Allocation Donut (all equity funds)
# ══════════════════════════════════════════════════════════════════════════
print("[11] Sector allocation donut...")

eq_codes  = fm[fm["category"] == "Equity"]["amfi_code"].tolist()
hld_eq    = hld[hld["amfi_code"].isin(eq_codes)]
sector_wt = (hld_eq.groupby("sector")["weight_pct"]
             .mean().sort_values(ascending=False))
# Group small sectors as "Others"
threshold = 2.5
big   = sector_wt[sector_wt >= threshold]
other = pd.Series({"Others": sector_wt[sector_wt < threshold].sum()})
sector_final = pd.concat([big, other]).sort_values(ascending=False)

colors_donut = [BLUE, TEAL, GREEN, ORANGE, PURPLE, RED, GREY,
                "#F59E0B", "#10B981", "#6366F1", "#EC4899"]

fig11, ax11 = plt.subplots(figsize=(10, 8))
wedges, texts, autotexts = ax11.pie(
    sector_final.values,
    labels=sector_final.index,
    autopct="%1.1f%%",
    colors=colors_donut[:len(sector_final)],
    startangle=90, pctdistance=0.80,
    wedgeprops=dict(width=0.55),
)
for at in autotexts:
    at.set_fontsize(9)
ax11.set_title("Sector Allocation — Equity Mutual Funds\n(Avg Weight % across all equity schemes)",
               fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{CHARTS}/11_sector_allocation_donut.png", dpi=150, bbox_inches="tight")
plt.close()
print("  saved 11_sector_allocation_donut.png")


# ══════════════════════════════════════════════════════════════════════════
# CHART 12 — SIP YoY Growth Rate (Plotly bar)
# ══════════════════════════════════════════════════════════════════════════
print("[12] SIP YoY growth rate...")

sip_yoy = sip.dropna(subset=["yoy_growth_pct"]).copy()
colors_bar = [GREEN if v >= 0 else RED for v in sip_yoy["yoy_growth_pct"]]

fig12 = go.Figure(go.Bar(
    x=sip_yoy["month_dt"], y=sip_yoy["yoy_growth_pct"],
    marker_color=colors_bar, name="YoY Growth %",
))
fig12.add_hline(y=0, line_dash="dot", line_color=GREY)
fig12.update_layout(
    title="Monthly SIP Inflow — Year-on-Year Growth % (2023–2025)",
    xaxis_title="Month", yaxis_title="YoY Growth (%)",
    height=420, width=1000,
    plot_bgcolor="white", paper_bgcolor="white",
    font=dict(family="Arial", size=12),
)
fig12.write_image(f"{CHARTS}/12_sip_yoy_growth.png", scale=2)
print("  saved 12_sip_yoy_growth.png")


# ══════════════════════════════════════════════════════════════════════════
# CHART 13 — Transaction Type Distribution by Payment Mode (Seaborn)
# ══════════════════════════════════════════════════════════════════════════
print("[13] Transaction type by payment mode...")

txn_pay = (txn.groupby(["transaction_type", "payment_mode"])
              .size().reset_index(name="count"))

fig13, ax13 = plt.subplots(figsize=(11, 6))
sns.barplot(data=txn_pay, x="transaction_type", y="count",
            hue="payment_mode", palette="Set2", ax=ax13, width=0.65)
ax13.set_title("Transaction Type vs Payment Mode", fontsize=14, fontweight="bold")
ax13.set_xlabel("Transaction Type", fontsize=12)
ax13.set_ylabel("Number of Transactions", fontsize=12)
ax13.legend(title="Payment Mode", bbox_to_anchor=(1.01, 1), loc="upper left")
plt.tight_layout()
plt.savefig(f"{CHARTS}/13_txn_type_payment_mode.png", dpi=150, bbox_inches="tight")
plt.close()
print("  saved 13_txn_type_payment_mode.png")


# ══════════════════════════════════════════════════════════════════════════
# CHART 14 — Scheme Performance: Sharpe vs Return (scatter, Plotly)
# ══════════════════════════════════════════════════════════════════════════
print("[14] Sharpe vs 3yr return scatter...")

perf = pd.read_csv(f"{PROC}/07_scheme_performance.csv")
perf = perf.merge(fm[["amfi_code", "sub_category"]], on="amfi_code")
perf["short"] = perf["scheme_name"].str.extract(r"^([^-]+)")[0].str.strip()

fig14 = px.scatter(
    perf, x="return_3yr_pct", y="sharpe_ratio",
    color="sub_category", size="aum_crore",
    hover_name="short",
    size_max=30,
    labels={"return_3yr_pct": "3-Year CAGR (%)", "sharpe_ratio": "Sharpe Ratio",
            "sub_category": "Category"},
    title="Risk-Adjusted Performance: Sharpe Ratio vs 3-Year Return",
    height=520, width=1000,
)
fig14.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                    font=dict(family="Arial", size=12))
fig14.write_image(f"{CHARTS}/14_sharpe_vs_return_scatter.png", scale=2)
print("  saved 14_sharpe_vs_return_scatter.png")


# ══════════════════════════════════════════════════════════════════════════
# CHART 15 — Expense Ratio Distribution by Category (Seaborn violin)
# ══════════════════════════════════════════════════════════════════════════
print("[15] Expense ratio distribution...")

fig15, ax15 = plt.subplots(figsize=(10, 6))
sns.violinplot(data=perf, x="sub_category", y="expense_ratio_pct",
               palette=[BLUE, ORANGE], inner="box", ax=ax15, width=0.65)
ax15.axhline(1.0, color=RED, linestyle="--", label="1% threshold")
ax15.set_title("Expense Ratio Distribution by Sub-Category", fontsize=14, fontweight="bold")
ax15.set_xlabel("Sub-Category", fontsize=12)
ax15.set_ylabel("Expense Ratio (%)", fontsize=12)
ax15.legend()
plt.tight_layout()
plt.savefig(f"{CHARTS}/15_expense_ratio_violin.png", dpi=150, bbox_inches="tight")
plt.close()
print("  saved 15_expense_ratio_violin.png")


print(f"\nAll charts saved to {CHARTS}/")
print(f"Total: {len(os.listdir(CHARTS))} chart files")
