# Data Dictionary — Bluestock MF Analytics

All cleaned files live in `data/processed/`. The SQLite database (`bluestock_mf.db`) mirrors these in a star schema.

---

## 01 — fund_master (dim_fund)

Source: `data/raw/01_fund_master.csv`

| Column | Type | Description |
|---|---|---|
| amfi_code | INTEGER | Unique AMFI scheme code. Primary key. Regular and Direct plans of the same scheme get different codes. |
| fund_house | TEXT | Asset Management Company name (e.g. SBI Mutual Fund, HDFC Mutual Fund). |
| scheme_name | TEXT | Full SEBI-registered scheme name including plan and option. |
| category | TEXT | Broad SEBI category: `Equity` or `Debt`. |
| sub_category | TEXT | SEBI sub-category (e.g. Large Cap, Mid Cap, ELSS, Liquid, Gilt). |
| plan | TEXT | `Regular` (distributor) or `Direct` (investor buys directly, lower expense ratio). |
| launch_date | TEXT | Fund inception date (YYYY-MM-DD). Stored as text in source; converted to datetime in processing. |
| benchmark | TEXT | Index the fund is measured against (e.g. NIFTY 100 TRI). |
| expense_ratio_pct | REAL | Annual fund management fee as % of AUM. Direct plans always lower than Regular. |
| exit_load_pct | REAL | Penalty charged on redemption before a holding period (typically 1%). |
| min_sip_amount | INTEGER | Minimum monthly SIP instalment in INR. |
| min_lumpsum_amount | INTEGER | Minimum one-time investment in INR. |
| fund_manager | TEXT | Name of the lead portfolio manager. |
| risk_category | TEXT | SEBI risk label: Low / Moderate / Moderately High / High / Very High. |
| sebi_category_code | TEXT | SEBI internal category code (e.g. EC01 = Equity Large Cap). |

---

## 02 — nav_history (fact_nav)

Source: `data/raw/02_nav_history.csv`

| Column | Type | Description |
|---|---|---|
| amfi_code | INTEGER | Foreign key → dim_fund. |
| date | TEXT | Calendar date (YYYY-MM-DD). Weekends and exchange holidays forward-filled from last known NAV. |
| nav | REAL | Net Asset Value per unit in INR. Always > 0. |

**Cleaning notes:** Dates parsed to datetime; duplicates removed; calendar gaps filled with `ffill` per fund. Shape grows from 46,000 rows (trading days only) to ~64,000+ rows (daily).

---

## 03 — aum_by_fund_house (fact_aum)

Source: `data/raw/03_aum_by_fund_house.csv`

| Column | Type | Description |
|---|---|---|
| date | TEXT | Semi-annual snapshot date (YYYY-MM-DD), typically Mar/Sep quarter-end. |
| fund_house | TEXT | Asset Management Company name. |
| aum_crore | REAL | Assets Under Management in INR crore at the snapshot date. |
| num_schemes | INTEGER | Number of live schemes managed by the fund house on that date. |

**Cleaning notes:** `aum_lakh_crore` column dropped (redundant — same value as aum_crore ÷ 1 lakh).

---

## 04 — monthly_sip_inflows

Source: `data/raw/04_monthly_sip_inflows.csv`

| Column | Type | Description |
|---|---|---|
| month | TEXT | Month in YYYY-MM format (e.g. 2022-01). |
| sip_inflow_crore | REAL | Total industry-wide SIP inflow for the month in INR crore. |
| active_sip_accounts_crore | REAL | Total active SIP mandates in crore units. |
| new_sip_accounts_lakh | REAL | New SIP registrations in the month, in lakh units. |
| sip_aum_lakh_crore | REAL | Total SIP AUM in lakh-crore INR. |
| yoy_growth_pct | REAL | Year-on-year growth of SIP inflow. NaN for first 12 months (2022) — expected, no prior year. |

---

## 05 — category_inflows

Source: `data/raw/05_category_inflows.csv`

| Column | Type | Description |
|---|---|---|
| month | TEXT | Month in YYYY-MM format. Covers Apr 2024 – Mar 2025. |
| category | TEXT | SEBI fund category (e.g. Large Cap, Mid Cap, ELSS, Hybrid Equity). |
| net_inflow_crore | REAL | Net inflow (purchases minus redemptions) for the category in INR crore. |

---

## 06 — industry_folio_count

Source: `data/raw/06_industry_folio_count.csv`

| Column | Type | Description |
|---|---|---|
| quarter_start | TEXT | Start month of the quarter in YYYY-MM format. Despite "month" naming in source, data is quarterly. |
| total_folios_crore | REAL | Total investor folios (accounts) across all fund types, in crore. |
| equity_folios_crore | REAL | Folios in equity schemes. |
| debt_folios_crore | REAL | Folios in debt schemes. |
| hybrid_folios_crore | REAL | Folios in hybrid schemes. |
| others_folios_crore | REAL | Folios in solution-oriented / other schemes. |

**Cleaning notes:** Column renamed from `month` → `quarter_start` to reflect true quarterly frequency.

---

## 07 — scheme_performance (fact_performance)

Source: `data/raw/07_scheme_performance.csv`

| Column | Type | Description |
|---|---|---|
| amfi_code | INTEGER | Foreign key → dim_fund. |
| scheme_name | TEXT | Scheme name (for reference; amfi_code is the key). |
| fund_house | TEXT | AMC name. |
| category | TEXT | Equity / Debt. |
| plan | TEXT | Regular / Direct. |
| return_1yr_pct | REAL | Trailing 1-year absolute return %. |
| return_3yr_pct | REAL | Trailing 3-year CAGR %. |
| return_5yr_pct | REAL | Trailing 5-year CAGR %. |
| benchmark_3yr_pct | REAL | Benchmark index 3-year CAGR for comparison. |
| alpha | REAL | Jensen's alpha — excess return over benchmark risk-adjusted. |
| beta | REAL | Sensitivity to market (benchmark) movements. |
| sharpe_ratio | REAL | Risk-adjusted return per unit of total risk (std dev). |
| sortino_ratio | REAL | Risk-adjusted return per unit of downside risk. |
| std_dev_ann_pct | REAL | Annualised standard deviation of returns %. |
| max_drawdown_pct | REAL | Maximum peak-to-trough decline %. Always negative. |
| aum_crore | REAL | Scheme AUM in INR crore at reporting date. |
| expense_ratio_pct | REAL | Annual expense ratio %. Valid range: 0.1%–2.5%. |
| morningstar_rating | INTEGER | Morningstar star rating (3–5 in this dataset). |
| risk_grade | TEXT | Risk classification: Low / Moderate / Moderately High / High / Very High. |

---

## 08 — investor_transactions (fact_transactions)

Source: `data/raw/08_investor_transactions.csv`

| Column | Type | Description |
|---|---|---|
| investor_id | TEXT | Anonymised investor identifier (e.g. INV003054). |
| transaction_date | TEXT | Date of transaction (YYYY-MM-DD). |
| amfi_code | INTEGER | Foreign key → dim_fund. |
| transaction_type | TEXT | `SIP` (recurring), `Lumpsum` (one-time purchase), `Redemption` (withdrawal). |
| amount_inr | INTEGER | Transaction amount in INR. Always > 0. |
| state | TEXT | Indian state of the investor. |
| city | TEXT | Investor's city. |
| city_tier | TEXT | `T30` (top 30 cities by AUM) or `B30` (beyond top 30). |
| age_group | TEXT | Investor age bracket (e.g. 18-25, 26-35, 36-45, 46-55, 56+). |
| gender | TEXT | Male / Female. |
| annual_income_lakh | REAL | Self-reported annual income in INR lakh. |
| payment_mode | TEXT | UPI / Net Banking / Cheque / Mandate. |
| kyc_status | TEXT | `Verified` (KYC complete) or `Pending`. |

---

## 09 — portfolio_holdings

Source: `data/raw/09_portfolio_holdings.csv`

| Column | Type | Description |
|---|---|---|
| amfi_code | INTEGER | Foreign key → dim_fund. |
| stock_symbol | TEXT | NSE ticker symbol of the holding. |
| stock_name | TEXT | Company name. |
| sector | TEXT | GICS/custom sector classification (e.g. Banking, IT, Utilities). |
| weight_pct | REAL | Portfolio weight % for this stock. Sum per fund ≈ 100%. |
| market_value_cr | REAL | Market value of holding in INR crore at portfolio_date. |
| current_price_inr | REAL | Stock price in INR at portfolio_date. |
| portfolio_date | TEXT | Disclosure date (YYYY-MM-DD). All entries: 2025-12-31. |

**Note:** 34 of 40 funds have holdings data; 6 newer/smaller funds have no entries.

---

## 10 — benchmark_indices

Source: `data/raw/10_benchmark_indices.csv`

| Column | Type | Description |
|---|---|---|
| date | TEXT | Trading date (YYYY-MM-DD). |
| index_name | TEXT | Index identifier (e.g. NIFTY50, NIFTY100, NIFTY_MIDCAP150). |
| close_value | REAL | Closing index level on that date. |

---

## Star Schema Summary

```
dim_fund ──────┬──── fact_nav
               ├──── fact_transactions
               ├──── fact_performance
               └──── fact_aum

dim_date ──────┬──── fact_nav          (via date)
               ├──── fact_transactions  (via transaction_date)
               └──── fact_aum           (via date)
```
