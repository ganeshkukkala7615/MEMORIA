import sqlite3
import pandas as pd

conn = sqlite3.connect("database/memoria.db")

print("CRITICAL + HIGH RISK - RISK HOTSPOTS")
print("=" * 110)

query = """
SELECT
    v.department_name,
    v.decision_type,

    COUNT(*) AS high_risk_decisions,

    SUM(
        CASE
            WHEN o.success_flag = 0 THEN 1
            ELSE 0
        END
    ) AS failed_outcomes,

    ROUND(
        100.0 * SUM(
            CASE
                WHEN o.success_flag = 0 THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS failure_rate_pct,

    ROUND(AVG(v.decision_risk_score), 2) AS avg_risk_score,

    ROUND(SUM(o.financial_impact), 2)
        AS total_financial_impact,

    ROUND(AVG(o.financial_impact), 2)
        AS avg_financial_impact

FROM vw_decision_risk v

JOIN outcomes o
    ON v.decision_id = o.decision_id

WHERE v.strategic_priority IN ('Critical', 'High')
  AND v.decision_risk_score >= 40

GROUP BY
    v.department_name,
    v.decision_type

ORDER BY
    total_financial_impact ASC
"""

try:
    df = pd.read_sql_query(query, conn)

    if df.empty:
        print("NO RESULTS FOUND")
    else:
        print(df.to_string(index=False))

except Exception as e:
    print("ERROR:")
    print(e)

finally:
    conn.close()