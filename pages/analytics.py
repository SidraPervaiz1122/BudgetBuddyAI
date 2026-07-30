"""
pages/analytics.py

BudgetBuddy AI - Analytics
------------------------------
The deep-dive companion to the Dashboard's quick overview. Everything
here is intentionally distinct from Dashboard's charts: monthly trend,
category ranking, daily trend, a single larger interactive pie, and a
searchable/sortable expense table - plus KPI cards that summarize the
whole history (total spent, average daily spend, highest/lowest expense).

Performance: expenses are read once via utils.helpers.load_all_expenses
(cached for 30s and shared with Dashboard/Sidebar), then every aggregation
below (category totals, monthly totals, daily totals, KPIs) is computed in
plain Python/pandas - no extra database queries.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.helpers import (
    format_currency,
    load_all_expenses,
    compute_total,
    compute_category_totals,
    compute_monthly_totals,
    compute_daily_totals,
    compute_average_daily_spending,
    get_highest_expense,
    get_lowest_expense,
    style_chart,
    CHART_CONFIG,
)
from components.sidebar import render_sidebar
from components.navbar import render_navbar

# ----------------------------------------------------------------------------
# Page configuration & auth guard
# ----------------------------------------------------------------------------

st.set_page_config(page_title="Analytics | BudgetBuddy AI", page_icon="📊", layout="wide")

if not st.session_state.get("logged_in"):
    st.warning("⚠️ Please log in to view analytics.")
    st.switch_page("pages/login.py")
    st.stop()

user_id = st.session_state["user_id"]
user_name = st.session_state.get("user_name", "there")

CATEGORY_ICONS = {
    "Food": "🍔", "Transport": "🚗", "Education": "📚", "Shopping": "🛍️",
    "Entertainment": "🎬", "Bills": "🧾", "Health": "🏥", "Other": "🗂️",
}

# ----------------------------------------------------------------------------
# Layout shell
# ----------------------------------------------------------------------------

render_sidebar(active_page="Analytics")
render_navbar(page_title="Analytics", user_name=user_name)

st.markdown(
    """
    <style>
        /* Prevent the expense table and KPI text from overflowing on
           narrow / tablet / mobile widths. */
        .block-container { max-width: 100%; }
        div[data-testid="stMetricValue"] {
            overflow-wrap: break-word;
            white-space: normal !important;
            overflow: visible !important;
            text-overflow: unset !important;
            font-size: clamp(1.1rem, 2.2vw, 1.6rem);
        }
        div[data-testid="stMetricLabel"] {
            overflow-wrap: break-word;
            white-space: normal !important;
            overflow: visible !important;
            text-overflow: unset !important;
        }
        div[data-testid="stMetricLabel"] p {
            white-space: normal !important;
            overflow: visible !important;
            text-overflow: unset !important;
        }
        div[data-testid="stMetricDelta"] {
            overflow-wrap: break-word;
            white-space: normal !important;
            overflow: visible !important;
            text-overflow: unset !important;
        }
        @media (max-width: 640px) {
            div[data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("### 📊 Your Spending Analytics")
st.caption("A deeper look at trends, categories, and history across all your expenses.")

# ----------------------------------------------------------------------------
# Load data once (cached) - everything else below is computed in Python
# ----------------------------------------------------------------------------

all_expenses = load_all_expenses(user_id)

if not all_expenses:
    st.info("📭 No expenses recorded yet. Add some expenses to unlock your analytics.")
    st.stop()

total_spent = compute_total(all_expenses)
category_totals = compute_category_totals(all_expenses)
monthly_totals = compute_monthly_totals(all_expenses)
daily_totals = compute_daily_totals(all_expenses)
avg_daily = compute_average_daily_spending(all_expenses)
highest_expense = get_highest_expense(all_expenses)
lowest_expense = get_lowest_expense(all_expenses)

# ----------------------------------------------------------------------------
# KPI cards
# ----------------------------------------------------------------------------

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric("💸 Total Spent", format_currency(total_spent))

with k2:
    st.metric("📐 Average Daily Spending", format_currency(avg_daily))

with k3:
    if highest_expense:
        st.metric(
            "🔺 Highest Expense",
            format_currency(highest_expense["amount"]),
            delta=f"{highest_expense['category']} · {highest_expense['date']}",
            delta_color="off",
        )
    else:
        st.metric("🔺 Highest Expense", "N/A")

with k4:
    if lowest_expense:
        st.metric(
            "🔻 Lowest Expense",
            format_currency(lowest_expense["amount"]),
            delta=f"{lowest_expense['category']} · {lowest_expense['date']}",
            delta_color="off",
        )
    else:
        st.metric("🔻 Lowest Expense", "N/A")

st.divider()

# ----------------------------------------------------------------------------
# Row 1: Monthly Spending Trend (line) + Top Spending Categories (h-bar)
# ----------------------------------------------------------------------------

trend_col, top_col = st.columns(2)

with trend_col:
    st.markdown("#### 📈 Monthly Spending Trend")
    trend_df = pd.DataFrame({"Month": list(monthly_totals.keys()), "Amount": list(monthly_totals.values())})
    # Keys look like "2026-07"; Plotly auto-detects those as dates and
    # misrenders a single-point time axis, so convert + plot as category.
    trend_df["Month"] = pd.to_datetime(trend_df["Month"], format="%Y-%m")
    trend_df = trend_df.sort_values("Month")
    trend_df["Label"] = trend_df["Month"].dt.strftime("%b %Y")

    fig_trend = px.line(
        trend_df, x="Label", y="Amount", markers=True, line_shape="spline",
        color_discrete_sequence=["#6366f1"],
    )
    fig_trend.update_traces(
        line=dict(width=3), marker=dict(size=8),
        hovertemplate="%{x}<br>Rs. %{y:,.0f}<extra></extra>",
    )
    fig_trend.update_xaxes(type="category", title=None)
    fig_trend.update_yaxes(title="Amount (PKR)")
    style_chart(fig_trend)
    st.plotly_chart(fig_trend, use_container_width=True, config=CHART_CONFIG)

with top_col:
    st.markdown("#### 🏆 Top Spending Categories")
    top_df = pd.DataFrame(
        {"Category": list(category_totals.keys()), "Amount": list(category_totals.values())}
    ).sort_values("Amount")
    fig_top = px.bar(
        top_df, x="Amount", y="Category", orientation="h",
        color="Amount", color_continuous_scale="Purp", text="Amount",
    )
    fig_top.update_traces(
        texttemplate="Rs. %{x:,.0f}", textposition="outside",
        hovertemplate="%{y}<br>Rs. %{x:,.0f}<extra></extra>",
    )
    fig_top.update_layout(coloraxis_showscale=False)
    fig_top.update_xaxes(tickprefix="Rs. ")
    fig_top.update_yaxes(title=None)
    style_chart(fig_top)
    st.plotly_chart(fig_top, use_container_width=True, config=CHART_CONFIG)

st.divider()

# ----------------------------------------------------------------------------
# Daily Spending Trend (area chart)
# ----------------------------------------------------------------------------

st.markdown("#### 📉 Daily Spending Trend")
daily_df = pd.DataFrame({"Date": list(daily_totals.keys()), "Amount": list(daily_totals.values())})
daily_df["Date"] = pd.to_datetime(daily_df["Date"])
daily_df = daily_df.sort_values("Date")

fig_daily = px.area(daily_df, x="Date", y="Amount", markers=True, color_discrete_sequence=["#22c55e"])
fig_daily.update_traces(
    line=dict(width=2.5), fillcolor="rgba(34,197,94,0.15)",
    hovertemplate="%{x|%b %d, %Y}<br>Rs. %{y:,.0f}<extra></extra>",
)
fig_daily.update_xaxes(title="Date", tickformat="%b %d")
fig_daily.update_yaxes(title="Amount (PKR)")
style_chart(fig_daily)
st.plotly_chart(fig_daily, use_container_width=True, config=CHART_CONFIG)

st.divider()

st.divider()

# ----------------------------------------------------------------------------
# Interactive Expense Table - search, filter by category, sortable columns
# ----------------------------------------------------------------------------
# Note: the Expense-by-Category pie chart intentionally does NOT appear on
# this page - it already lives on the Dashboard, and repeating it here was
# the exact "duplicate chart" this redesign is meant to remove.

st.markdown("#### 🔎 Interactive Expense Table")

filt_col1, filt_col2 = st.columns([2, 1])
with filt_col1:
    search_term = st.text_input("Search by description", placeholder="e.g. groceries, bus, netflix")
with filt_col2:
    filter_category = st.selectbox("Filter by category", options=["All"] + sorted(category_totals.keys()))

table_rows = all_expenses
if filter_category != "All":
    table_rows = [e for e in table_rows if e["category"] == filter_category]
if search_term.strip():
    term = search_term.strip().lower()
    table_rows = [e for e in table_rows if term in (e.get("description") or "").lower()]

if table_rows:
    table_df = pd.DataFrame(table_rows)[["date", "category", "amount", "description"]].copy()
    table_df.columns = ["Date", "Category", "Amount (PKR)", "Description"]
    st.caption(f"Showing {len(table_df)} of {len(all_expenses)} transactions — click a column header to sort.")

    # Fully dynamic height: the table hugs its actual row count (no empty
    # trailing rows for small result sets) and only becomes scrollable once
    # there are enough rows to need it, instead of always reserving a fixed
    # block of space.
    ROW_HEIGHT_PX = 35
    HEADER_HEIGHT_PX = 38
    MAX_TABLE_HEIGHT_PX = 560   # ~15 rows visible before it scrolls
    dynamic_height = min(HEADER_HEIGHT_PX + ROW_HEIGHT_PX * len(table_df), MAX_TABLE_HEIGHT_PX)

    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True,
        height=dynamic_height,
        column_config={
            "Amount (PKR)": st.column_config.NumberColumn(format="Rs. %.2f"),
        },
    )
else:
    st.info("📭 No transactions match your search/filter.")