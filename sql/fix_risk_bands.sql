DROP VIEW IF EXISTS vw_decision_risk;

CREATE VIEW vw_decision_risk AS

WITH assumption_metrics AS (

    SELECT
        decision_id,

        AVG(confidence_level) AS avg_confidence,

        AVG(ABS(variance_pct)) AS avg_assumption_variance,

        SUM(
            CASE
                WHEN status IN ('Failed', 'Failure', 'Incorrect')
                THEN 1
                ELSE 0
            END
        ) AS assumption_failures,

        COUNT(*) AS assumption_count

    FROM assumptions

    GROUP BY decision_id
),

outcome_metrics AS (

    SELECT
        decision_id,

        COUNT(*) AS outcome_count,

        SUM(
            CASE
                WHEN success_flag = 0
                THEN 1
                ELSE 0
            END
        ) AS outcome_failures,

        AVG(ABS(variance_pct)) AS avg_outcome_variance,

        SUM(financial_impact) AS financial_impact,

        SUM(operational_impact) AS operational_impact

    FROM outcomes

    GROUP BY decision_id
)

SELECT

    d.decision_id,

    d.decision_title,

    d.decision_type,

    d.department_id,

    dep.department_name,

    d.strategic_priority,

    d.decision_date,

    d.expected_value,

    d.expected_timeframe_days,

    d.status,

    COALESCE(a.avg_confidence, 0) AS avg_assumption_confidence,

    COALESCE(a.avg_assumption_variance, 0)
        AS avg_assumption_variance,

    COALESCE(a.assumption_failures, 0)
        AS assumption_failures,

    COALESCE(a.assumption_count, 0)
        AS assumption_count,

    COALESCE(o.outcome_count, 0)
        AS outcome_count,

    COALESCE(o.outcome_failures, 0)
        AS outcome_failures,

    COALESCE(o.avg_outcome_variance, 0)
        AS avg_outcome_variance,

    COALESCE(o.financial_impact, 0)
        AS financial_impact,

    COALESCE(o.operational_impact, 0)
        AS operational_impact,

    ROUND(

        LEAST(
            100,

            (

                /* Strategic priority: 0–20 */

                CASE
                    WHEN d.strategic_priority = 'Critical'
                        THEN 20
                    WHEN d.strategic_priority = 'High'
                        THEN 15
                    WHEN d.strategic_priority = 'Medium'
                        THEN 10
                    ELSE 5
                END

                +

                /* Assumption confidence risk: 0–20 */

                CASE
                    WHEN COALESCE(a.avg_confidence, 1) < 0.60
                        THEN 20
                    WHEN COALESCE(a.avg_confidence, 1) < 0.70
                        THEN 15
                    WHEN COALESCE(a.avg_confidence, 1) < 0.80
                        THEN 10
                    WHEN COALESCE(a.avg_confidence, 1) < 0.90
                        THEN 5
                    ELSE 0
                END

                +

                /* Assumption variance: 0–20 */

                CASE
                    WHEN COALESCE(a.avg_assumption_variance, 0) >= 30
                        THEN 20
                    WHEN COALESCE(a.avg_assumption_variance, 0) >= 20
                        THEN 15
                    WHEN COALESCE(a.avg_assumption_variance, 0) >= 10
                        THEN 10
                    WHEN COALESCE(a.avg_assumption_variance, 0) >= 5
                        THEN 5
                    ELSE 0
                END

                +

                /* Outcome failure rate: 0–20 */

                CASE
                    WHEN COALESCE(o.outcome_count, 0) = 0
                        THEN 0

                    WHEN
                        CAST(o.outcome_failures AS REAL)
                        / o.outcome_count >= 0.75
                        THEN 20

                    WHEN
                        CAST(o.outcome_failures AS REAL)
                        / o.outcome_count >= 0.50
                        THEN 15

                    WHEN
                        CAST(o.outcome_failures AS REAL)
                        / o.outcome_count >= 0.25
                        THEN 10

                    WHEN
                        CAST(o.outcome_failures AS REAL)
                        / o.outcome_count > 0
                        THEN 5

                    ELSE 0
                END

                +

                /* Outcome variance: 0–20 */

                CASE
                    WHEN COALESCE(o.avg_outcome_variance, 0) >= 30
                        THEN 20
                    WHEN COALESCE(o.avg_outcome_variance, 0) >= 20
                        THEN 15
                    WHEN COALESCE(o.avg_outcome_variance, 0) >= 10
                        THEN 10
                    WHEN COALESCE(o.avg_outcome_variance, 0) >= 5
                        THEN 5
                    ELSE 0
                END

            )

        )

    , 2) AS decision_risk_score,

    CASE

        WHEN (

            CASE
                WHEN d.strategic_priority = 'Critical' THEN 20
                WHEN d.strategic_priority = 'High' THEN 15
                WHEN d.strategic_priority = 'Medium' THEN 10
                ELSE 5
            END

            +

            CASE
                WHEN COALESCE(a.avg_confidence, 1) < 0.60 THEN 20
                WHEN COALESCE(a.avg_confidence, 1) < 0.70 THEN 15
                WHEN COALESCE(a.avg_confidence, 1) < 0.80 THEN 10
                WHEN COALESCE(a.avg_confidence, 1) < 0.90 THEN 5
                ELSE 0
            END

            +

            CASE
                WHEN COALESCE(a.avg_assumption_variance, 0) >= 30 THEN 20
                WHEN COALESCE(a.avg_assumption_variance, 0) >= 20 THEN 15
                WHEN COALESCE(a.avg_assumption_variance, 0) >= 10 THEN 10
                WHEN COALESCE(a.avg_assumption_variance, 0) >= 5 THEN 5
                ELSE 0
            END

            +

            CASE
                WHEN COALESCE(o.outcome_count, 0) = 0 THEN 0
                WHEN CAST(o.outcome_failures AS REAL) / o.outcome_count >= 0.75 THEN 20
                WHEN CAST(o.outcome_failures AS REAL) / o.outcome_count >= 0.50 THEN 15
                WHEN CAST(o.outcome_failures AS REAL) / o.outcome_count >= 0.25 THEN 10
                WHEN CAST(o.outcome_failures AS REAL) / o.outcome_count > 0 THEN 5
                ELSE 0
            END

            +

            CASE
                WHEN COALESCE(o.avg_outcome_variance, 0) >= 30 THEN 20
                WHEN COALESCE(o.avg_outcome_variance, 0) >= 20 THEN 15
                WHEN COALESCE(o.avg_outcome_variance, 0) >= 10 THEN 10
                WHEN COALESCE(o.avg_outcome_variance, 0) >= 5 THEN 5
                ELSE 0
            END

        ) >= 75
            THEN 'Critical'

        WHEN (

            CASE
                WHEN d.strategic_priority = 'Critical' THEN 20
                WHEN d.strategic_priority = 'High' THEN 15
                WHEN d.strategic_priority = 'Medium' THEN 10
                ELSE 5
            END

            +

            CASE
                WHEN COALESCE(a.avg_confidence, 1) < 0.60 THEN 20
                WHEN COALESCE(a.avg_confidence, 1) < 0.70 THEN 15
                WHEN COALESCE(a.avg_confidence, 1) < 0.80 THEN 10
                WHEN COALESCE(a.avg_confidence, 1) < 0.90 THEN 5
                ELSE 0
            END

            +

            CASE
                WHEN COALESCE(a.avg_assumption_variance, 0) >= 30 THEN 20
                WHEN COALESCE(a.avg_assumption_variance, 0) >= 20 THEN 15
                WHEN COALESCE(a.avg_assumption_variance, 0) >= 10 THEN 10
                WHEN COALESCE(a.avg_assumption_variance, 0) >= 5 THEN 5
                ELSE 0
            END

            +

            CASE
                WHEN COALESCE(o.outcome_count, 0) = 0 THEN 0
                WHEN CAST(o.outcome_failures AS REAL) / o.outcome_count >= 0.75 THEN 20
                WHEN CAST(o.outcome_failures AS REAL) / o.outcome_count >= 0.50 THEN 15
                WHEN CAST(o.outcome_failures AS REAL) / o.outcome_count >= 0.25 THEN 10
                WHEN CAST(o.outcome_failures AS REAL) / o.outcome_count > 0 THEN 5
                ELSE 0
            END

            +

            CASE
                WHEN COALESCE(o.avg_outcome_variance, 0) >= 30 THEN 20
                WHEN COALESCE(o.avg_outcome_variance, 0) >= 20 THEN 15
                WHEN COALESCE(o.avg_outcome_variance, 0) >= 10 THEN 10
                WHEN COALESCE(o.avg_outcome_variance, 0) >= 5 THEN 5
                ELSE 0
            END

        ) >= 50
            THEN 'High'

        WHEN (

            CASE
                WHEN d.strategic_priority = 'Critical' THEN 20
                WHEN d.strategic_priority = 'High' THEN 15
                WHEN d.strategic_priority = 'Medium' THEN 10
                ELSE 5
            END

            +

            CASE
                WHEN COALESCE(a.avg_confidence, 1) < 0.60 THEN 20
                WHEN COALESCE(a.avg_confidence, 1) < 0.70 THEN 15
                WHEN COALESCE(a.avg_confidence, 1) < 0.80 THEN 10
                WHEN COALESCE(a.avg_confidence, 1) < 0.90 THEN 5
                ELSE 0
            END

            +

            CASE
                WHEN COALESCE(a.avg_assumption_variance, 0) >= 30 THEN 20
                WHEN COALESCE(a.avg_assumption_variance, 0) >= 20 THEN 15
                WHEN COALESCE(a.avg_assumption_variance, 0) >= 10 THEN 10
                WHEN COALESCE(a.avg_assumption_variance, 0) >= 5 THEN 5
                ELSE 0
            END

            +

            CASE
                WHEN COALESCE(o.outcome_count, 0) = 0 THEN 0
                WHEN CAST(o.outcome_failures AS REAL) / o.outcome_count >= 0.75 THEN 20
                WHEN CAST(o.outcome_failures AS REAL) / o.outcome_count >= 0.50 THEN 15
                WHEN CAST(o.outcome_failures AS REAL) / o.outcome_count >= 0.25 THEN 10
                WHEN CAST(o.outcome_failures AS REAL) / o.outcome_count > 0 THEN 5
                ELSE 0
            END

            +

            CASE
                WHEN COALESCE(o.avg_outcome_variance, 0) >= 30 THEN 20
                WHEN COALESCE(o.avg_outcome_variance, 0) >= 20 THEN 15
                WHEN COALESCE(o.avg_outcome_variance, 0) >= 10 THEN 10
                WHEN COALESCE(o.avg_outcome_variance, 0) >= 5 THEN 5
                ELSE 0
            END

        ) >= 25
            THEN 'Medium'

        ELSE 'Low'

    END AS risk_band

FROM decisions d

JOIN departments dep
    ON d.department_id = dep.department_id

LEFT JOIN assumption_metrics a
    ON d.decision_id = a.decision_id

LEFT JOIN outcome_metrics o
    ON d.decision_id = o.decision_id;