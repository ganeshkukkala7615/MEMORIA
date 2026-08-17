import sqlite3
from datetime import datetime

import pandas as pd


# ============================================================
# MEMORIA — DATA QUALITY ENGINE
# ============================================================

DB_PATH = "database/memoria.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

conn = sqlite3.connect(DB_PATH)


# ============================================================
# RESULTS STORAGE
# ============================================================

results = []


def add_result(
    check_name,
    table_name,
    records_checked,
    records_failed,
    severity="INFO",
    details=""
):
    """
    Store the result of a data-quality check.
    """

    failure_rate = (
        records_failed / records_checked
        if records_checked > 0
        else 0
    )

    results.append(
        {
            "check_name": check_name,
            "table_name": table_name,
            "check_date": datetime.now(),
            "records_checked": records_checked,
            "records_failed": records_failed,
            "failure_rate": round(
                failure_rate,
                6
            ),
            "severity": severity,
            "details": details,
        }
    )


# ============================================================
# CHECK 1 — PRIMARY KEY DUPLICATES
# ============================================================

primary_keys = {
    "departments": "department_id",
    "employees": "employee_id",
    "decisions": "decision_id",
    "assumptions": "assumption_id",
    "initiatives": "initiative_id",
    "experiments": "experiment_id",
    "outcomes": "outcome_id",
    "incidents": "incident_id",
    "lessons": "lesson_id",
    "actions": "action_id",
    "recurrence_events": "recurrence_id",
}


print("\n==============================================")
print("MEMORIA DATA QUALITY ENGINE")
print("==============================================\n")

print("CHECK 1 — PRIMARY KEY INTEGRITY")


for table, primary_key in primary_keys.items():

    df = pd.read_sql_query(
        f"SELECT {primary_key} FROM {table}",
        conn
    )

    total = len(df)

    duplicate_count = int(
        df[primary_key].duplicated().sum()
    )

    if duplicate_count == 0:

        severity = "PASS"

    else:

        severity = "CRITICAL"

    add_result(
        check_name="Primary Key Uniqueness",
        table_name=table,
        records_checked=total,
        records_failed=duplicate_count,
        severity=severity,
        details=f"Key: {primary_key}"
    )

    print(
        f"{table:<22} "
        f"Duplicates: {duplicate_count:>6} "
        f"[{severity}]"
    )


# ============================================================
# CHECK 2 — NULL VALUES
# ============================================================

print("\nCHECK 2 — NULL VALUES")


required_columns = {
    "departments": [
        "department_id",
        "department_name",
        "business_unit",
    ],

    "employees": [
        "employee_id",
        "department_id",
        "employee_name",
    ],

    "decisions": [
        "decision_id",
        "department_id",
        "decision_title",
    ],

    "assumptions": [
        "assumption_id",
        "decision_id",
        "assumption_text",
    ],

    "initiatives": [
        "initiative_id",
        "decision_id",
        "initiative_name",
    ],

    "incidents": [
        "incident_id",
        "department_id",
        "incident_title",
    ],

    "lessons": [
        "lesson_id",
        "lesson_title",
    ],

    "actions": [
        "action_id",
        "lesson_id",
        "action_description",
    ],
}


for table, columns in required_columns.items():

    df = pd.read_sql_query(
        f"SELECT {', '.join(columns)} FROM {table}",
        conn
    )

    total = len(df)

    null_rows = int(
        df.isnull()
        .any(axis=1)
        .sum()
    )

    severity = (
        "PASS"
        if null_rows == 0
        else "WARNING"
    )

    add_result(
        check_name="Required Field Completeness",
        table_name=table,
        records_checked=total,
        records_failed=null_rows,
        severity=severity,
        details=", ".join(columns)
    )

    print(
        f"{table:<22} "
        f"Null rows: {null_rows:>6} "
        f"[{severity}]"
    )


# ============================================================
# CHECK 3 — FOREIGN KEY: EMPLOYEES → DEPARTMENTS
# ============================================================

print("\nCHECK 3 — FOREIGN KEY INTEGRITY")


employee_fk = pd.read_sql_query(
    """
    SELECT e.employee_id
    FROM employees e
    LEFT JOIN departments d
        ON e.department_id = d.department_id
    WHERE d.department_id IS NULL
    """,
    conn
)

failed = len(employee_fk)

add_result(
    check_name="Employee Department Relationship",
    table_name="employees",
    records_checked=10000,
    records_failed=failed,
    severity="PASS" if failed == 0 else "CRITICAL",
    details="employees.department_id → departments.department_id"
)

print(
    f"Employees → Departments: "
    f"{failed} broken relationships"
)


# ============================================================
# CHECK 4 — FOREIGN KEY: DECISIONS → EMPLOYEES
# ============================================================

decision_fk = pd.read_sql_query(
    """
    SELECT d.decision_id
    FROM decisions d
    LEFT JOIN employees e
        ON d.decision_owner_id = e.employee_id
    WHERE e.employee_id IS NULL
    """,
    conn
)

failed = len(decision_fk)

add_result(
    check_name="Decision Owner Relationship",
    table_name="decisions",
    records_checked=20000,
    records_failed=failed,
    severity="PASS" if failed == 0 else "CRITICAL",
    details="decision_owner_id → employees.employee_id"
)

print(
    f"Decisions → Employees: "
    f"{failed} broken relationships"
)


# ============================================================
# CHECK 5 — FOREIGN KEY: ASSUMPTIONS → DECISIONS
# ============================================================

assumption_fk = pd.read_sql_query(
    """
    SELECT a.assumption_id
    FROM assumptions a
    LEFT JOIN decisions d
        ON a.decision_id = d.decision_id
    WHERE d.decision_id IS NULL
    """,
    conn
)

failed = len(assumption_fk)

add_result(
    check_name="Assumption Decision Relationship",
    table_name="assumptions",
    records_checked=40066,
    records_failed=failed,
    severity="PASS" if failed == 0 else "CRITICAL",
    details="assumption.decision_id → decisions.decision_id"
)

print(
    f"Assumptions → Decisions: "
    f"{failed} broken relationships"
)


# ============================================================
# CHECK 6 — FOREIGN KEY: INCIDENTS → DEPARTMENTS
# ============================================================

incident_fk = pd.read_sql_query(
    """
    SELECT i.incident_id
    FROM incidents i
    LEFT JOIN departments d
        ON i.department_id = d.department_id
    WHERE d.department_id IS NULL
    """,
    conn
)

failed = len(incident_fk)

add_result(
    check_name="Incident Department Relationship",
    table_name="incidents",
    records_checked=50000,
    records_failed=failed,
    severity="PASS" if failed == 0 else "CRITICAL",
    details="incident.department_id → departments.department_id"
)

print(
    f"Incidents → Departments: "
    f"{failed} broken relationships"
)


# ============================================================
# CHECK 7 — FOREIGN KEY: LESSONS → INCIDENTS
# ============================================================

lesson_fk = pd.read_sql_query(
    """
    SELECT l.lesson_id
    FROM lessons l
    LEFT JOIN incidents i
        ON l.incident_id = i.incident_id
    WHERE l.incident_id IS NOT NULL
      AND i.incident_id IS NULL
    """,
    conn
)

failed = len(lesson_fk)

add_result(
    check_name="Lesson Incident Relationship",
    table_name="lessons",
    records_checked=30000,
    records_failed=failed,
    severity="PASS" if failed == 0 else "CRITICAL",
    details="lesson.incident_id → incidents.incident_id"
)

print(
    f"Lessons → Incidents: "
    f"{failed} broken relationships"
)


# ============================================================
# CHECK 8 — FOREIGN KEY: ACTIONS → LESSONS
# ============================================================

action_fk = pd.read_sql_query(
    """
    SELECT a.action_id
    FROM actions a
    LEFT JOIN lessons l
        ON a.lesson_id = l.lesson_id
    WHERE l.lesson_id IS NULL
    """,
    conn
)

failed = len(action_fk)

add_result(
    check_name="Action Lesson Relationship",
    table_name="actions",
    records_checked=23962,
    records_failed=failed,
    severity="PASS" if failed == 0 else "CRITICAL",
    details="action.lesson_id → lessons.lesson_id"
)

print(
    f"Actions → Lessons: "
    f"{failed} broken relationships"
)


# ============================================================
# CHECK 9 — NUMERIC RANGE VALIDATION
# ============================================================

print("\nCHECK 4 — NUMERIC RANGE VALIDATION")


# Confidence must be between 0 and 1.
assumption_range = pd.read_sql_query(
    """
    SELECT assumption_id
    FROM assumptions
    WHERE confidence_level < 0
       OR confidence_level > 1
    """,
    conn
)

failed = len(assumption_range)

add_result(
    check_name="Confidence Range",
    table_name="assumptions",
    records_checked=40066,
    records_failed=failed,
    severity="PASS" if failed == 0 else "WARNING",
    details="confidence_level must be between 0 and 1"
)

print(
    f"Assumption confidence: "
    f"{failed} invalid values"
)


# Experiment p-values
experiment_range = pd.read_sql_query(
    """
    SELECT experiment_id
    FROM experiments
    WHERE p_value < 0
       OR p_value > 1
    """,
    conn
)

failed = len(experiment_range)

add_result(
    check_name="P-Value Range",
    table_name="experiments",
    records_checked=5000,
    records_failed=failed,
    severity="PASS" if failed == 0 else "WARNING",
    details="p_value must be between 0 and 1"
)

print(
    f"Experiment p-values: "
    f"{failed} invalid values"
)


# ============================================================
# CHECK 10 — DATE LOGIC
# ============================================================

print("\nCHECK 5 — DATE LOGIC")


initiative_dates = pd.read_sql_query(
    """
    SELECT initiative_id
    FROM initiatives
    WHERE end_date < start_date
    """,
    conn
)

failed = len(initiative_dates)

add_result(
    check_name="Initiative Date Consistency",
    table_name="initiatives",
    records_checked=10000,
    records_failed=failed,
    severity="PASS" if failed == 0 else "CRITICAL",
    details="end_date must be >= start_date"
)

print(
    f"Initiative dates: "
    f"{failed} invalid records"
)


# ============================================================
# CHECK 11 — NEGATIVE FINANCIAL VALUES
# ============================================================

negative_values = pd.read_sql_query(
    """
    SELECT outcome_id
    FROM outcomes
    WHERE expected_value < 0
       OR actual_value < 0
    """,
    conn
)

failed = len(negative_values)

add_result(
    check_name="Outcome Financial Validity",
    table_name="outcomes",
    records_checked=39970,
    records_failed=failed,
    severity="PASS" if failed == 0 else "WARNING",
    details="Expected and actual values should be non-negative"
)

print(
    f"Outcome financial values: "
    f"{failed} invalid records"
)


# ============================================================
# CHECK 12 — ASSUMPTION VARIANCE CONSISTENCY
# ============================================================

variance_check = pd.read_sql_query(
    """
    SELECT assumption_id
    FROM assumptions
    WHERE ABS(
        variance_pct -
        ((actual_value - expected_value)
        / NULLIF(expected_value, 0) * 100)
    ) > 0.1
    """,
    conn
)

failed = len(variance_check)

add_result(
    check_name="Assumption Variance Consistency",
    table_name="assumptions",
    records_checked=40066,
    records_failed=failed,
    severity="PASS" if failed == 0 else "WARNING",
    details="Stored variance must match expected vs actual"
)

print(
    f"Assumption variance: "
    f"{failed} inconsistent records"
)


# ============================================================
# CHECK 13 — OUTCOME VARIANCE CONSISTENCY
# ============================================================

outcome_variance = pd.read_sql_query(
    """
    SELECT outcome_id
    FROM outcomes
    WHERE ABS(
        variance_pct -
        ((actual_value - expected_value)
        / NULLIF(expected_value, 0) * 100)
    ) > 0.1
    """,
    conn
)

failed = len(outcome_variance)

add_result(
    check_name="Outcome Variance Consistency",
    table_name="outcomes",
    records_checked=39970,
    records_failed=failed,
    severity="PASS" if failed == 0 else "WARNING",
    details="Stored variance must match expected vs actual"
)

print(
    f"Outcome variance: "
    f"{failed} inconsistent records"
)


# ============================================================
# CREATE DATA QUALITY REPORT
# ============================================================

results_df = pd.DataFrame(results)


# ============================================================
# OVERALL SCORE
# ============================================================

total_checks = len(results_df)

critical_failures = len(
    results_df[
        results_df["severity"] == "CRITICAL"
    ]
)

warnings = len(
    results_df[
        results_df["severity"] == "WARNING"
    ]
)

passed = len(
    results_df[
        results_df["severity"] == "PASS"
    ]
)


if critical_failures > 0:

    overall_status = "CRITICAL"

elif warnings > 0:

    overall_status = "WARNING"

else:

    overall_status = "PASS"


# ============================================================
# DISPLAY SUMMARY
# ============================================================

print("\n==============================================")
print("DATA QUALITY SUMMARY")
print("==============================================")

print(
    f"Total checks       : {total_checks}"
)

print(
    f"Passed             : {passed}"
)

print(
    f"Warnings           : {warnings}"
)

print(
    f"Critical failures  : {critical_failures}"
)

print(
    f"Overall status     : {overall_status}"
)

print("==============================================")


# ============================================================
# SAVE REPORT
# ============================================================

results_df.to_sql(
    "data_quality_results",
    conn,
    if_exists="replace",
    index=False
)

results_df.to_csv(
    "data_quality_report.csv",
    index=False
)


conn.close()

print("\nReports created:")
print("1. data_quality_report.csv")
print("2. data_quality_results table")
print("\nMEMORIA DATA QUALITY ENGINE COMPLETE.")