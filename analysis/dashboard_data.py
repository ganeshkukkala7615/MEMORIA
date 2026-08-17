import sqlite3
import pandas as pd
import os

DB = "database/memoria.db"
OUTPUT = "outputs"

os.makedirs(OUTPUT, exist_ok=True)

conn = sqlite3.connect(DB)

queries = {

    "risk_band": """
    SELECT
        CASE
            WHEN decision_risk_score >= 40 THEN 'High'
            WHEN decision_risk_score >= 30 THEN 'Medium'
            ELSE 'Low'
        END AS risk_band,
        COUNT(*) AS decisions,
        ROUND(AVG(decision_risk_score), 2) AS avg_score,
        MIN(decision_risk_score) AS min_score,
        MAX(decision_risk_score) AS max_score
    FROM vw_decision_risk
    WHERE strategic_priority = 'Critical'
    GROUP BY risk_band
    ORDER BY avg_score DESC
    """,

    "department_risk": """
    SELECT
        department_name,
        COUNT(*) AS high_risk_decisions,
        ROUND(AVG(decision_risk_score), 2) AS avg_score,
        MIN(decision_risk_score) AS min_score,
        MAX(decision_risk_score) AS max_score
    FROM vw_decision_risk
    WHERE strategic_priority = 'Critical'
      AND decision_risk_score >= 40
    GROUP BY department_name
    ORDER BY high_risk_decisions DESC
    """,

    "decision_type_risk": """
    SELECT
        decision_type,
        COUNT(*) AS high_risk_decisions,
        ROUND(AVG(decision_risk_score), 2) AS avg_score,
        MIN(decision_risk_score) AS min_score,
        MAX(decision_risk_score) AS max_score
    FROM vw_decision_risk
    WHERE strategic_priority = 'Critical'
      AND decision_risk_score >= 40
    GROUP BY decision_type
    ORDER BY high_risk_decisions DESC
    """,

    "financial_department": """
   SELECT
       v.department_name,
       COUNT(*) AS high_risk_decisions,
       ROUND(SUM(o.financial_impact), 2) AS total_financial_impact,
       ROUND(AVG(o.financial_impact), 2) AS avg_financial_impact,
       ROUND(AVG(v.decision_risk_score), 2) AS avg_risk_score
  FROM vw_decision_risk v
  JOIN outcomes o
     ON v.decision_id = o.decision_id
  WHERE v.strategic_priority = 'Critical'
  AND v.decision_risk_score >= 40
  GROUP BY v.department_name
  ORDER BY total_financial_impact ASC
    """,

    "financial_decision_type": """
    SELECT
    v.decision_type,
    COUNT(*) AS high_risk_decisions,
    ROUND(SUM(o.financial_impact), 2) AS total_financial_impact,
    ROUND(AVG(o.financial_impact), 2) AS avg_financial_impact,
    ROUND(AVG(v.decision_risk_score), 2) AS avg_risk_score,
    MIN(v.decision_risk_score) AS min_score,
    MAX(v.decision_risk_score) AS max_score
FROM vw_decision_risk v
JOIN outcomes o
    ON v.decision_id = o.decision_id
WHERE v.strategic_priority = 'Critical'
  AND v.decision_risk_score >= 40
GROUP BY v.decision_type
ORDER BY total_financial_impact ASC
    """,

    "outcome_performance": """
    SELECT
        CASE
            WHEN o.success_flag = 1 THEN 'Successful'
            ELSE 'Failed'
        END AS outcome_status,
        COUNT(*) AS outcomes,
        ROUND(AVG(o.variance_pct), 2) AS avg_variance_pct,
        ROUND(SUM(o.financial_impact), 2) AS total_financial_impact,
        ROUND(AVG(o.financial_impact), 2) AS avg_financial_impact
    FROM outcomes o
    JOIN vw_decision_risk v
        ON o.decision_id = v.decision_id
    WHERE v.strategic_priority IN ('Critical', 'High')
      AND v.decision_risk_score >= 40
    GROUP BY outcome_status
    ORDER BY outcomes DESC
    """,

    "assumption_category": """
    SELECT
        a.assumption_category,
        COUNT(*) AS assumptions,
        SUM(
            CASE WHEN a.status = 'Failed'
            THEN 1 ELSE 0 END
        ) AS failed_assumptions,
        ROUND(
            100.0 * SUM(
                CASE WHEN a.status = 'Failed'
                THEN 1 ELSE 0 END
            ) / COUNT(*), 2
        ) AS failure_rate_pct,
        ROUND(AVG(a.variance_pct), 2) AS avg_variance_pct,
        ROUND(AVG(a.confidence_level), 2) AS avg_confidence,
        ROUND(AVG(v.decision_risk_score), 2) AS avg_risk_score
    FROM assumptions a
    JOIN vw_decision_risk v
        ON a.decision_id = v.decision_id
    WHERE v.strategic_priority IN ('Critical', 'High')
    GROUP BY a.assumption_category
    ORDER BY failure_rate_pct DESC
    """,

    "risk_hotspots": """
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
            ) / COUNT(*), 2
        ) AS failure_rate_pct,
        ROUND(AVG(v.decision_risk_score), 2) AS avg_risk_score,
        ROUND(SUM(o.financial_impact), 2) AS total_financial_impact,
        ROUND(AVG(o.financial_impact), 2) AS avg_financial_impact
    FROM vw_decision_risk v
    JOIN outcomes o
        ON v.decision_id = o.decision_id
    WHERE v.strategic_priority IN ('Critical', 'High')
      AND v.decision_risk_score >= 40
    GROUP BY
        v.department_name,
        v.decision_type
    ORDER BY total_financial_impact ASC
    """
}

print("=" * 90)
print("MEMORIA - DASHBOARD DATA GENERATION")
print("=" * 90)

for name, query in queries.items():

    try:
        df = pd.read_sql_query(query, conn)

        path = os.path.join(OUTPUT, name + ".csv")
        df.to_csv(path, index=False)

        print(f"[OK] {name}.csv -> {len(df)} rows")

    except Exception as e:
        print(f"[ERROR] {name}: {e}")

conn.close()

print("=" * 90)
print("DATA EXPORT COMPLETED")
print("=" * 90)