import streamlit as st
import pandas as pd
from pathlib import Path

# =========================================================
# MEMORIA - DECISION INTELLIGENCE DASHBOARD
# =========================================================

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="MEMORIA | Decision Intelligence",
    page_icon="M",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "outputs"


# ---------------------------------------------------------
# HELPER FUNCTION
# ---------------------------------------------------------

def load_csv(filename):
    """Load CSV from outputs folder."""
    path = OUTPUT_DIR / filename

    if not path.exists():
        st.error(f"Missing file: {path}")
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except Exception as e:
        st.error(f"Could not load {filename}: {e}")
        return pd.DataFrame()


# ---------------------------------------------------------
# LOAD ALL DASHBOARD DATA
# ---------------------------------------------------------

risk_band = load_csv("risk_band.csv")
department_risk = load_csv("department_risk.csv")
decision_type_risk = load_csv("decision_type_risk.csv")
financial_department = load_csv("financial_department.csv")
financial_decision_type = load_csv("financial_decision_type.csv")
outcome_performance = load_csv("outcome_performance.csv")
assumption_category = load_csv("assumption_category.csv")
risk_hotspots = load_csv("risk_hotspots.csv")


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("MEMORIA")
st.subheader("Decision Intelligence & Risk Analytics")

st.write(
    "Executive dashboard for monitoring high-risk decisions, "
    "financial exposure, outcome performance, and assumption reliability."
)

st.divider()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("MEMORIA Controls")

st.sidebar.markdown("### Dashboard Filters")

# Department filter

if (
    not department_risk.empty
    and "department_name" in department_risk.columns
):

    department_options = sorted(
        department_risk["department_name"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

else:
    department_options = []

selected_department = st.sidebar.selectbox(
    "Department",
    ["All"] + department_options
)


# Decision type filter

if (
    not decision_type_risk.empty
    and "decision_type" in decision_type_risk.columns
):

    decision_options = sorted(
        decision_type_risk["decision_type"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

else:
    decision_options = []

selected_decision_type = st.sidebar.selectbox(
    "Decision Type",
    ["All"] + decision_options
)


st.sidebar.divider()

st.sidebar.markdown("### Risk Threshold")

risk_threshold = st.sidebar.slider(
    "Minimum Risk Score",
    min_value=40,
    max_value=65,
    value=40,
    step=5
)

st.sidebar.divider()

st.sidebar.info(
    "MEMORIA identifies high-risk decisions and analyzes "
    "their financial, operational, outcome, and assumption-level impact."
)


# =========================================================
# APPLY FILTERS
# =========================================================

filtered_department_risk = department_risk.copy()
filtered_decision_type_risk = decision_type_risk.copy()
filtered_financial_department = financial_department.copy()
filtered_financial_decision_type = financial_decision_type.copy()
filtered_hotspots = risk_hotspots.copy()


# Department filter

if selected_department != "All":

    if "department_name" in filtered_department_risk.columns:

        filtered_department_risk = filtered_department_risk[
            filtered_department_risk["department_name"]
            == selected_department
        ]

    if "department_name" in filtered_financial_department.columns:

        filtered_financial_department = filtered_financial_department[
            filtered_financial_department["department_name"]
            == selected_department
        ]

    if "department_name" in filtered_hotspots.columns:

        filtered_hotspots = filtered_hotspots[
            filtered_hotspots["department_name"]
            == selected_department
        ]


# Decision type filter

if selected_decision_type != "All":

    if "decision_type" in filtered_decision_type_risk.columns:

        filtered_decision_type_risk = filtered_decision_type_risk[
            filtered_decision_type_risk["decision_type"]
            == selected_decision_type
        ]

    if "decision_type" in filtered_financial_decision_type.columns:

        filtered_financial_decision_type = (
            filtered_financial_decision_type[
                filtered_financial_decision_type["decision_type"]
                == selected_decision_type
            ]
        )

    if "decision_type" in filtered_hotspots.columns:

        filtered_hotspots = filtered_hotspots[
            filtered_hotspots["decision_type"]
            == selected_decision_type
        ]


# =========================================================
# EXECUTIVE KPI CALCULATIONS
# =========================================================

if (
    not filtered_department_risk.empty
    and "high_risk_decisions" in filtered_department_risk.columns
):

    total_high_risk = int(
        filtered_department_risk["high_risk_decisions"].sum()
    )

else:

    total_high_risk = 0


if (
    not filtered_department_risk.empty
    and "avg_score" in filtered_department_risk.columns
):

    avg_risk_score = filtered_department_risk["avg_score"].mean()

else:

    avg_risk_score = 0


if (
    not filtered_financial_department.empty
    and "total_financial_impact" in filtered_financial_department.columns
):

    total_financial_impact = (
        filtered_financial_department["total_financial_impact"].sum()
    )

else:

    total_financial_impact = 0


# Outcome metrics

failed_outcomes = 0
successful_outcomes = 0

if (
    not outcome_performance.empty
    and "outcome_status" in outcome_performance.columns
    and "outcomes" in outcome_performance.columns
):

    failed_rows = outcome_performance[
        outcome_performance["outcome_status"].astype(str).str.lower()
        == "failed"
    ]

    successful_rows = outcome_performance[
        outcome_performance["outcome_status"].astype(str).str.lower()
        == "successful"
    ]

    if not failed_rows.empty:
        failed_outcomes = int(
            failed_rows["outcomes"].sum()
        )

    if not successful_rows.empty:
        successful_outcomes = int(
            successful_rows["outcomes"].sum()
        )


total_outcomes = failed_outcomes + successful_outcomes

if total_outcomes > 0:

    failure_rate = (
        failed_outcomes / total_outcomes
    ) * 100

else:

    failure_rate = 0


# =========================================================
# EXECUTIVE OVERVIEW
# =========================================================

st.markdown("## Executive Risk Overview")

c1, c2, c3, c4 = st.columns(4)

with c1:

    st.metric(
        "High-Risk Decisions",
        f"{total_high_risk:,}"
    )

with c2:

    st.metric(
        "Average Risk Score",
        f"{avg_risk_score:.2f}"
    )

with c3:

    st.metric(
        "Financial Impact",
        f"{total_financial_impact:,.0f}"
    )

with c4:

    st.metric(
        "Outcome Failure Rate",
        f"{failure_rate:.2f}%"
    )


st.divider()


# =========================================================
# EXECUTIVE SUMMARY
# =========================================================

st.markdown("## Executive Summary")

summary_col1, summary_col2 = st.columns(2)

with summary_col1:

    if total_high_risk > 0:

        st.write(
            f"MEMORIA currently identifies **{total_high_risk:,} "
            "high-risk decisions** under the selected filters."
        )

    else:

        st.write(
            "No high-risk decisions match the selected filters."
        )


with summary_col2:

    if failure_rate > 0:

        st.write(
            f"The observed outcome failure rate is "
            f"**{failure_rate:.2f}%**."
        )

    else:

        st.write(
            "No failed outcomes are present in the selected data."
        )


st.divider()


# =========================================================
# RISK BY DEPARTMENT
# =========================================================

st.markdown("## Risk Exposure by Department")

if not filtered_department_risk.empty:

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:

        st.markdown("### High-Risk Decisions")

        if (
            "department_name" in filtered_department_risk.columns
            and "high_risk_decisions"
            in filtered_department_risk.columns
        ):

            department_chart = (
                filtered_department_risk[
                    ["department_name", "high_risk_decisions"]
                ]
                .set_index("department_name")
            )

            st.bar_chart(
                department_chart,
                width="stretch"
            )

    with chart_col2:

        st.markdown("### Average Risk Score")

        if (
            "department_name" in filtered_department_risk.columns
            and "avg_score" in filtered_department_risk.columns
        ):

            score_chart = (
                filtered_department_risk[
                    ["department_name", "avg_score"]
                ]
                .set_index("department_name")
            )

            st.bar_chart(
                score_chart,
                width="stretch"
            )

else:

    st.info(
        "No department data matches the selected filters."
    )


# =========================================================
# DEPARTMENT TABLE
# =========================================================

with st.expander("View Department Risk Data"):

    st.dataframe(
        filtered_department_risk,
        width="stretch"
    )


st.divider()


# =========================================================
# RISK BY DECISION TYPE
# =========================================================

st.markdown("## Risk by Decision Type")

if not filtered_decision_type_risk.empty:

    if (
        "decision_type" in filtered_decision_type_risk.columns
        and "high_risk_decisions"
        in filtered_decision_type_risk.columns
    ):

        decision_chart = (
            filtered_decision_type_risk[
                ["decision_type", "high_risk_decisions"]
            ]
            .set_index("decision_type")
        )

        st.bar_chart(
            decision_chart,
            width="stretch"
        )

else:

    st.info(
        "No decision-type data matches the selected filters."
    )


with st.expander("View Decision Type Risk Data"):

    st.dataframe(
        filtered_decision_type_risk,
        width="stretch"
    )


st.divider()


# =========================================================
# FINANCIAL IMPACT
# =========================================================

st.markdown("## Financial Impact Analysis")

financial_col1, financial_col2 = st.columns(2)

with financial_col1:

    st.markdown("### Financial Impact by Department")

    if (
        not filtered_financial_department.empty
        and "department_name"
        in filtered_financial_department.columns
        and "total_financial_impact"
        in filtered_financial_department.columns
    ):

        financial_dept_chart = (
            filtered_financial_department[
                [
                    "department_name",
                    "total_financial_impact"
                ]
            ]
            .set_index("department_name")
        )

        st.bar_chart(
            financial_dept_chart,
            width="stretch"
        )

    else:

        st.info(
            "No financial department data available."
        )


with financial_col2:

    st.markdown("### Financial Impact by Decision Type")

    if (
        not filtered_financial_decision_type.empty
        and "decision_type"
        in filtered_financial_decision_type.columns
        and "total_financial_impact"
        in filtered_financial_decision_type.columns
    ):

        financial_type_chart = (
            filtered_financial_decision_type[
                [
                    "decision_type",
                    "total_financial_impact"
                ]
            ]
            .set_index("decision_type")
        )

        st.bar_chart(
            financial_type_chart,
            width="stretch"
        )

    else:

        st.info(
            "No financial decision-type data available."
        )


with st.expander("View Financial Department Data"):

    st.dataframe(
        filtered_financial_department,
        width="stretch"
    )


with st.expander("View Financial Decision Type Data"):

    st.dataframe(
        filtered_financial_decision_type,
        width="stretch"
    )


st.divider()


# =========================================================
# OUTCOME PERFORMANCE
# =========================================================

st.markdown("## Outcome Performance")

if not outcome_performance.empty:

    outcome_col1, outcome_col2 = st.columns(2)

    with outcome_col1:

        st.metric(
            "Successful Outcomes",
            f"{successful_outcomes:,}"
        )

    with outcome_col2:

        st.metric(
            "Failed Outcomes",
            f"{failed_outcomes:,}"
        )

    st.dataframe(
        outcome_performance,
        width="stretch"
    )

else:

    st.info(
        "Outcome performance data is unavailable."
    )


st.divider()


# =========================================================
# ASSUMPTION ANALYSIS
# =========================================================

st.markdown("## Assumption Risk Analysis")

if not assumption_category.empty:

    if (
        "assumption_category"
        in assumption_category.columns
        and "failure_rate_pct"
        in assumption_category.columns
    ):

        assumption_chart = (
            assumption_category[
                [
                    "assumption_category",
                    "failure_rate_pct"
                ]
            ]
            .set_index("assumption_category")
        )

        st.bar_chart(
            assumption_chart,
            width="stretch"
        )

    st.dataframe(
        assumption_category,
        width="stretch"
    )

else:

    st.info(
        "Assumption analysis data is unavailable."
    )


st.divider()


# =========================================================
# RISK BAND
# =========================================================

st.markdown("## Risk Band Distribution")

if not risk_band.empty:

    st.dataframe(
        risk_band,
        width="stretch"
    )

    if (
        "risk_band" in risk_band.columns
        and "decisions" in risk_band.columns
    ):

        risk_band_chart = (
            risk_band[
                ["risk_band", "decisions"]
            ]
            .set_index("risk_band")
        )

        st.bar_chart(
            risk_band_chart,
            width="stretch"
        )


st.divider()


# =========================================================
# CRITICAL RISK HOTSPOTS
# =========================================================

st.markdown("## Critical Risk Hotspots")

if not filtered_hotspots.empty:

    st.write(
        f"Showing {len(filtered_hotspots):,} matching risk records."
    )

    # Additional risk score filter if column exists

    if "decision_risk_score" in filtered_hotspots.columns:

        filtered_hotspots = filtered_hotspots[
            filtered_hotspots["decision_risk_score"]
            >= risk_threshold
        ]

    st.dataframe(
        filtered_hotspots,
        width="stretch",
        height=500
    )

else:

    st.info(
        "No risk hotspots match the selected filters."
    )


st.divider()


# =========================================================
# DATASET INFORMATION
# =========================================================

st.markdown("## Dashboard Data")

info_col1, info_col2, info_col3, info_col4 = st.columns(4)

with info_col1:

    st.metric(
        "Departments",
        len(department_risk)
    )

with info_col2:

    st.metric(
        "Decision Types",
        len(decision_type_risk)
    )

with info_col3:

    st.metric(
        "Assumption Categories",
        len(assumption_category)
    )

with info_col4:

    st.metric(
        "Risk Hotspots",
        len(risk_hotspots)
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "MEMORIA | Decision Intelligence & Risk Analytics"
)

st.caption(
    "Built with Python, SQLite, Pandas and Streamlit"
)