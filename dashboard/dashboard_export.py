"""
Day 6 -- Dashboard Development
Generates 4 publication-quality dashboard pages (PNG + combined PDF).
Layout mirrors the Power BI / Tableau specification from the task board.

Pages:
  1. Industry Overview  -- KPIs, AUM trend, AUM by AMC
  2. Fund Performance   -- Scatter (return vs risk), scorecard table, NAV vs benchmark
  3. Investor Analytics -- State bars, donut, age-group SIP, monthly volume
  4. SIP & Market Trends-- Dual-axis SIP+Nifty50, category heatmap, top-5 FY25

Deliverables: page1-4 PNGs + Dashboard.pdf (all in dashboard/ folder)
"""

import os
import warnings
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import matplotlib.colors as mcolors
from matplotlib.dates import DateFormatter as MDateFormatter
from matplotlib.patches import FancyBboxPatch
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
import pandas as pd
import numpy as np

warnings.filterwarnings("ignore")
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.titlesize": 10,
    "axes.labelsize": 8,
    "xtick.labelsize": 7.5,
    "ytick.labelsize": 7.5,
})

BASE = os.path.dirname(os.path.abspath(__file__))
PROC = os.path.join(BASE, "..", "data", "processed")
RAW  = os.path.join(BASE, "..", "data", "raw")
OUT  = BASE

# ── Bluestock Palette ────────────────────────────────────────────────────────
BG      = "#EEF2F7"
HEADER  = "#0F172A"
PRIMARY = "#1E40AF"
BLUE    = "#2563EB"
ORANGE  = "#F97316"
GREEN   = "#16A34A"
RED     = "#DC2626"
PURPLE  = "#7C3AED"
TEAL    = "#0D9488"
GREY    = "#64748B"
LGREY   = "#E2E8F0"
GOLD    = "#D97706"
WHITE   = "#FFFFFF"

CAT_PAL = {
    "Large Cap":       PRIMARY,
    "Mid Cap":         BLUE,
    "Small Cap":       ORANGE,
    "ELSS":            GREEN,
    "Flexi Cap":       PURPLE,
    "Large & Mid Cap": TEAL,
    "Liquid":          GREY,
    "Debt":            GOLD,
    "Gilt":            RED,
    "Multi Cap":       "#0891B2",
    "Index":           "#059669",
    "Hybrid":          "#9333EA",
}

PW, PH, DPI = 16, 9, 150

# ── Load data ────────────────────────────────────────────────────────────────
print("Loading data ...")
fm   = pd.read_csv(os.path.join(PROC, "01_fund_master.csv"))
nav  = pd.read_csv(os.path.join(RAW,  "02_nav_history.csv"), parse_dates=["date"])
aum  = pd.read_csv(os.path.join(PROC, "03_aum_by_fund_house.csv"), parse_dates=["date"])
sip  = pd.read_csv(os.path.join(PROC, "04_monthly_sip_inflows.csv"))
cat  = pd.read_csv(os.path.join(PROC, "05_category_inflows.csv"))
fol  = pd.read_csv(os.path.join(PROC, "06_industry_folio_count.csv"))
perf = pd.read_csv(os.path.join(PROC, "07_scheme_performance.csv"))
txn  = pd.read_csv(os.path.join(PROC, "08_investor_transactions.csv"),
                   parse_dates=["transaction_date"])
bm   = pd.read_csv(os.path.join(PROC, "10_benchmark_indices.csv"), parse_dates=["date"])

nav  = nav.sort_values(["amfi_code", "date"]).reset_index(drop=True)
sip["month_dt"]   = pd.to_datetime(sip["month"])
cat["month_dt"]   = pd.to_datetime(cat["month"])
fol["quarter_dt"] = pd.to_datetime(fol["quarter_start"])
print("Data loaded.")


# ── Shared helpers ───────────────────────────────────────────────────────────

def add_header(fig, title):
    ax = fig.add_axes([0, 0.936, 1, 0.064])
    ax.set_facecolor(HEADER)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.text(0.012, 0.52, "BLUESTOCK", color="#93C5FD", fontsize=14,
            fontweight="bold", va="center", fontfamily="monospace")
    ax.text(0.108, 0.52, "|", color="#475569", fontsize=14, va="center")
    ax.text(0.118, 0.52, title, color="white", fontsize=12,
            fontweight="bold", va="center")
    ax.text(0.988, 0.52,
            "Mutual Fund Analytics  |  Capstone Project  |  Bluestock Fintech",
            color="#475569", fontsize=7.5, va="center", ha="right")


def kpi_card(ax, value, label, sub=None, color=PRIMARY):
    ax.set_facecolor(WHITE)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0.04, 0.06), 0.92, 0.88,
                                boxstyle="round,pad=0.02",
                                lw=1.8, edgecolor=color, facecolor=WHITE, zorder=2))
    ax.add_patch(FancyBboxPatch((0.04, 0.80), 0.92, 0.14,
                                boxstyle="round,pad=0.01",
                                lw=0, facecolor=color, alpha=0.13, zorder=3))
    ax.text(0.5, 0.87, label, ha="center", va="center", fontsize=8.5,
            color=color, fontweight="bold", zorder=4)
    ax.text(0.5, 0.51, value, ha="center", va="center", fontsize=19,
            color=HEADER, fontweight="bold", zorder=4)
    if sub:
        ax.text(0.5, 0.19, sub, ha="center", va="center",
                fontsize=7.5, color=GREY, zorder=4)


def style_ax(ax, title=None, xlabel=None, ylabel=None, grid="y"):
    ax.set_facecolor(WHITE)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_edgecolor(LGREY)
    ax.tick_params(colors=GREY, labelsize=7.5)
    if grid:
        ax.grid(axis=grid, color=LGREY, linewidth=0.6, alpha=0.9, zorder=0)
    if title:  ax.set_title(title, fontsize=9.5, fontweight="bold", color=HEADER, pad=5)
    if xlabel: ax.set_xlabel(xlabel, fontsize=8, color=GREY)
    if ylabel: ax.set_ylabel(ylabel, fontsize=8, color=GREY)


def add_section_bg(fig, pos, label):
    """Thin coloured section label strip."""
    ax = fig.add_axes(pos)
    ax.set_facecolor(BG); ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    ax.text(0.01, 0.5, label, fontsize=7.5, color=GREY,
            fontstyle="italic", va="center")


# ============================================================================
# PAGE 1 — Industry Overview
# ============================================================================
print("\n[1] Rendering Page 1 — Industry Overview ...")

aum_trend   = aum.groupby("date")["aum_crore"].sum().reset_index()
aum_trend["aum_lakh_cr"] = aum_trend["aum_crore"] / 1e5

latest_dt   = aum["date"].max()
aum_amc     = (aum[aum["date"] == latest_dt]
               .sort_values("aum_crore")
               .assign(aum_lakh_cr=lambda x: x["aum_crore"] / 1e5))

fig1 = plt.figure(figsize=(PW, PH), facecolor=BG)
add_header(fig1, "Industry Overview")

kpis = [
    ("₹81L Cr",  "Total Industry AUM",  "Mar 2026",  PRIMARY),
    ("₹31K Cr",  "Annual SIP Inflows",  "FY2025",    BLUE),
    ("26.12 Cr", "Total Folios",        "Q4 FY2026", GREEN),
    ("1,908",    "Total Schemes",       "Active",    ORANGE),
]
for i, (val, lbl, sub, col) in enumerate(kpis):
    ax = fig1.add_axes([0.03 + i * 0.245, 0.756, 0.22, 0.165])
    kpi_card(ax, val, lbl, sub=sub, color=col)

# AUM Trend line chart
ax_t = fig1.add_axes([0.04, 0.07, 0.63, 0.65])
ax_t.fill_between(aum_trend["date"], aum_trend["aum_lakh_cr"],
                  alpha=0.10, color=PRIMARY)
ax_t.plot(aum_trend["date"], aum_trend["aum_lakh_cr"],
          color=PRIMARY, lw=2.5, marker="o", ms=5, zorder=3)
last = aum_trend.iloc[-1]
ax_t.annotate(f'₹{last["aum_lakh_cr"]:.1f}L Cr',
              xy=(last["date"], last["aum_lakh_cr"]),
              xytext=(8, 8), textcoords="offset points",
              fontsize=8, color=PRIMARY, fontweight="bold",
              arrowprops=dict(arrowstyle="-", color=LGREY, lw=0.8))
style_ax(ax_t, "Industry AUM Trend — 10 Fund Houses, 2022–2026",
         ylabel="AUM (₹ Lakh Crore)")
ax_t.xaxis.set_major_formatter(MDateFormatter("%b '%y"))
ax_t.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"₹{v:.0f}L"))
plt.setp(ax_t.get_xticklabels(), rotation=30, ha="right")

# AUM by AMC bar
ax_a = fig1.add_axes([0.72, 0.07, 0.26, 0.65])
colors_bar = [PRIMARY if v == aum_amc["aum_crore"].max() else BLUE
              for v in aum_amc["aum_crore"]]
short = aum_amc["fund_house"].str.replace(r"\s*Mutual Fund", "", regex=True).str[:18]
bars = ax_a.barh(short, aum_amc["aum_lakh_cr"], color=colors_bar, height=0.65)
style_ax(ax_a, "AUM by AMC — Mar 2026", xlabel="₹ Lakh Crore", grid="x")
ax_a.spines["left"].set_visible(False)
ax_a.tick_params(axis="y", labelsize=7)
for bar in bars:
    w = bar.get_width()
    ax_a.text(w + 0.05, bar.get_y() + bar.get_height() / 2,
              f"₹{w:.1f}L", va="center", ha="left", fontsize=7, color=GREY)

out1 = os.path.join(OUT, "page1_industry_overview.png")
fig1.savefig(out1, dpi=DPI, bbox_inches="tight", facecolor=BG)
plt.close(fig1)
print(f"   Saved {out1}")


# ============================================================================
# PAGE 2 — Fund Performance
# ============================================================================
print("\n[2] Rendering Page 2 — Fund Performance ...")

# NAV normalised to 100 for top 3 equity funds by AUM
top3 = (perf[perf["category"] == "Equity"]
        .sort_values("aum_crore", ascending=False)
        .head(3)[["amfi_code", "scheme_name"]])

nifty100 = bm[bm["index_name"] == "NIFTY100"].set_index("date")["close_value"]

def norm100(series):
    first = series.dropna().iloc[0]
    return (series / first) * 100

fig2 = plt.figure(figsize=(PW, PH), facecolor=BG)
add_header(fig2, "Fund Performance")

# Scatter: return vs risk, bubble = AUM
ax_sc = fig2.add_axes([0.04, 0.07, 0.46, 0.84])
sub_cats = perf["sub_category"] if "sub_category" in perf.columns else perf["category"]
unique_cats = perf["category"].unique()
for cat_name in unique_cats:
    sub = perf[perf["category"] == cat_name]
    sizes = (sub["aum_crore"] / sub["aum_crore"].max() * 400 + 60).clip(60, 600)
    ax_sc.scatter(sub["return_3yr_pct"], sub["std_dev_ann_pct"],
                  s=sizes, color=CAT_PAL.get(cat_name, GREY),
                  alpha=0.75, label=cat_name, zorder=3, edgecolors="white", lw=0.5)

# Label top 5 by AUM
for _, row in perf.nlargest(5, "aum_crore").iterrows():
    short_name = row["scheme_name"].split("-")[0].strip()[:18]
    ax_sc.annotate(short_name,
                   xy=(row["return_3yr_pct"], row["std_dev_ann_pct"]),
                   xytext=(5, 4), textcoords="offset points",
                   fontsize=6.5, color=HEADER, alpha=0.85)

ax_sc.axvline(perf["return_3yr_pct"].mean(), color=LGREY, lw=1, ls="--")
ax_sc.axhline(perf["std_dev_ann_pct"].mean(), color=LGREY, lw=1, ls="--")
ax_sc.text(perf["return_3yr_pct"].mean() + 0.2,
           perf["std_dev_ann_pct"].max() * 0.98,
           "Avg Return", fontsize=7, color=GREY)
style_ax(ax_sc, "Risk-Return Scatter  (bubble = AUM, 3-Year Annualised)",
         xlabel="3-Year Return (%)", ylabel="Annualised Std Dev (%)", grid=None)
ax_sc.legend(loc="upper left", fontsize=7, framealpha=0.7,
             markerscale=0.7, handletextpad=0.4)
ax_sc.grid(True, color=LGREY, lw=0.5, alpha=0.7)

# Quadrant labels
ret_m = perf["return_3yr_pct"].mean()
std_m = perf["std_dev_ann_pct"].mean()
xlim = ax_sc.get_xlim(); ylim = ax_sc.get_ylim()
ax_sc.text(xlim[1]*0.98, ylim[1]*0.97, "High Return\nHigh Risk",
           ha="right", va="top", fontsize=7, color=RED, alpha=0.6)
ax_sc.text(xlim[0]*0.98 if xlim[0] < 0 else xlim[0]+0.2, ylim[0]+0.3,
           "Low Return\nLow Risk",
           ha="left", va="bottom", fontsize=7, color=GREEN, alpha=0.6)

# Scorecard table (top 10 by Sharpe)
top10 = perf.nlargest(10, "sharpe_ratio")[
    ["scheme_name", "return_3yr_pct", "sharpe_ratio", "expense_ratio_pct",
     "morningstar_rating", "risk_grade"]
].reset_index(drop=True)

ax_tbl = fig2.add_axes([0.54, 0.46, 0.44, 0.45])
ax_tbl.set_facecolor(WHITE)
ax_tbl.set_xlim(0, 1); ax_tbl.set_ylim(0, 1); ax_tbl.axis("off")
ax_tbl.set_title("Fund Scorecard — Top 10 by Sharpe Ratio",
                 fontsize=9.5, fontweight="bold", color=HEADER, pad=4)

headers  = ["Scheme", "3yr Ret%", "Sharpe", "Exp%", "Risk"]
col_x    = [0.01, 0.52, 0.65, 0.77, 0.90]
row_h    = 0.074
header_y = 0.92

# Header row
for j, h in enumerate(headers):
    ax_tbl.text(col_x[j], header_y, h, fontsize=7.5,
                color=WHITE, fontweight="bold",
                transform=ax_tbl.transAxes)
ax_tbl.add_patch(FancyBboxPatch((0, 0.88), 1, 0.08,
                                boxstyle="square,pad=0",
                                facecolor=PRIMARY, lw=0, zorder=1))

risk_col = {"Low": GREEN, "Moderate": GOLD, "High": RED,
            "Very High": RED, "Moderately High": ORANGE}

for i, row in top10.iterrows():
    y = header_y - (i + 1) * row_h
    bg = LGREY if i % 2 == 0 else WHITE
    ax_tbl.add_patch(FancyBboxPatch((0, y - 0.02), 1, row_h,
                                   boxstyle="square,pad=0",
                                   facecolor=bg, lw=0, zorder=0))
    name = row["scheme_name"].split("-")[0].strip()[:30]
    ax_tbl.text(col_x[0], y + 0.01, name, fontsize=6.8, color=HEADER,
                transform=ax_tbl.transAxes, va="center")
    ax_tbl.text(col_x[1], y + 0.01, f"{row['return_3yr_pct']:.1f}%",
                fontsize=7, color=PRIMARY, fontweight="bold", va="center")
    ax_tbl.text(col_x[2], y + 0.01, f"{row['sharpe_ratio']:.2f}",
                fontsize=7, color=HEADER, va="center")
    ax_tbl.text(col_x[3], y + 0.01, f"{row['expense_ratio_pct']:.2f}%",
                fontsize=7, color=HEADER, va="center")
    rc = risk_col.get(str(row["risk_grade"]), GREY)
    ax_tbl.text(col_x[4], y + 0.01, str(row["risk_grade"])[:3],
                fontsize=7, color=rc, fontweight="bold", va="center")

# NAV vs NIFTY100 normalised
ax_nav = fig2.add_axes([0.54, 0.07, 0.44, 0.35])
nav_colors = [GREEN, TEAL, PURPLE]
for (_, fr), col in zip(top3.iterrows(), nav_colors):
    fn = nav[nav["amfi_code"] == fr["amfi_code"]].set_index("date")["nav"]
    fn_n = norm100(fn)
    name = fr["scheme_name"].split("-")[0].strip()[:20]
    ax_nav.plot(fn_n.index, fn_n.values, lw=1.6, color=col,
                label=name, alpha=0.9)

nifty_n = norm100(nifty100.reindex(
    pd.date_range(nifty100.index.min(), nifty100.index.max(), freq="B")
).ffill())
ax_nav.plot(nifty_n.index, nifty_n.values,
            lw=1.8, color=ORANGE, ls="--", label="NIFTY 100", alpha=0.85)

style_ax(ax_nav, "NAV vs NIFTY 100  (Indexed to 100 at start)",
         ylabel="Indexed Value", grid="y")
ax_nav.xaxis.set_major_formatter(MDateFormatter("%b '%y"))
plt.setp(ax_nav.get_xticklabels(), rotation=25, ha="right")
ax_nav.legend(loc="upper left", fontsize=7, framealpha=0.7, ncol=2)
ax_nav.text(0.98, 0.97, "Slicers: Fund House | Category | Plan",
            transform=ax_nav.transAxes, ha="right", va="top",
            fontsize=6.5, color=GREY, fontstyle="italic")

out2 = os.path.join(OUT, "page2_fund_performance.png")
fig2.savefig(out2, dpi=DPI, bbox_inches="tight", facecolor=BG)
plt.close(fig2)
print(f"   Saved {out2}")


# ============================================================================
# PAGE 3 — Investor Analytics
# ============================================================================
print("\n[3] Rendering Page 3 — Investor Analytics ...")

# State bar (top 15)
state_txn = (txn.groupby("state")["amount_inr"].sum()
             .sort_values(ascending=True).tail(15))
state_cr  = state_txn / 1e7

# Donut
donut_data = txn.groupby("transaction_type")["amount_inr"].sum()
donut_colors = {
    "SIP": BLUE, "Lumpsum": ORANGE, "Redemption": RED,
    "STP": PURPLE, "SWP": TEAL, "Switch": GREY,
}

# Age group avg SIP
age_sip = (txn[txn["transaction_type"] == "SIP"]
           .groupby("age_group")["amount_inr"].mean()
           .sort_index())

# Monthly transaction volume
txn["month_dt"] = txn["transaction_date"].dt.to_period("M").dt.to_timestamp()
monthly_vol = (txn.groupby("month_dt")["amount_inr"].sum() / 1e7).reset_index()

fig3 = plt.figure(figsize=(PW, PH), facecolor=BG)
add_header(fig3, "Investor Analytics")

# State bars
ax_st = fig3.add_axes([0.03, 0.52, 0.55, 0.40])
bar_c = [PRIMARY if i == len(state_cr)-1 else BLUE for i in range(len(state_cr))]
ax_st.barh(state_cr.index, state_cr.values, color=bar_c, height=0.7)
style_ax(ax_st, "Transaction Amount by State — Top 15 (₹ Crore)",
         xlabel="₹ Crore", grid="x")
ax_st.spines["left"].set_visible(False)
ax_st.tick_params(axis="y", labelsize=7)
for i, v in enumerate(state_cr.values):
    ax_st.text(v + state_cr.max() * 0.01, i, f"₹{v:.0f}Cr",
               va="center", ha="left", fontsize=6.5, color=GREY)
ax_st.text(0.98, 0.02, "Slicer: State | City Tier",
           transform=ax_st.transAxes, ha="right", fontsize=6.5,
           color=GREY, fontstyle="italic")

# Donut
ax_dn = fig3.add_axes([0.62, 0.52, 0.36, 0.40])
dc = [donut_colors.get(k, GREY) for k in donut_data.index]
wedges, texts, autotexts = ax_dn.pie(
    donut_data.values, labels=None,
    colors=dc, autopct="%1.1f%%",
    startangle=90, pctdistance=0.75,
    wedgeprops=dict(width=0.50, edgecolor=WHITE, linewidth=2))
for at in autotexts:
    at.set_fontsize(8); at.set_color(WHITE); at.set_fontweight("bold")
legend_patches = [mpatches.Patch(color=donut_colors.get(k, GREY), label=f"{k}  ₹{v/1e7:.0f}Cr")
                  for k, v in donut_data.items()]
ax_dn.legend(handles=legend_patches, loc="lower center",
             bbox_to_anchor=(0.5, -0.18), fontsize=7.5, ncol=2,
             framealpha=0.5)
ax_dn.set_title("SIP / Lumpsum / Redemption Split",
                fontsize=9.5, fontweight="bold", color=HEADER, pad=4)

# Age group avg SIP bar
ax_ag = fig3.add_axes([0.03, 0.07, 0.42, 0.40])
age_order = ["18-25", "26-35", "36-45", "46-55", "56+"]
age_data  = age_sip.reindex([a for a in age_order if a in age_sip.index])
bar_ag = ax_ag.bar(age_data.index, age_data.values,
                   color=[BLUE, GREEN, ORANGE, PURPLE, TEAL][:len(age_data)],
                   width=0.6)
style_ax(ax_ag, "Age Group vs Avg SIP Amount (₹)",
         xlabel="Age Group", ylabel="Avg SIP Amount (₹)")
ax_ag.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"₹{v:,.0f}"))
for bar in bar_ag:
    ax_ag.text(bar.get_x() + bar.get_width() / 2,
               bar.get_height() + age_data.max() * 0.02,
               f"₹{bar.get_height():,.0f}",
               ha="center", va="bottom", fontsize=7.5, color=HEADER, fontweight="bold")

# Monthly transaction volume line
ax_mv = fig3.add_axes([0.50, 0.07, 0.48, 0.40])
ax_mv.fill_between(monthly_vol["month_dt"], monthly_vol["amount_inr"],
                   alpha=0.12, color=TEAL)
ax_mv.plot(monthly_vol["month_dt"], monthly_vol["amount_inr"],
           color=TEAL, lw=2.0, marker="o", ms=3.5, zorder=3)
style_ax(ax_mv, "Monthly Transaction Volume (₹ Crore)",
         xlabel="Month", ylabel="₹ Crore")
ax_mv.xaxis.set_major_formatter(MDateFormatter("%b '%y"))
ax_mv.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"₹{v:.0f}Cr"))
plt.setp(ax_mv.get_xticklabels(), rotation=30, ha="right")
ax_mv.text(0.98, 0.97, "Slicer: State | Age Group | City Tier",
           transform=ax_mv.transAxes, ha="right", va="top",
           fontsize=6.5, color=GREY, fontstyle="italic")

out3 = os.path.join(OUT, "page3_investor_analytics.png")
fig3.savefig(out3, dpi=DPI, bbox_inches="tight", facecolor=BG)
plt.close(fig3)
print(f"   Saved {out3}")


# ============================================================================
# PAGE 4 — SIP & Market Trends
# ============================================================================
print("\n[4] Rendering Page 4 — SIP & Market Trends ...")

# Dual-axis: SIP inflow (bar) + Nifty 50 (line)
nifty50 = (bm[bm["index_name"] == "NIFTY50"]
           .set_index("date")["close_value"]
           .resample("ME").last()
           .reset_index())
nifty50.columns = ["date", "nifty50"]

sip_m = sip[["month_dt", "sip_inflow_crore"]].copy()
sip_m = sip_m.sort_values("month_dt").reset_index(drop=True)

# Category heatmap: last 12 months
cat_recent = cat[cat["month_dt"] >= cat["month_dt"].max() - pd.DateOffset(months=11)]
hm_data = cat_recent.pivot_table(index="category", columns="month_dt",
                                  values="net_inflow_crore", aggfunc="sum")
hm_data.columns = [d.strftime("%b'%y") for d in hm_data.columns]

# Top 5 categories by net inflow FY25 (Apr 2024 – Mar 2025)
fy25 = cat[(cat["month_dt"] >= "2024-04-01") & (cat["month_dt"] <= "2025-03-31")]
top5_cat = (fy25.groupby("category")["net_inflow_crore"]
            .sum().nlargest(5).sort_values())

fig4 = plt.figure(figsize=(PW, PH), facecolor=BG)
add_header(fig4, "SIP & Market Trends")

# Dual-axis
ax_d = fig4.add_axes([0.05, 0.50, 0.92, 0.42])
ax_d2 = ax_d.twinx()

bars_d = ax_d.bar(sip_m["month_dt"], sip_m["sip_inflow_crore"],
                  width=20, color=BLUE, alpha=0.75, label="SIP Inflow (₹ Cr)", zorder=2)
ax_d.set_ylabel("SIP Inflow (₹ Crore)", fontsize=8, color=BLUE)
ax_d.tick_params(axis="y", colors=BLUE, labelsize=7.5)
ax_d.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"₹{v:,.0f}"))

merged_nifty = pd.merge_asof(sip_m.sort_values("month_dt"),
                              nifty50.sort_values("date"),
                              left_on="month_dt", right_on="date", direction="nearest")
ax_d2.plot(merged_nifty["month_dt"], merged_nifty["nifty50"],
           color=ORANGE, lw=2.2, marker="o", ms=3.5, label="NIFTY 50", zorder=3)
ax_d2.set_ylabel("NIFTY 50 Level", fontsize=8, color=ORANGE)
ax_d2.tick_params(axis="y", colors=ORANGE, labelsize=7.5)
ax_d2.spines["top"].set_visible(False)
ax_d2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))

ax_d.set_facecolor(WHITE)
ax_d.spines[["top"]].set_visible(False)
ax_d.spines[["left", "bottom"]].set_edgecolor(LGREY)
ax_d.spines["right"].set_edgecolor(ORANGE)
ax_d.grid(axis="y", color=LGREY, lw=0.6, alpha=0.7, zorder=0)
ax_d.xaxis.set_major_formatter(MDateFormatter("%b '%y"))
plt.setp(ax_d.get_xticklabels(), rotation=30, ha="right", fontsize=7)
ax_d.set_title("Monthly SIP Inflows vs NIFTY 50 Index (2022–2026)",
               fontsize=9.5, fontweight="bold", color=HEADER, pad=5)

lines_d  = [mpatches.Patch(facecolor=BLUE,   label="SIP Inflow (₹ Cr)"),
            mpatches.Patch(facecolor=ORANGE, label="NIFTY 50")]
ax_d.legend(handles=lines_d, loc="upper left", fontsize=8, framealpha=0.7)

# Category heatmap
ax_hm = fig4.add_axes([0.05, 0.07, 0.52, 0.38])
sns.heatmap(hm_data, ax=ax_hm, cmap="YlOrRd",
            linewidths=0.4, linecolor=BG,
            fmt=".0f", annot=True, annot_kws={"size": 6},
            cbar_kws={"shrink": 0.7, "pad": 0.01})
ax_hm.set_title("Category Inflow Heatmap — Last 12 Months (₹ Crore)",
                fontsize=9.5, fontweight="bold", color=HEADER, pad=5)
ax_hm.set_xlabel(""); ax_hm.set_ylabel("")
ax_hm.tick_params(axis="x", rotation=40, labelsize=6.5)
ax_hm.tick_params(axis="y", rotation=0,  labelsize=7)

# Top 5 categories FY25
ax_t5 = fig4.add_axes([0.62, 0.07, 0.36, 0.38])
colors_t5 = [CAT_PAL.get(c, BLUE) for c in top5_cat.index]
bars_t5 = ax_t5.barh(top5_cat.index, top5_cat.values / 1e3,
                     color=colors_t5, height=0.6)
style_ax(ax_t5, "Top 5 Categories — Net Inflow FY25 (₹ '000 Cr)",
         xlabel="Net Inflow (₹ '000 Crore)", grid="x")
ax_t5.spines["left"].set_visible(False)
ax_t5.tick_params(axis="y", labelsize=8)
for bar in bars_t5:
    w = bar.get_width()
    ax_t5.text(w + top5_cat.max() / 1e3 * 0.02, bar.get_y() + bar.get_height() / 2,
               f"₹{w:.1f}K Cr", va="center", ha="left",
               fontsize=8, color=HEADER, fontweight="bold")

out4 = os.path.join(OUT, "page4_sip_trends.png")
fig4.savefig(out4, dpi=DPI, bbox_inches="tight", facecolor=BG)
plt.close(fig4)
print(f"   Saved {out4}")


# ============================================================================
# Combine into PDF
# ============================================================================
print("\nCombining into Dashboard.pdf ...")
pdf_path = os.path.join(OUT, "Dashboard.pdf")
with PdfPages(pdf_path) as pdf:
    for png in [out1, out2, out3, out4]:
        img = plt.imread(png)
        h, w = img.shape[:2]
        fig_pdf = plt.figure(figsize=(PW, PH))
        fig_pdf.add_axes([0, 0, 1, 1]).imshow(img)
        fig_pdf.axes[0].axis("off")
        pdf.savefig(fig_pdf, dpi=DPI, bbox_inches="tight")
        plt.close(fig_pdf)
    d = pdf.infodict()
    d["Title"]   = "Bluestock Fintech — Mutual Fund Analytics Dashboard"
    d["Author"]  = "Capstone Team: asthananeha2015 / bsoham2704 / Bubai Das"
    d["Subject"] = "Mutual Fund Analytics — Day 6 Dashboard"
print(f"   Saved {pdf_path}")

print("\n" + "="*60)
print("Day 6 Dashboard Export Complete")
print("="*60)
print(f"  page1_industry_overview.png")
print(f"  page2_fund_performance.png")
print(f"  page3_investor_analytics.png")
print(f"  page4_sip_trends.png")
print(f"  Dashboard.pdf")
print(f"\nNote: To create bluestock_mf_dashboard.pbix, open Power BI Desktop,")
print(f"  connect to data/processed/*.csv or bluestock_mf.db via SQLite ODBC,")
print(f"  then recreate these visuals interactively with drill-through enabled.")
