-- ============================================================
-- Default Rate by Customer Segment
-- Business Use: Risk segmentation for pricing and policy
-- ============================================================
WITH age_income_bands AS (
    SELECT
        SK_ID_CURR,
        TARGET,
        AMT_CREDIT,
        AMT_INCOME_TOTAL,
        CASE
            WHEN -DAYS_BIRTH/365 < 25 THEN 'Under 25'
            WHEN -DAYS_BIRTH/365 < 35 THEN '25-34'
            WHEN -DAYS_BIRTH/365 < 50 THEN '35-49'
            WHEN -DAYS_BIRTH/365 < 65 THEN '50-64'
            ELSE '65+'
        END AS AGE_BAND,
        CASE
            WHEN AMT_INCOME_TOTAL < 50000  THEN 'Low (<50K)'
            WHEN AMT_INCOME_TOTAL < 100000 THEN 'Medium (50-100K)'
            WHEN AMT_INCOME_TOTAL < 200000 THEN 'High (100-200K)'
            ELSE 'Very High (>200K)'
        END AS INCOME_BAND
    FROM CREDIT_RISK_DB.ANALYTICS.APPLICATIONS
)
SELECT
    AGE_BAND,
    INCOME_BAND,
    COUNT(*)                                    AS TOTAL_CUSTOMERS,
    SUM(TARGET)                                 AS TOTAL_DEFAULTS,
    ROUND(AVG(TARGET) * 100, 2)                 AS DEFAULT_RATE_PCT,
    ROUND(AVG(AMT_CREDIT), 0)                   AS AVG_LOAN_AMOUNT,
    ROUND(AVG(AMT_INCOME_TOTAL), 0)             AS AVG_INCOME
FROM age_income_bands
GROUP BY AGE_BAND, INCOME_BAND
ORDER BY DEFAULT_RATE_PCT DESC;
