## 01_fund_master.csv
- Shape: 40 rows, 15 columns
- launch_date is stored as text (str), not a proper date — will need conversion later
- No major issues otherwise; one row per fund+plan combination (e.g. same scheme has separate Regular/Direct rows)
## 02_nav_history.csv
- Shape: 46,000 rows, 3 columns (amfi_code, date, nav)
- date is stored as text (str), needs conversion to datetime later
- nav is correctly float64
- One row per fund per day — clean time-series structure
## 03_aum_by_fund_house.csv
- Shape: (?, 5) — confirm exact row count
- date stored as text (str) — same recurring issue as other files
- aum_lakh_crore and aum_crore represent the same value in different units (lakh-crore vs crore) — redundant, pick one for analysis
- Need to verify fund_house naming matches fund_master.csv exactly later
## 04_monthly_sip_inflows.csv
- Shape: (48, 6) — Jan 2022 to Dec 2025, monthly industry SIP data
- month stored as text (str) — recurring issue
- yoy_growth_pct has exactly 12 NaN values — EXPECTED, first 12 months (2022) have no prior-year data to compare against. Not a data quality issue.
- Later months show healthy YoY growth (~17-20%), consistent with India's SIP growth trend
## 05_category_inflows.csv
- Shape: (144, 3) = 12 categories × 12 months — clean grid, no gaps
- month stored as text (str) — recurring issue
- Likely covers one financial year (Apr 2024 - Mar 2025), need to confirm exact month range
- 12 categories span equity/debt/hybrid types — useful for category-level analysis later
## 06_industry_folio_count.csv
- Shape: (21, 6)
- month stored as text (str) — recurring issue
- IMPORTANT: column named "month" but data is actually QUARTERLY (Jan, Apr, Jul, Oct pattern) — not a gap, just lower frequency than the name suggests
- Steady folio growth over time, consistent with known industry trend
## 07_scheme_performance.csv
- Shape: (40, 19) — one row per fund, rich performance metrics
- ZERO missing values across all 19 columns — fully clean dataset
- No date columns
- morningstar_rating range: 3-5 (no 1-2 star funds in this list)
- risk_grade: 5 clean categories (Low, Moderate, Moderately High, High, Very High) — no inconsistencies
## 08_investor_transactions.csv
- Shape: (32778, 13) — largest file, investor-level transaction records
- transaction_date stored as text (str) — recurring issue
- ZERO missing values across all columns
- AMFI code validation: all 40 unique codes in transactions match fund_master exactly — 0 invalid, 0% mismatch
- Rich demographic fields: state, city, city_tier (T30/B30), age_group, gender, income, payment_mode, kyc_status
## 09_portfolio_holdings.csv
- Shape: (322, 8) — avg ~9-10 holdings per fund across 34 funds
- portfolio_date stored as text (str) — recurring issue
- ZERO missing values
- weight_pct sums to ~100% per fund for all funds — clean, no broken portfolios
- AMFI code validation: all 34 codes valid, exist in fund_master — 0 mismatches
- NOTE: only 34 of 40 funds have holdings data — 6 funds (likely newer/smaller) have no holdings entries at all. Not invalid data, just incomplete coverage.