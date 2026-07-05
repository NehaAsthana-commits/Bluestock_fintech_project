-- ============================================================
-- Bluestock MF Analytics — 10 Analytical SQL Queries
-- Database: bluestock_mf.db
-- ============================================================

-- ── Q1: Top 5 funds by AUM (from scheme_performance snapshot) ─────────────

SELECT
    f.fund_house,
    f.scheme_name,
    f.plan,
    p.aum_crore
FROM fact_performance p
JOIN dim_fund f ON f.amfi_code = p.amfi_code
ORDER BY p.aum_crore DESC
LIMIT 5;

-- ── Q2: Average NAV per month across all funds ────────────────────────────

SELECT
    d.year,
    d.month,
    d.month_name,
    ROUND(AVG(n.nav), 4) AS avg_nav
FROM fact_nav n
JOIN dim_date d ON d.date = n.date
GROUP BY d.year, d.month
ORDER BY d.year, d.month;

-- ── Q3: SIP inflow YoY growth (from investor_transactions) ───────────────

SELECT
    d.year,
    ROUND(SUM(t.amount_inr) / 1e7, 2) AS total_sip_crore
FROM fact_transactions t
JOIN dim_date d ON d.date = t.transaction_date
WHERE t.transaction_type = 'SIP'
GROUP BY d.year
ORDER BY d.year;

-- ── Q4: Transaction count and total amount by state ───────────────────────

SELECT
    state,
    COUNT(*)                          AS num_transactions,
    ROUND(SUM(amount_inr) / 1e7, 2)  AS total_amount_crore
FROM fact_transactions
GROUP BY state
ORDER BY total_amount_crore DESC;

-- ── Q5: Funds with expense_ratio < 1% (low-cost funds) ───────────────────

SELECT
    f.fund_house,
    f.scheme_name,
    f.plan,
    p.expense_ratio_pct,
    p.return_3yr_pct,
    p.morningstar_rating
FROM fact_performance p
JOIN dim_fund f ON f.amfi_code = p.amfi_code
WHERE p.expense_ratio_pct < 1.0
ORDER BY p.expense_ratio_pct;

-- ── Q6: Best performing funds by 3-year return (top 10) ──────────────────

SELECT
    f.fund_house,
    f.scheme_name,
    f.category,
    f.sub_category,
    p.return_3yr_pct,
    p.alpha,
    p.sharpe_ratio
FROM fact_performance p
JOIN dim_fund f ON f.amfi_code = p.amfi_code
ORDER BY p.return_3yr_pct DESC
LIMIT 10;

-- ── Q7: Fund house AUM trend over time ────────────────────────────────────

SELECT
    a.fund_house,
    a.date,
    a.aum_crore
FROM fact_aum a
ORDER BY a.fund_house, a.date;

-- ── Q8: Transaction breakdown by type and city tier (T30 vs B30) ──────────

SELECT
    transaction_type,
    city_tier,
    COUNT(*)                          AS num_transactions,
    ROUND(AVG(amount_inr), 0)         AS avg_amount_inr,
    ROUND(SUM(amount_inr) / 1e7, 2)  AS total_amount_crore
FROM fact_transactions
GROUP BY transaction_type, city_tier
ORDER BY transaction_type, city_tier;

-- ── Q9: NAV growth rate — latest vs 1 year ago for each fund ─────────────

WITH latest AS (
    SELECT amfi_code, nav AS nav_latest, date AS latest_date
    FROM fact_nav
    WHERE date = (SELECT MAX(date) FROM fact_nav)
),
year_ago AS (
    SELECT n.amfi_code, n.nav AS nav_1yr_ago
    FROM fact_nav n
    JOIN (SELECT amfi_code, MIN(ABS(JULIANDAY(date) - JULIANDAY(
              (SELECT MAX(date) FROM fact_nav), '-365 days'))) AS diff
          FROM fact_nav
          GROUP BY amfi_code) closest ON closest.amfi_code = n.amfi_code
    WHERE ABS(JULIANDAY(n.date) - JULIANDAY(
              (SELECT MAX(date) FROM fact_nav), '-365 days')) = closest.diff
)
SELECT
    f.fund_house,
    f.scheme_name,
    f.plan,
    l.nav_latest,
    y.nav_1yr_ago,
    ROUND((l.nav_latest - y.nav_1yr_ago) / y.nav_1yr_ago * 100, 2) AS return_1yr_pct
FROM latest l
JOIN year_ago y ON y.amfi_code = l.amfi_code
JOIN dim_fund f ON f.amfi_code = l.amfi_code
ORDER BY return_1yr_pct DESC;

-- ── Q10: Risk-adjusted return — funds ranked by Sharpe ratio ─────────────

SELECT
    f.fund_house,
    f.scheme_name,
    f.sub_category,
    p.sharpe_ratio,
    p.sortino_ratio,
    p.beta,
    p.max_drawdown_pct,
    p.risk_grade
FROM fact_performance p
JOIN dim_fund f ON f.amfi_code = p.amfi_code
ORDER BY p.sharpe_ratio DESC;
