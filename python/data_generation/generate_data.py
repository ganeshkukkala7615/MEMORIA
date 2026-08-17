import sqlite3
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


# ============================================================
# MEMORIA — Synthetic Enterprise Data Generator
# ============================================================

SEED = 42

random.seed(SEED)
np.random.seed(SEED)

DB_PATH = "database/memoria.db"


# ============================================================
# CONFIGURATION
# ============================================================

NUM_EMPLOYEES = 10000
NUM_DECISIONS = 20000
NUM_INITIATIVES = 10000
NUM_EXPERIMENTS = 5000
NUM_INCIDENTS = 50000

START_DATE = pd.Timestamp("2021-01-01")
END_DATE = pd.Timestamp("2026-06-30")


# ============================================================
# REFERENCE DATA
# ============================================================

departments = [
    ("Finance", "Corporate"),
    ("Operations", "Operations"),
    ("Technology", "Technology"),
    ("Product", "Product"),
    ("Marketing", "Commercial"),
    ("Sales", "Commercial"),
    ("Human Resources", "Corporate"),
    ("Risk", "Corporate"),
    ("Procurement", "Operations"),
    ("Customer Experience", "Commercial"),
    ("Strategy", "Corporate"),
    ("Data & Analytics", "Technology"),
    ("Legal", "Corporate"),
    ("Quality", "Operations"),
    ("Research", "Technology"),
]

locations = [
    "Bengaluru",
    "Chennai",
    "Hyderabad",
    "Mumbai",
    "Delhi",
    "Pune",
    "Gurugram",
    "Kolkata",
    "Singapore",
    "London",
    "New York",
]

first_names = [
    "Aarav", "Arjun", "Rahul", "Vikram", "Aditya",
    "Rohan", "Karan", "Nikhil", "Varun", "Siddharth",
    "Ananya", "Priya", "Meera", "Sneha", "Kavya",
    "Isha", "Neha", "Riya", "Aditi", "Divya"
]

last_names = [
    "Sharma", "Reddy", "Kumar", "Patel", "Singh",
    "Rao", "Nair", "Iyer", "Mehta", "Gupta",
    "Kapoor", "Joshi", "Verma", "Menon", "Das"
]

decision_types = [
    "Investment",
    "Pricing",
    "Hiring",
    "Technology",
    "Process Change",
    "Product Launch",
    "Policy Change",
    "Vendor Selection",
    "Capacity Planning",
    "Strategic Initiative",
]

priorities = [
    "Critical",
    "High",
    "Medium",
    "Low",
]

job_levels = [
    "Analyst",
    "Senior Analyst",
    "Manager",
    "Senior Manager",
    "Director",
    "Vice President",
]

role_types = [
    "Individual Contributor",
    "People Manager",
    "Technical Specialist",
    "Business Specialist",
]

assumption_categories = [
    "Demand",
    "Cost",
    "Customer Behavior",
    "Technology",
    "Timeline",
    "Resource",
    "Market",
    "Operational",
]

incident_categories = [
    "Process Failure",
    "Technology Failure",
    "Resource Constraint",
    "Quality Issue",
    "Planning Error",
    "Communication Failure",
    "Vendor Issue",
    "Data Issue",
    "Policy Failure",
]

severities = [
    "Low",
    "Medium",
    "High",
    "Critical",
]

lesson_categories = [
    "Process",
    "Technology",
    "People",
    "Planning",
    "Governance",
    "Data",
    "Risk",
]

status_values = [
    "Completed",
    "In Progress",
    "Cancelled",
    "Delayed",
]

# Root causes deliberately reused across departments.
# This allows MEMORIA to discover hidden organizational patterns.
root_causes = [
    "Poor demand forecasting",
    "Late stakeholder involvement",
    "Insufficient testing",
    "Unclear ownership",
    "Inadequate documentation",
    "Poor communication",
    "Insufficient training",
    "Incorrect assumptions",
    "Weak monitoring",
    "Inadequate risk assessment",
    "Data quality problems",
    "Vendor dependency",
    "Resource underestimation",
    "Timeline compression",
    "Change management failure",
]


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def random_date():
    days = (END_DATE - START_DATE).days
    return (
        START_DATE
        + pd.Timedelta(days=random.randint(0, days))
    ).date()


def random_name():
    return f"{random.choice(first_names)} {random.choice(last_names)}"


def random_text(prefix, item_id):
    return f"{prefix} {item_id}"


# ============================================================
# 1. DEPARTMENTS
# ============================================================

department_rows = []

for department_id, (department_name, business_unit) in enumerate(
    departments, start=1
):
    department_rows.append(
        {
            "department_id": department_id,
            "department_name": department_name,
            "business_unit": business_unit,
            "department_head": random_name(),
            "created_date": "2021-01-01",
        }
    )

departments_df = pd.DataFrame(department_rows)


# ============================================================
# 2. EMPLOYEES
# ============================================================

employee_rows = []

for employee_id in range(1, NUM_EMPLOYEES + 1):

    department_id = random.randint(1, len(departments))

    employee_rows.append(
        {
            "employee_id": employee_id,
            "department_id": department_id,
            "employee_name": random_name(),
            "job_level": random.choice(job_levels),
            "role_type": random.choice(role_types),
            "location": random.choice(locations),
            "joining_date": random_date(),
        }
    )

employees_df = pd.DataFrame(employee_rows)


# ============================================================
# 3. DECISIONS
# ============================================================

decision_rows = []

for decision_id in range(1, NUM_DECISIONS + 1):

    department_id = random.randint(1, len(departments))

    owner_pool = employees_df[
        employees_df["department_id"] == department_id
    ]

    owner_id = int(
        owner_pool.sample(1)["employee_id"].iloc[0]
    )

    decision_type = random.choice(decision_types)

    expected_value = round(
        np.random.lognormal(mean=11, sigma=1.0),
        2
    )

    decision_rows.append(
        {
            "decision_id": decision_id,
            "department_id": department_id,
            "decision_owner_id": owner_id,
            "decision_title": random_text(
                decision_type + " Decision",
                decision_id
            ),
            "decision_type": decision_type,
            "decision_date": random_date(),
            "strategic_priority": random.choice(priorities),
            "expected_outcome": (
                f"Improve {decision_type.lower()} performance"
            ),
            "expected_value": expected_value,
            "expected_timeframe_days": random.randint(30, 365),
            "status": random.choice(
                ["Completed", "In Progress", "Delayed"]
            ),
        }
    )

decisions_df = pd.DataFrame(decision_rows)


# ============================================================
# 4. ASSUMPTIONS
# ============================================================

assumption_rows = []

assumption_id = 1

for _, decision in decisions_df.iterrows():

    number_of_assumptions = random.randint(1, 3)

    for _ in range(number_of_assumptions):

        category = random.choice(assumption_categories)

        expected = round(
            np.random.normal(100, 20),
            2
        )

        # Certain departments systematically overestimate outcomes.
        # This creates a hidden pattern for later analysis.
        if decision["department_id"] in [2, 5, 9]:
            actual = expected * np.random.uniform(0.65, 0.90)
        else:
            actual = expected * np.random.uniform(0.80, 1.20)

        variance = ((actual - expected) / expected) * 100

        confidence = random.uniform(0.55, 0.98)

        if abs(variance) <= 10:
            status = "Validated"
        elif abs(variance) <= 25:
            status = "Partially Validated"
        else:
            status = "Failed"

        assumption_rows.append(
            {
                "assumption_id": assumption_id,
                "decision_id": int(decision["decision_id"]),
                "assumption_text": (
                    f"{category} assumption for decision "
                    f"{decision['decision_id']}"
                ),
                "assumption_category": category,
                "confidence_level": round(confidence, 3),
                "expected_value": expected,
                "actual_value": round(actual, 2),
                "variance_pct": round(variance, 2),
                "status": status,
            }
        )

        assumption_id += 1

assumptions_df = pd.DataFrame(assumption_rows)


# ============================================================
# 5. INITIATIVES
# ============================================================

initiative_rows = []

for initiative_id in range(1, NUM_INITIATIVES + 1):

    decision_id = random.randint(1, NUM_DECISIONS)

    start_date = random_date()
    end_date = start_date + timedelta(
        days=random.randint(30, 365)
    )

    budget = round(
        np.random.lognormal(mean=12, sigma=1.0),
        2
    )

    actual_cost = budget * random.uniform(0.75, 1.35)

    owner_id = random.randint(1, NUM_EMPLOYEES)

    initiative_rows.append(
        {
            "initiative_id": initiative_id,
            "decision_id": decision_id,
            "initiative_name": (
                f"Enterprise Initiative {initiative_id}"
            ),
            "start_date": start_date,
            "end_date": end_date,
            "budget": round(budget, 2),
            "actual_cost": round(actual_cost, 2),
            "owner_id": owner_id,
            "status": random.choice(status_values),
        }
    )

initiatives_df = pd.DataFrame(initiative_rows)


# ============================================================
# 6. EXPERIMENTS
# ============================================================

experiment_rows = []

for experiment_id in range(1, NUM_EXPERIMENTS + 1):

    decision_id = random.randint(1, NUM_DECISIONS)

    initiative_id = random.randint(1, NUM_INITIATIVES)

    control_size = random.randint(500, 10000)
    treatment_size = random.randint(500, 10000)

    control_metric = random.uniform(5, 50)

    uplift = np.random.normal(0.08, 0.12)

    treatment_metric = control_metric * (1 + uplift)

    uplift_pct = (
        (treatment_metric - control_metric)
        / control_metric
    ) * 100

    p_value = random.uniform(0.001, 0.25)

    if p_value < 0.05 and uplift > 0:
        result = "Successful"
    elif p_value < 0.05 and uplift < 0:
        result = "Negative"
    else:
        result = "Inconclusive"

    experiment_rows.append(
        {
            "experiment_id": experiment_id,
            "decision_id": decision_id,
            "initiative_id": initiative_id,
            "experiment_name": (
                f"Experiment {experiment_id}"
            ),
            "hypothesis": (
                "Intervention will improve the target metric"
            ),
            "control_group_size": control_size,
            "treatment_group_size": treatment_size,
            "control_metric": round(control_metric, 4),
            "treatment_metric": round(treatment_metric, 4),
            "uplift_pct": round(uplift_pct, 2),
            "p_value": round(p_value, 4),
            "confidence_level": 1 - p_value,
            "result": result,
            "experiment_date": random_date(),
        }
    )

experiments_df = pd.DataFrame(experiment_rows)


# ============================================================
# 7. OUTCOMES
# ============================================================

outcome_rows = []

outcome_id = 1

for _, decision in decisions_df.iterrows():

    number_of_metrics = random.randint(1, 3)

    for _ in range(number_of_metrics):

        expected = decision["expected_value"]

        # Create realistic outcome variation.
        actual = expected * np.random.normal(0.92, 0.20)

        variance = (
            (actual - expected)
            / expected
        ) * 100

        success = 1 if variance >= -10 else 0

        financial_impact = (
            actual - expected
        )

        outcome_rows.append(
            {
                "outcome_id": outcome_id,
                "decision_id": int(decision["decision_id"]),
                "initiative_id": random.randint(
                    1,
                    NUM_INITIATIVES
                ),
                "outcome_date": random_date(),
                "metric_name": random.choice(
                    [
                        "Revenue",
                        "Cost",
                        "Efficiency",
                        "Quality",
                        "Customer Satisfaction",
                        "Productivity",
                    ]
                ),
                "expected_value": round(expected, 2),
                "actual_value": round(actual, 2),
                "variance_pct": round(variance, 2),
                "success_flag": success,
                "financial_impact": round(
                    financial_impact,
                    2
                ),
                "operational_impact": round(
                    random.uniform(-100, 100),
                    2
                ),
            }
        )

        outcome_id += 1

outcomes_df = pd.DataFrame(outcome_rows)


# ============================================================
# 8. INCIDENTS
# ============================================================

incident_rows = []

for incident_id in range(1, NUM_INCIDENTS + 1):

    department_id = random.randint(1, len(departments))

    decision_id = random.randint(1, NUM_DECISIONS)

    initiative_id = random.randint(1, NUM_INITIATIVES)

    # Certain root causes occur more frequently.
    if random.random() < 0.45:
        root_cause = random.choice(
            [
                "Poor communication",
                "Unclear ownership",
                "Poor demand forecasting",
                "Insufficient testing",
            ]
        )
    else:
        root_cause = random.choice(root_causes)

    severity = random.choices(
        severities,
        weights=[45, 35, 15, 5]
    )[0]

    financial_impact = {
        "Low": random.uniform(1000, 10000),
        "Medium": random.uniform(10000, 100000),
        "High": random.uniform(100000, 1000000),
        "Critical": random.uniform(1000000, 5000000),
    }[severity]

    incident_rows.append(
        {
            "incident_id": incident_id,
            "department_id": department_id,
            "decision_id": decision_id,
            "initiative_id": initiative_id,
            "incident_date": random_date(),
            "incident_title": (
                f"{root_cause} Incident {incident_id}"
            ),
            "incident_category": random.choice(
                incident_categories
            ),
            "severity": severity,
            "root_cause": root_cause,
            "impact_description": (
                f"Operational impact caused by {root_cause}"
            ),
            "financial_impact": round(
                financial_impact,
                2
            ),
            "resolution_days": random.randint(1, 90),
            "recurrence_flag": 0,
        }
    )

incidents_df = pd.DataFrame(incident_rows)


# ============================================================
# 9. LESSONS
# ============================================================

lesson_rows = []

lesson_id = 1

# Only some incidents generate lessons.
lesson_incidents = incidents_df.sample(
    frac=0.60,
    random_state=SEED
)

for _, incident in lesson_incidents.iterrows():

    validated = (
        1 if random.random() < 0.75 else 0
    )

    lesson_rows.append(
        {
            "lesson_id": lesson_id,
            "incident_id": int(
                incident["incident_id"]
            ),
            "decision_id": int(
                incident["decision_id"]
            ),
            "lesson_title": (
                f"Lesson from Incident "
                f"{incident['incident_id']}"
            ),
            "lesson_description": (
                f"Future initiatives should address "
                f"{incident['root_cause']}"
            ),
            "lesson_category": random.choice(
                lesson_categories
            ),
            "confidence_score": round(
                random.uniform(0.60, 0.98),
                3
            ),
            "created_date": incident["incident_date"],
            "validated_flag": validated,
        }
    )

    lesson_id += 1

lessons_df = pd.DataFrame(lesson_rows)


# ============================================================
# 10. ACTIONS
# ============================================================

action_rows = []

action_id = 1

for _, lesson in lessons_df.iterrows():

    # Not every lesson becomes an action.
    if random.random() < 0.80:

        action_date = pd.Timestamp(
            lesson["created_date"]
        )

        due_date = (
            action_date
            + pd.Timedelta(
                days=random.randint(15, 120)
            )
        )

        status = random.choices(
            [
                "Completed",
                "In Progress",
                "Overdue",
                "Cancelled",
            ],
            weights=[55, 20, 20, 5]
        )[0]

        completion_date = None

        if status == "Completed":
            completion_date = (
                action_date
                + pd.Timedelta(
                    days=random.randint(5, 100)
                )
            ).date()

        # Some actions are ineffective even when completed.
        effectiveness = (
            random.uniform(0.70, 1.0)
            if status == "Completed"
            else random.uniform(0.0, 0.5)
        )

        action_rows.append(
            {
                "action_id": action_id,
                "lesson_id": int(
                    lesson["lesson_id"]
                ),
                "action_owner_id": random.randint(
                    1,
                    NUM_EMPLOYEES
                ),
                "action_description": (
                    f"Implement preventive action "
                    f"for lesson {lesson['lesson_id']}"
                ),
                "action_date": action_date.date(),
                "due_date": due_date.date(),
                "completion_date": completion_date,
                "status": status,
                "effectiveness_score": round(
                    effectiveness,
                    3
                ),
            }
        )

        action_id += 1

actions_df = pd.DataFrame(action_rows)


# ============================================================
# 11. RECURRENCE EVENTS
# ============================================================

recurrence_rows = []

# Match incidents through common root causes.
root_cause_groups = incidents_df.groupby(
    "root_cause"
)

recurrence_id = 1

for root_cause, group in root_cause_groups:

    if len(group) < 2:
        continue

    group = group.sort_values("incident_date")

    records = group.to_dict("records")

    for i in range(1, len(records)):

        previous = records[i - 1]
        current = records[i]

        previous_date = pd.Timestamp(
            previous["incident_date"]
        )

        current_date = pd.Timestamp(
            current["incident_date"]
        )

        days_between = (
            current_date - previous_date
        ).days

        if 0 < days_between <= 365:

            same_department = int(
                previous["department_id"]
                == current["department_id"]
            )

            # If a lesson/action exists, recurrence may
            # have been prevented.
            previous_lesson = lessons_df[
                lessons_df["incident_id"]
                == previous["incident_id"]
            ]

            lesson_available = int(
                len(previous_lesson) > 0
            )

            action_available = 0

            if lesson_available:

                lesson_ids = previous_lesson[
                    "lesson_id"
                ].tolist()

                action_available = int(
                    actions_df[
                        actions_df["lesson_id"].isin(
                            lesson_ids
                        )
                    ].shape[0] > 0
                )

            # Hidden pattern:
            # completed effective actions reduce recurrence.
            prevented = int(
                action_available == 1
                and random.random() < 0.65
            )

            recurrence_rows.append(
                {
                    "recurrence_id": recurrence_id,
                    "original_incident_id": int(
                        previous["incident_id"]
                    ),
                    "recurring_incident_id": int(
                        current["incident_id"]
                    ),
                    "days_between": days_between,
                    "same_root_cause_flag": 1,
                    "same_department_flag": same_department,
                    "lesson_available_flag": lesson_available,
                    "action_available_flag": action_available,
                    "recurrence_prevented_flag": prevented,
                }
            )

            recurrence_id += 1

recurrence_df = pd.DataFrame(recurrence_rows)


# ============================================================
# WRITE TO SQLITE
# ============================================================

print("\nWriting data to SQLite...\n")

conn = sqlite3.connect(DB_PATH)

tables = {
    "departments": departments_df,
    "employees": employees_df,
    "decisions": decisions_df,
    "assumptions": assumptions_df,
    "initiatives": initiatives_df,
    "experiments": experiments_df,
    "outcomes": outcomes_df,
    "incidents": incidents_df,
    "lessons": lessons_df,
    "actions": actions_df,
    "recurrence_events": recurrence_df,
}

for table_name, dataframe in tables.items():

    dataframe.to_sql(
        table_name,
        conn,
        if_exists="append",
        index=False
    )

    print(
        f"{table_name:<20} "
        f"{len(dataframe):>10,} records"
    )


# ============================================================
# DATA QUALITY LOG
# ============================================================

quality_rows = []

for table_name, dataframe in tables.items():

    records = len(dataframe)

    missing_values = int(
        dataframe.isna().sum().sum()
    )

    failure_rate = (
        missing_values / max(records, 1)
    )

    quality_rows.append(
        {
            "table_name": table_name,
            "check_name": "Initial completeness check",
            "check_date": datetime.now(),
            "records_checked": records,
            "records_failed": missing_values,
            "failure_rate": failure_rate,
            "quality_status": (
                "PASS"
                if missing_values == 0
                else "WARNING"
            ),
        }
    )

quality_df = pd.DataFrame(quality_rows)

quality_df.to_sql(
    "data_quality_log",
    conn,
    if_exists="append",
    index=False
)

conn.close()


# ============================================================
# SUMMARY
# ============================================================

print("\n==============================================")
print("MEMORIA DATA GENERATION COMPLETE")
print("==============================================")

for table_name, dataframe in tables.items():
    print(
        f"{table_name:<20}: "
        f"{len(dataframe):>10,} records"
    )

print(
    f"{'data_quality_log':<20}: "
    f"{len(quality_df):>10,} records"
)

print("\nDatabase:")
print(DB_PATH)

print("\nSeed:")
print(SEED)

print("\n==============================================")