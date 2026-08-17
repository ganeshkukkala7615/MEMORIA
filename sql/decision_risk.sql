DROP VIEW IF EXISTS vw_decision_risk;

CREATE VIEW vw_decision_risk AS

WITH assumption_metrics AS (

    SELECT
        decision_id,

        AVG(confidence_level)
            AS avg_confidence,

        AVG(ABS(variance_pct))
            AS avg_assumption_error,

        MAX(ABS(variance_pct))
            AS max_assumption_error,

        COUNT(*) AS assumption_count

    FROM assumptions

    GROUP BY decision_id
),

outcome_metrics AS (

    SELECT
        decision_id,

        AVG(success_flag)
            AS success_rate,

        AVG(ABS(variance_pct))
            AS avg_outcome_error,

        SUM(financial_impact)
            AS financial_impact

    FROM outcomes

    GROUP BY decision_id
),

incident_metrics AS (

    SELECT
        decision_id,

        COUNT(*) AS incident_count,

        SUM(financial_impact)
            AS incident_impact

    FROM incidents

    GROUP BY decision_id
),

recurrence_metrics AS (

    SELECT
        i.decision_id,

        COUNT(r.recurrence_id)
            AS recurrence_count

    FROM incidents i

    LEFT JOIN recurrence_events r
        ON i.incident_id = r.original_incident_id

    GROUP BY i.decision_id
)

SELECT

    d.decision_id,

    d.decision_title,

    d.decision_type,

    d.department_id,

    dep.department_name,

    d.decision_date,

    d.strategic_priority,

    d.expected_value,

    COALESCE(am.avg_confidence, 0)
        AS avg_confidence,

    COALESCE(am.avg_assumption_error, 0)
        AS avg_assumption_error,

    COALESCE(am.max_assumption_error, 0)
        AS max_assumption_error,

    COALESCE(am.assumption_count, 0)
        AS assumption_count,

    COALESCE(om.success_rate, 0)
        AS success_rate,

    COALESCE(om.avg_outcome_error, 0)
        AS avg_outcome_error,

    COALESCE(om.financial_impact, 0)
        AS financial_impact,

    COALESCE(im.incident_count, 0)
        AS incident_count,

    COALESCE(im.incident_impact, 0)
        AS incident_impact,

    COALESCE(rm.recurrence_count, 0)
        AS recurrence_count,


    /* ======================================================
       ASSUMPTION RISK
       ====================================================== */

    ROUND(

        (
            (1 - COALESCE(am.avg_confidence, 0)) * 50

            +

            MIN(
                COALESCE(am.avg_assumption_error, 0),
                50
            )

        ),

        2

    ) AS assumption_risk_score,


    /* ======================================================
       OUTCOME RISK
       ====================================================== */

    ROUND(

        (
            MIN(
                COALESCE(om.avg_outcome_error, 0),
                50
            )

            +

            (1 - COALESCE(om.success_rate, 0)) * 50

        ),

        2

    ) AS outcome_risk_score,


    /* ======================================================
       OPERATIONAL RISK
       ====================================================== */

    ROUND(

        (

            MIN(
                COALESCE(im.incident_count, 0),
                10
            ) * 5

            +

            MIN(
                COALESCE(im.incident_impact, 0) / 10000000,
                25
            )

        ),

        2

    ) AS operational_risk_score,


    /* ======================================================
       RECURRENCE RISK
       ====================================================== */

    ROUND(

        MIN(
            COALESCE(rm.recurrence_count, 0) * 10,
            100
        ),

        2

    ) AS recurrence_risk_score,


    /* ======================================================
       FINAL DECISION RISK
       ====================================================== */

    ROUND(

        (

            (
                (
                    (1 - COALESCE(am.avg_confidence, 0)) * 50

                    +

                    MIN(
                        COALESCE(am.avg_assumption_error, 0),
                        50
                    )
                )

                * 0.35
            )

            +

            (
                (
                    MIN(
                        COALESCE(om.avg_outcome_error, 0),
                        50
                    )

                    +

                    (1 - COALESCE(om.success_rate, 0)) * 50

                )

                * 0.25
            )

            +

            (
                (
                    MIN(
                        COALESCE(im.incident_count, 0),
                        10
                    ) * 5

                    +

                    MIN(
                        COALESCE(im.incident_impact, 0) / 10000000,
                        25
                    )

                )

                * 0.25
            )

            +

            (
                MIN(
                    COALESCE(rm.recurrence_count, 0) * 10,
                    100
                )

                * 0.15
            )

        ),

        2

    ) AS decision_risk_score,


    /* ======================================================
       RISK BAND
       ====================================================== */

    CASE

        WHEN (

            (
                (
                    (1 - COALESCE(am.avg_confidence, 0)) * 50

                    +

                    MIN(
                        COALESCE(am.avg_assumption_error, 0),
                        50
                    )
                ) * 0.35

            )

            +

            (
                (
                    MIN(
                        COALESCE(om.avg_outcome_error, 0),
                        50
                    )

                    +

                    (1 - COALESCE(om.success_rate, 0)) * 50

                ) * 0.25

            )

            +

            (
                (
                    MIN(
                        COALESCE(im.incident_count, 0),
                        10
                    ) * 5

                    +

                    MIN(
                        COALESCE(im.incident_impact, 0) / 10000000,
                        25
                    )

                ) * 0.25

            )

            +

            (
                MIN(
                    COALESCE(rm.recurrence_count, 0) * 10,
                    100
                ) * 0.15
            )

        ) >= 70

        THEN 'Critical'


        WHEN (

            (
                (
                    (1 - COALESCE(am.avg_confidence, 0)) * 50

                    +

                    MIN(
                        COALESCE(am.avg_assumption_error, 0),
                        50
                    )
                ) * 0.35

            )

            +

            (
                (
                    MIN(
                        COALESCE(om.avg_outcome_error, 0),
                        50
                    )

                    +

                    (1 - COALESCE(om.success_rate, 0)) * 50

                ) * 0.25

            )

            +

            (
                (
                    MIN(
                        COALESCE(im.incident_count, 0),
                        10
                    ) * 5

                    +

                    MIN(
                        COALESCE(im.incident_impact, 0) / 10000000,
                        25
                    )

                ) * 0.25

            )

            +

            (
                MIN(
                    COALESCE(rm.recurrence_count, 0) * 10,
                    100
                ) * 0.15
            )

        ) >= 50

        THEN 'High'


        WHEN (

            (
                (
                    (1 - COALESCE(am.avg_confidence, 0)) * 50

                    +

                    MIN(
                        COALESCE(am.avg_assumption_error, 0),
                        50
                    )
                ) * 0.35

            )

            +

            (
                (
                    MIN(
                        COALESCE(om.avg_outcome_error, 0),
                        50
                    )

                    +

                    (1 - COALESCE(om.success_rate, 0)) * 50

                ) * 0.25

            )

            +

            (
                (
                    MIN(
                        COALESCE(im.incident_count, 0),
                        10
                    ) * 5

                    +

                    MIN(
                        COALESCE(im.incident_impact, 0) / 10000000,
                        25
                    )

                ) * 0.25

            )

            +

            (
                MIN(
                    COALESCE(rm.recurrence_count, 0) * 10,
                    100
                ) * 0.15
            )

        ) >= 30

        THEN 'Medium'

        ELSE 'Low'

    END AS risk_band
,

CASE

    WHEN COALESCE(am.avg_assumption_error, 0)
         >= COALESCE(om.avg_outcome_error, 0)

         AND COALESCE(am.avg_assumption_error, 0)
         >= COALESCE(im.incident_count, 0) * 5

         AND COALESCE(am.avg_assumption_error, 0)
         >= COALESCE(rm.recurrence_count, 0) * 10

    THEN 'Assumption Failure'


    WHEN COALESCE(om.avg_outcome_error, 0)
         >= COALESCE(am.avg_assumption_error, 0)

         AND COALESCE(om.avg_outcome_error, 0)
         >= COALESCE(im.incident_count, 0) * 5

         AND COALESCE(om.avg_outcome_error, 0)
         >= COALESCE(rm.recurrence_count, 0) * 10

    THEN 'Outcome Failure'


    WHEN COALESCE(rm.recurrence_count, 0) * 10
         >= COALESCE(im.incident_count, 0) * 5

         AND COALESCE(rm.recurrence_count, 0) > 0

    THEN 'Recurring Problem'


    WHEN COALESCE(im.incident_count, 0) > 0

    THEN 'Operational Failure'


    ELSE 'Low Evidence'

END AS primary_failure_driver

FROM decisions d

JOIN departments dep
    ON d.department_id = dep.department_id

LEFT JOIN assumption_metrics am
    ON d.decision_id = am.decision_id

LEFT JOIN outcome_metrics om
    ON d.decision_id = om.decision_id

LEFT JOIN incident_metrics im
    ON d.decision_id = im.decision_id

LEFT JOIN recurrence_metrics rm
    ON d.decision_id = rm.decision_id;