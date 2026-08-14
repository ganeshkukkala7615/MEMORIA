PRAGMA foreign_keys = ON;

-- ============================================
-- MEMORIA
-- Enterprise Decision Intelligence Platform
-- Core Database Schema
-- ============================================


-- ============================================
-- 1. DEPARTMENTS
-- ============================================

CREATE TABLE departments (
    department_id INTEGER PRIMARY KEY,
    department_name TEXT NOT NULL UNIQUE,
    business_unit TEXT NOT NULL,
    department_head TEXT,
    created_date DATE
);


-- ============================================
-- 2. EMPLOYEES
-- ============================================

CREATE TABLE employees (
    employee_id INTEGER PRIMARY KEY,
    department_id INTEGER NOT NULL,
    employee_name TEXT NOT NULL,
    job_level TEXT,
    role_type TEXT,
    location TEXT,
    joining_date DATE,

    FOREIGN KEY (department_id)
        REFERENCES departments(department_id)
);


-- ============================================
-- 3. DECISIONS
-- ============================================

CREATE TABLE decisions (
    decision_id INTEGER PRIMARY KEY,
    department_id INTEGER NOT NULL,
    decision_owner_id INTEGER,
    decision_title TEXT NOT NULL,
    decision_type TEXT,
    decision_date DATE,
    strategic_priority TEXT,
    expected_outcome TEXT,
    expected_value REAL,
    expected_timeframe_days INTEGER,
    status TEXT,

    FOREIGN KEY (department_id)
        REFERENCES departments(department_id),

    FOREIGN KEY (decision_owner_id)
        REFERENCES employees(employee_id)
);


-- ============================================
-- 4. ASSUMPTIONS
-- ============================================

CREATE TABLE assumptions (
    assumption_id INTEGER PRIMARY KEY,
    decision_id INTEGER NOT NULL,
    assumption_text TEXT NOT NULL,
    assumption_category TEXT,
    confidence_level REAL,
    expected_value REAL,
    actual_value REAL,
    variance_pct REAL,
    status TEXT,

    FOREIGN KEY (decision_id)
        REFERENCES decisions(decision_id)
);


-- ============================================
-- 5. INITIATIVES
-- ============================================

CREATE TABLE initiatives (
    initiative_id INTEGER PRIMARY KEY,
    decision_id INTEGER NOT NULL,
    initiative_name TEXT NOT NULL,
    start_date DATE,
    end_date DATE,
    budget REAL,
    actual_cost REAL,
    owner_id INTEGER,
    status TEXT,

    FOREIGN KEY (decision_id)
        REFERENCES decisions(decision_id),

    FOREIGN KEY (owner_id)
        REFERENCES employees(employee_id)
);


-- ============================================
-- 6. EXPERIMENTS
-- ============================================

CREATE TABLE experiments (
    experiment_id INTEGER PRIMARY KEY,
    decision_id INTEGER,
    initiative_id INTEGER,
    experiment_name TEXT NOT NULL,
    hypothesis TEXT,
    control_group_size INTEGER,
    treatment_group_size INTEGER,
    control_metric REAL,
    treatment_metric REAL,
    uplift_pct REAL,
    p_value REAL,
    confidence_level REAL,
    result TEXT,
    experiment_date DATE,

    FOREIGN KEY (decision_id)
        REFERENCES decisions(decision_id),

    FOREIGN KEY (initiative_id)
        REFERENCES initiatives(initiative_id)
);


-- ============================================
-- 7. OUTCOMES
-- ============================================

CREATE TABLE outcomes (
    outcome_id INTEGER PRIMARY KEY,
    decision_id INTEGER NOT NULL,
    initiative_id INTEGER,
    outcome_date DATE,
    metric_name TEXT NOT NULL,
    expected_value REAL,
    actual_value REAL,
    variance_pct REAL,
    success_flag INTEGER,
    financial_impact REAL,
    operational_impact REAL,

    FOREIGN KEY (decision_id)
        REFERENCES decisions(decision_id),

    FOREIGN KEY (initiative_id)
        REFERENCES initiatives(initiative_id)
);


-- ============================================
-- 8. INCIDENTS
-- ============================================

CREATE TABLE incidents (
    incident_id INTEGER PRIMARY KEY,
    department_id INTEGER NOT NULL,
    decision_id INTEGER,
    initiative_id INTEGER,
    incident_date DATE,
    incident_title TEXT NOT NULL,
    incident_category TEXT,
    severity TEXT,
    root_cause TEXT,
    impact_description TEXT,
    financial_impact REAL,
    resolution_days INTEGER,
    recurrence_flag INTEGER,

    FOREIGN KEY (department_id)
        REFERENCES departments(department_id),

    FOREIGN KEY (decision_id)
        REFERENCES decisions(decision_id),

    FOREIGN KEY (initiative_id)
        REFERENCES initiatives(initiative_id)
);


-- ============================================
-- 9. LESSONS
-- ============================================

CREATE TABLE lessons (
    lesson_id INTEGER PRIMARY KEY,
    incident_id INTEGER,
    decision_id INTEGER,
    lesson_title TEXT NOT NULL,
    lesson_description TEXT,
    lesson_category TEXT,
    confidence_score REAL,
    created_date DATE,
    validated_flag INTEGER,

    FOREIGN KEY (incident_id)
        REFERENCES incidents(incident_id),

    FOREIGN KEY (decision_id)
        REFERENCES decisions(decision_id)
);


-- ============================================
-- 10. ACTIONS
-- ============================================

CREATE TABLE actions (
    action_id INTEGER PRIMARY KEY,
    lesson_id INTEGER NOT NULL,
    action_owner_id INTEGER,
    action_description TEXT NOT NULL,
    action_date DATE,
    due_date DATE,
    completion_date DATE,
    status TEXT,
    effectiveness_score REAL,

    FOREIGN KEY (lesson_id)
        REFERENCES lessons(lesson_id),

    FOREIGN KEY (action_owner_id)
        REFERENCES employees(employee_id)
);


-- ============================================
-- 11. RECURRENCE EVENTS
-- ============================================

CREATE TABLE recurrence_events (
    recurrence_id INTEGER PRIMARY KEY,
    original_incident_id INTEGER NOT NULL,
    recurring_incident_id INTEGER NOT NULL,
    days_between INTEGER,
    same_root_cause_flag INTEGER,
    same_department_flag INTEGER,
    lesson_available_flag INTEGER,
    action_available_flag INTEGER,
    recurrence_prevented_flag INTEGER,

    FOREIGN KEY (original_incident_id)
        REFERENCES incidents(incident_id),

    FOREIGN KEY (recurring_incident_id)
        REFERENCES incidents(incident_id)
);


-- ============================================
-- 12. DATA QUALITY LOG
-- ============================================

CREATE TABLE data_quality_log (
    quality_id INTEGER PRIMARY KEY,
    table_name TEXT NOT NULL,
    check_name TEXT NOT NULL,
    check_date DATETIME,
    records_checked INTEGER,
    records_failed INTEGER,
    failure_rate REAL,
    quality_status TEXT
);