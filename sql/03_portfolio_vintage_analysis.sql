-- ============================================================
-- Vintage Analysis — Default rates by loan origination period
-- Business Use: Credit policy effectiveness over time
-- ============================================================
SELECT
    NAME_CONTRACT_TYPE                              AS LOAN_TYPE,
    NAME_INCOME_TYPE                                AS INCOME_TYPE,
    COUNT(*)                                        AS LOAN_COUNT,
    ROUND(SUM(AMT_CREDIT)/1e6, 2)                  AS TOTAL_EXPOSURE_M,
    ROUND(AVG(TARGET)*100, 2)                       AS DEFAULT_RATE_PCT,
    ROUND(AVG(AMT_CREDIT), 0)                       AS AVG_LOAN,
    ROUND(AVG(AMT_ANNUITY), 0)                      AS AVG_ANNUITY,
    ROUND(AVG(AMT_CREDIT/NULLIF(AMT_INCOME_TOTAL,0)), 2) AS AVG_DTI_RATIO
FROM CREDIT_RISK_DB.ANALYTICS.APPLICATIONS
GROUP BY NAME_CONTRACT_TYPE, NAME_INCOME_TYPE
HAVING LOAN_COUNT > 100
