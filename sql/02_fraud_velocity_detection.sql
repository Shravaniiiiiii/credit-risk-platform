-- ============================================================
-- High Velocity Transaction Detection
-- Business Use: Real-time fraud monitoring alerts
-- ============================================================
WITH daily_stats AS (
    SELECT
        card1                                           AS CARD_ID,
        COUNT(*)                                        AS TXN_COUNT,
        SUM(TransactionAmt)                             AS TOTAL_AMOUNT,
        MAX(TransactionAmt)                             AS MAX_SINGLE_TXN,
        COUNT(DISTINCT ProductCD)                       AS UNIQUE_PRODUCTS,
        AVG(TransactionAmt)                             AS AVG_TXN_AMOUNT,
        SUM(isFraud)                                    AS FRAUD_COUNT
    FROM CREDIT_RISK_DB.FRAUD.TRANSACTIONS
    GROUP BY card1
),
flagged AS (
    SELECT *,
        NTILE(100) OVER (ORDER BY TXN_COUNT)    AS TXN_PERCENTILE,
        NTILE(100) OVER (ORDER BY TOTAL_AMOUNT) AS AMOUNT_PERCENTILE
    FROM daily_stats
)
SELECT
    CARD_ID,
    TXN_COUNT,
    ROUND(TOTAL_AMOUNT, 2)       AS TOTAL_AMOUNT,
    ROUND(MAX_SINGLE_TXN, 2)    AS MAX_SINGLE_TXN,
    FRAUD_COUNT,
    TXN_PERCENTILE,
    AMOUNT_PERCENTILE,
    CASE WHEN TXN_PERCENTILE > 95 OR AMOUNT_PERCENTILE > 95
         THEN 'HIGH RISK' ELSE 'NORMAL' END AS RISK_FLAG
FROM flagged
WHERE TXN_PERCENTILE > 90 OR AMOUNT_PERCENTILE > 90
ORDER BY TOTAL_AMOUNT DESC
LIMIT 500;
