"""
Organizes project files into the 5 required Google Drive submission sub-folders:
  submission/
    Source_Code/
    Datasets/
    Documentation/
    PPT_Slides/
    Demo_Video/

Run from project root:  python organize_submission.py
"""

import os
import shutil
import zipfile
import glob

BASE = os.path.dirname(os.path.abspath(__file__))
SUB  = os.path.join(BASE, "submission")

# ── Create folder structure ──────────────────────────────────
folders = [
    "Source_Code/scripts",
    "Source_Code/notebooks",
    "Source_Code/sql",
    "Datasets/raw",
    "Datasets/processed",
    "Datasets/output_reports",
    "Documentation/charts",
    "PPT_Slides/page_screenshots",
    "Demo_Video",
]
for f in folders:
    os.makedirs(os.path.join(SUB, f), exist_ok=True)

print("Folder structure created.\n")


def copy(src, dst_folder, rename=None):
    src_path = os.path.join(BASE, src)
    if not os.path.exists(src_path):
        print(f"  [SKIP] {src}  (not found)")
        return
    dst_name = rename if rename else os.path.basename(src_path)
    dst_path = os.path.join(SUB, dst_folder, dst_name)
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    shutil.copy2(src_path, dst_path)
    print(f"  [OK]  {src}  -->  submission/{dst_folder}/{dst_name}")


def copy_glob(pattern, dst_folder):
    for src in sorted(glob.glob(os.path.join(BASE, pattern))):
        rel = os.path.relpath(src, BASE)
        copy(rel, dst_folder)


# ============================================================
# 1. SOURCE CODE
# ============================================================
print("=" * 58)
print(" SOURCE CODE")
print("=" * 58)

# Python scripts
for script in [
    "data_ingestion.py",
    "live_nav_fetch.py",
    "data_cleaning.py",
    "db_loader.py",
    "eda_analysis.py",
    "performance_analytics.py",
    "advanced_analytics.py",
    "recommender.py",
]:
    copy(script, "Source_Code/scripts")

copy("dashboard/dashboard_export.py", "Source_Code/scripts")
copy("dashboard/ppt_dashboard.py",    "Source_Code/scripts")

# Notebooks
for nb in [
    "notebooks/01_data_exploration.ipynb",
    "notebooks/02_data_cleaning.ipynb",
    "notebooks/EDA_Analysis.ipynb",
    "notebooks/Performance_Analytics.ipynb",
    "notebooks/Advanced_Analytics.ipynb",
]:
    copy(nb, "Source_Code/notebooks")

# SQL
copy("sql/schema.sql",  "Source_Code/sql")
copy("sql/queries.sql", "Source_Code/sql")

# Requirements
copy("requirements.txt", "Source_Code")

print()


# ============================================================
# 2. DATASETS
# ============================================================
print("=" * 58)
print(" DATASETS")
print("=" * 58)

# Raw CSVs
copy_glob("data/raw/*.csv", "Datasets/raw")

# Live NAV CSVs (if exist)
for f in glob.glob(os.path.join(BASE, "data/raw/live/*.csv")):
    rel = os.path.relpath(f, BASE)
    copy(rel, "Datasets/raw/live")

# Processed / cleaned CSVs
copy_glob("data/processed/*.csv", "Datasets/processed")

# SQLite database
copy("bluestock_mf.db", "Datasets")

# Output analytical reports
for csv in [
    "fund_scorecard.csv",
    "alpha_beta.csv",
    "var_cvar_report.csv",
    "sip_continuity_report.csv",
]:
    copy(csv, "Datasets/output_reports")

print()


# ============================================================
# 3. DOCUMENTATION
# ============================================================
print("=" * 58)
print(" DOCUMENTATION")
print("=" * 58)

copy("reports/data_dictionary.md",       "Documentation")
copy("notebooks/data_quality_notes.md",  "Documentation")
copy("notebooks/day1_quality_summary.md","Documentation")

# All chart PNGs from reports/charts
copy_glob("reports/charts/*.png", "Documentation/charts")

# Write project README into Documentation
readme = """# Bluestock Fintech — Mutual Fund Analytics
## Capstone Project I

**Team:** asthananeha2015 / bsoham2704 / Bubai Das

---

## Project Summary
End-to-end mutual fund analytics pipeline covering 40 Indian mutual fund schemes
from 10 fund houses across 6 categories (Large Cap, Mid Cap, Small Cap, ELSS, Flexi Cap, Liquid/Debt).

## Tech Stack
Python 3.13 | pandas | numpy | matplotlib | seaborn | plotly | SQLAlchemy | SQLite | python-pptx

## Data Sources
- AMFI (Association of Mutual Funds in India)
- mfapi.in (live NAV API)
- NSE / BSE benchmark indices

## Day-by-Day Deliverables
| Day | Task | Key Output |
|-----|------|------------|
| 1 | Data Ingestion | 10 raw CSVs loaded, quality summary |
| 2 | Data Cleaning + SQL | 10 cleaned CSVs, SQLite star schema, 10 SQL queries |
| 3 | EDA | 15 charts (01-15), EDA_Analysis.ipynb |
| 4 | Performance Analytics | fund_scorecard.csv, alpha_beta.csv, 3 charts |
| 5 | Advanced Analytics | VaR/CVaR, Rolling Sharpe, SIP continuity, HHI, recommender |
| 6 | Dashboard | bluestock_mf_dashboard.pptx (5 slides, 16:9) |

## Key Metrics
- Total funds analysed: 40 (Regular + Direct plans)
- NAV history rows: ~46,000 trading days
- Investor transactions: 32,778
- Fund houses: 10
- Benchmark indices: 7 (NIFTY50, NIFTY100, BSE_SMALLCAP, etc.)

## Top Fund (Scorecard): ICICI Pru Midcap Fund Regular — Score 84.5/100
## Best Sharpe: Mirae Asset Large Cap Direct
## Highest VaR risk: SBI Small Cap Direct (-2.69%/day)
## Most diversified by HHI: UTI Mid Cap (HHI 1,241)
"""

with open(os.path.join(SUB, "Documentation", "README.md"), "w", encoding="utf-8") as f:
    f.write(readme)
print("  [OK]  README.md  -->  submission/Documentation/README.md")
print()


# ============================================================
# 4. PPT / SLIDES
# ============================================================
print("=" * 58)
print(" PPT / SLIDES")
print("=" * 58)

copy("dashboard/bluestock_mf_dashboard.pptx", "PPT_Slides")
copy("dashboard/Dashboard.pdf",               "PPT_Slides")

for pg in [
    "dashboard/page1_industry_overview.png",
    "dashboard/page2_fund_performance.png",
    "dashboard/page3_investor_analytics.png",
    "dashboard/page4_sip_trends.png",
]:
    copy(pg, "PPT_Slides/page_screenshots")

print()


# ============================================================
# 5. DEMO VIDEO
# ============================================================
print("=" * 58)
print(" DEMO VIDEO")
print("=" * 58)

demo_note = """DEMO VIDEO — TO BE RECORDED

Please record a 3-5 minute screen walkthrough covering:

1. Open bluestock_mf_dashboard.pptx (PPT_Slides/)
   - Walk through all 4 dashboard pages
   - Explain KPIs: Total AUM ₹81L Cr, SIP Inflows ₹31K Cr, 26.12Cr Folios

2. Open Jupyter notebooks (Source_Code/notebooks/)
   - EDA_Analysis.ipynb  — show key charts (NAV trends, AUM by AMC)
   - Performance_Analytics.ipynb  — show fund scorecard, Sharpe ranking
   - Advanced_Analytics.ipynb  — show VaR/CVaR, rolling Sharpe, SIP continuity

3. Run recommender from terminal:
   cd Source_Code/scripts
   python recommender.py --risk Moderate

4. Show SQLite database:
   Open bluestock_mf.db in DB Browser for SQLite
   Run a sample query from sql/queries.sql

Tools: OBS Studio / Loom / Windows Screen Recorder (Win+G)
Format: MP4, 1920x1080, 3-5 minutes
Upload this video file to the Demo_Video/ folder on Google Drive.
"""

with open(os.path.join(SUB, "Demo_Video", "RECORD_DEMO_HERE.txt"), "w", encoding="utf-8") as f:
    f.write(demo_note)
print("  [OK]  RECORD_DEMO_HERE.txt  -->  submission/Demo_Video/")
print()


# ============================================================
# Create ZIP archive
# ============================================================
print("=" * 58)
print(" Creating ZIP archive ...")
print("=" * 58)

zip_path = os.path.join(BASE, "Bluestock_MF_Analytics_Submission.zip")
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(SUB):
        # Skip __pycache__ etc.
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git")]
        for file in files:
            abs_path = os.path.join(root, file)
            arc_name = os.path.relpath(abs_path, BASE)
            zf.write(abs_path, arc_name)

zip_mb = os.path.getsize(zip_path) / 1e6
print(f"  [OK]  Bluestock_MF_Analytics_Submission.zip  ({zip_mb:.1f} MB)")
print()


# ============================================================
# Summary
# ============================================================
print("=" * 58)
print(" SUBMISSION FOLDER SUMMARY")
print("=" * 58)
for folder in ["Source_Code", "Datasets", "Documentation", "PPT_Slides", "Demo_Video"]:
    fp = os.path.join(SUB, folder)
    count = sum(len(files) for _, _, files in os.walk(fp))
    size  = sum(os.path.getsize(os.path.join(r,f))
                for r,_,files in os.walk(fp) for f in files)
    print(f"  {folder:<20} {count:>3} files   {size/1e6:>6.1f} MB")

print()
print("NEXT STEPS:")
print("  1. Record demo video and add to submission/Demo_Video/")
print("  2. Create Google Drive folder named  'NehaAsthana_Submission'")
print("  3. Upload the 5 sub-folders (or upload the ZIP and extract)")
print("  4. Set sharing: Anyone with the link -> Viewer")
print("  5. Copy link and paste into the submission form")
