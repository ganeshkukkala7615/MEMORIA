DROP VIEW IF EXISTS vw_executive_intelligence;

CREATE VIEW vw_executive_intelligence AS

SELECT

    department_name,

    COUNT(*) AS total_decisions,

    SUM(
        CASE
            WHEN risk_band = 'Critical' THEN 1
            ELSE 0
        END
    ) AS critical_decisions,

    SUM(
        CASE
            WHEN risk_band = 'High' THEN 1
            ELSE 0
        END
    ) AS high_risk_decisions,

    SUM(
        CASE
            WHEN risk_band IN ('Critical','High')
            THEN 1
            ELSE 0
        END
    ) AS elevated_risk_decisions,

    ROUND(
        AVG(decision_risk_score),
        2
    ) AS avg_decision_risk,

    ROUND(
        AVG(avg_confidence),
        3
    ) AS avg_confidence,

    ROUND(
        AVG(avg_assumption_error),
        2
    ) AS avg_assumption_error,

    ROUND(
        AVG(avg_outcome_error),
        2
    ) AS avg_outcome_error,

    SUM(incident_count)
        AS total_incidents,

    SUM(recurrence_count)
        AS total_recurrences,

    ROUND(
        SUM(financial_impact),
        2
    ) AS total_financial_impact,

    ROUND(
        SUM(incident_impact),
        2
    ) AS total_incident_impact

FROM vw_decision_risk

GROUP BY department_name;