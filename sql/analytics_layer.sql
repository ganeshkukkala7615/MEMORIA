-- ============================================================
-- MEMORIA ANALYTICAL LAYER
-- ============================================================


-- ============================================================
-- 1. DECISION PERFORMANCE
-- ============================================================

DROP VIEW IF EXISTS vw_decision_performance;

CREATE VIEW vw_decision_performance AS

SELECT
    d.decision_id,
    d.decision_title,
    d.decision_type,
    d.department_id,
    dep.department_name,
    d.decision_date,
    d.strategic_priority,
    d.expected_value,

    COUNT(DISTINCT a.assumption_id)
        AS assumption_count,

    AVG(a.confidence_level)
        AS avg_assumption_confidence,

    AVG(a.variance_pct)
        AS avg_assumption_variance,

    COUNT(DISTINCT o.outcome_id)
        AS outcome_count,

    AVG(o.actual_value)
        AS avg_actual_value,

    AVG(o.variance_pct)
        AS avg_outcome_variance,

    SUM(o.financial_impact)
        AS total_financial_impact,

    AVG(o.success_flag)
        AS outcome_success_rate

FROM decisions d

LEFT JOIN departments dep
    ON d.department_id = dep.department_id

LEFT JOIN assumptions a
    ON d.decision_id = a.decision_id

LEFT JOIN outcomes o
    ON d.decision_id = o.decision_id

GROUP BY
    d.decision_id,
    d.decision_title,
    d.decision_type,
    d.department_id,
    dep.department_name,
    d.decision_date,
    d.strategic_priority,
    d.expected_value;


-- ============================================================
-- 2. DEPARTMENT PERFORMANCE
-- ============================================================

DROP VIEW IF EXISTS vw_department_performance;

CREATE VIEW vw_department_performance AS

SELECT

    dep.department_id,

    dep.department_name,

    dep.business_unit,

    COUNT(DISTINCT e.employee_id)
        AS employee_count,

    COUNT(DISTINCT d.decision_id)
        AS decision_count,

    COUNT(DISTINCT i.initiative_id)
        AS initiative_count,

    COUNT(DISTINCT inc.incident_id)
        AS incident_count,

    COUNT(DISTINCT l.lesson_id)
        AS lesson_count,

    COUNT(DISTINCT ac.action_id)
        AS action_count,

    AVG(o.success_flag)
        AS decision_success_rate,

    AVG(a.variance_pct)
        AS avg_assumption_variance,

    AVG(o.variance_pct)
        AS avg_outcome_variance,

    SUM(o.financial_impact)
        AS total_financial_impact,

    SUM(inc.financial_impact)
        AS total_incident_impact

FROM departments dep

LEFT JOIN employees e
    ON dep.department_id = e.department_id

LEFT JOIN decisions d
    ON dep.department_id = d.department_id

LEFT JOIN initiatives i
    ON d.decision_id = i.decision_id

LEFT JOIN incidents inc
    ON dep.department_id = inc.department_id

LEFT JOIN lessons l
    ON inc.incident_id = l.incident_id

LEFT JOIN actions ac
    ON l.lesson_id = ac.lesson_id

LEFT JOIN outcomes o
    ON d.decision_id = o.decision_id

GROUP BY

    dep.department_id,
    dep.department_name,
    dep.business_unit;


-- ============================================================
-- 3. ASSUMPTION RISK
-- ============================================================

DROP VIEW IF EXISTS vw_assumption_risk;

CREATE VIEW vw_assumption_risk AS

SELECT

    a.assumption_id,

    a.decision_id,

    d.decision_title,

    d.department_id,

    dep.department_name,

    a.assumption_category,

    a.confidence_level,

    a.expected_value,

    a.actual_value,

    a.variance_pct,

    a.status,

    CASE

        WHEN a.confidence_level >= 0.85
             AND ABS(a.variance_pct) >= 20
            THEN 'High Confidence / High Error'

        WHEN a.confidence_level >= 0.85
             AND ABS(a.variance_pct) >= 10
            THEN 'High Confidence / Moderate Error'

        WHEN ABS(a.variance_pct) >= 20
            THEN 'High Error'

        ELSE 'Normal'

    END AS assumption_risk_class

FROM assumptions a

JOIN decisions d
    ON a.decision_id = d.decision_id

JOIN departments dep
    ON d.department_id = dep.department_id;


-- ============================================================
-- 4. INCIDENT RECURRENCE ANALYSIS
-- ============================================================

DROP VIEW IF EXISTS vw_incident_recurrence;

CREATE VIEW vw_incident_recurrence AS

SELECT

    i.incident_id,

    i.department_id,

    dep.department_name,

    i.incident_date,

    i.incident_category,

    i.severity,

    i.root_cause,

    i.financial_impact,

    COUNT(DISTINCT r.recurrence_id)
        AS recurrence_count,

    MAX(
        r.lesson_available_flag
    ) AS lesson_available_flag,

    MAX(
        r.action_available_flag
    ) AS action_available_flag,

    MAX(
        r.recurrence_prevented_flag
    ) AS recurrence_prevented_flag

FROM incidents i

JOIN departments dep
    ON i.department_id = dep.department_id

LEFT JOIN recurrence_events r

    ON i.incident_id =
       r.original_incident_id

GROUP BY

    i.incident_id,

    i.department_id,

    dep.department_name,

    i.incident_date,

    i.incident_category,

    i.severity,

    i.root_cause,

    i.financial_impact;


-- ============================================================
-- 5. LESSON EFFECTIVENESS
-- ============================================================

DROP VIEW IF EXISTS vw_lesson_effectiveness;

CREATE VIEW vw_lesson_effectiveness AS

SELECT

    l.lesson_id,

    l.incident_id,

    i.root_cause,

    i.severity,

    dep.department_name,

    l.lesson_category,

    l.confidence_score,

    l.validated_flag,

    COUNT(DISTINCT ac.action_id)
        AS action_count,

    AVG(ac.effectiveness_score)
        AS avg_action_effectiveness,

    SUM(
        CASE
            WHEN ac.status = 'Completed'
            THEN 1
            ELSE 0
        END
    ) AS completed_actions,

    AVG(
        CASE
            WHEN r.recurrence_prevented_flag = 1
            THEN 1
            ELSE 0
        END
    ) AS recurrence_prevention_rate

FROM lessons l

JOIN incidents i
    ON l.incident_id = i.incident_id

JOIN departments dep
    ON i.department_id = dep.department_id

LEFT JOIN actions ac
    ON l.lesson_id = ac.lesson_id

LEFT JOIN recurrence_events r
    ON i.incident_id =
       r.original_incident_id

GROUP BY

    l.lesson_id,

    l.incident_id,

    i.root_cause,

    i.severity,

    dep.department_name,

    l.lesson_category,

    l.confidence_score,

    l.validated_flag;


-- ============================================================
-- 6. EXECUTIVE KPI
-- ============================================================

DROP VIEW IF EXISTS vw_executive_kpis;

CREATE VIEW vw_executive_kpis AS

SELECT

    (SELECT COUNT(*)
     FROM decisions)
        AS total_decisions,

    (SELECT COUNT(*)
     FROM initiatives)
        AS total_initiatives,

    (SELECT COUNT(*)
     FROM incidents)
        AS total_incidents,

    (SELECT COUNT(*)
     FROM lessons)
        AS total_lessons,

    (SELECT COUNT(*)
     FROM actions)
        AS total_actions,

    (SELECT AVG(success_flag)
     FROM outcomes)
        AS overall_success_rate,

    (SELECT AVG(variance_pct)
     FROM assumptions)
        AS avg_assumption_variance,

    (SELECT SUM(financial_impact)
     FROM outcomes)
        AS total_financial_impact,

    (SELECT SUM(financial_impact)
     FROM incidents)
        AS total_incident_impact,

    (SELECT AVG(effectiveness_score)
     FROM actions)
        AS avg_action_effectiveness,

    (SELECT AVG(recurrence_prevented_flag)
     FROM recurrence_events)
        AS recurrence_prevention_rate;


-- ============================================================
-- 7. ROOT CAUSE ANALYSIS
-- ============================================================

DROP VIEW IF EXISTS vw_root_cause_analysis;

CREATE VIEW vw_root_cause_analysis AS

SELECT

    i.root_cause,

    COUNT(*) AS incident_count,

    COUNT(
        DISTINCT i.department_id
    ) AS departments_affected,

    COUNT(
        DISTINCT i.decision_id
    ) AS decisions_affected,

    SUM(i.financial_impact)
        AS total_financial_impact,

    AVG(i.resolution_days)
        AS avg_resolution_days,

    AVG(
        CASE
            WHEN r.recurrence_id IS NOT NULL
            THEN 1
            ELSE 0
        END
    ) AS recurrence_rate

FROM incidents i

LEFT JOIN recurrence_events r

    ON i.incident_id =
       r.original_incident_id

GROUP BY

    i.root_cause;