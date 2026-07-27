"""
pages/analytics.py

BudgetBuddy AI - Analytics
------------------------------
A complete analytics dashboard covering monthly spending, category
distribution, highest spending category, average expense, and daily /
weekly spending trends. All data is read live from database/db.py.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from database.db import get_user_expenses, get_category_totals, get_monthly_expenses
from utils.helpers import format_currency, calculate_highest_spending_category, calculate_monthly_statistics
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

# ----------------------------------------------------------------------------
# Layout shell
# ----------------------------------------------------------------------------

render_sidebar(active_page="Analytics")
render_navbar(page_title="Analytics", user_name=user_name)

st.markdown("### 📊 Your Spending Analytics")
st.caption("A deeper look at how and where your money is going.")

# ----------------------------------------------------------------------------
# Pull live data
# ----------------------------------------------------------------------------

all_expenses = get_user_expenses(user_id)
category_totals = get_category_totals(user_id)
monthly_totals = get_monthly_expenses(user_id)
stats = calculate_monthly_statistics(all_expenses)
top_category = calculate_highest_spending_category(category_totals)

if not all_expenses:
    st.info("📭 No expenses recorded yet. Add some expenses to unlock your analytics.")
    st.stop()

# ----------------------------------------------------------------------------
# Summary metrics
# ----------------------------------------------------------------------------

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric("💸 Total Spent", format_currency(stats["total"]))

with m2:
    st.metric("📐 Average Expense", format_currency(stats["average"]))

with m3:
    if top_category:
        st.metric(f"🏆 Highest Category", top_category[0], delta=format_currency(top_category[1]))
    else:
        st.metric("🏆 Highest Category", "N/A")

with m4:
    st.metric("🔢 Total Transactions", stats["count"])

st.divider()

# ----------------------------------------------------------------------------
# Prepare a DataFrame once for time-based aggregations
# ----------------------------------------------------------------------------

df = pd.DataFrame(all_expenses)
df["date"] = pd.to_datetime(df["date"])
df["amount"] = df["amount"].astype(float)

# ----------------------------------------------------------------------------
# Monthly spending & category distribution
# ----------------------------------------------------------------------------

row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.markdown("#### 📊 Monthly Spending")
    if monthly_totals:
        month_df = pd.DataFrame(
            {"Month": list(monthly_totals.keys()), "Amount": list(monthly_totals.values())}
        )
        fig_month = px.bar(month_df, x="Month", y="Amount", color_discrete_sequence=["#3b82f6"])
        fig_month.update_layout(margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_month, use_container_width=True)
    else:
        st.info("📭 No monthly data available yet.")

with row1_col2:
    st.markdown("#### 🥧 Category Distribution")
    if category_totals:
        cat_df = pd.DataFrame(
            {"Category": list(category_totals.keys()), "Amount": list(category_totals.values())}
        )
        fig_cat = px.pie(
            cat_df, names="Category", values="Amount", hole=0.45,
            color_discrete_sequence=px.colors.sequential.Sunset,
        )
        fig_cat.update_layout(margin=dict(t=10, b=10, l=10, r=10), legend_title_text="")
        st.plotly_chart(fig_cat, use_container_width=True)
    else:
        st.info("📭 No category data available yet.")

st.divider()

# ----------------------------------------------------------------------------
# Daily and weekly trends
# ----------------------------------------------------------------------------

st.markdown("#### 📉 Daily Spending Trend")
daily_df = df.groupby("date")["amount"].sum().reset_index().sort_values("date")
fig_daily = px.line(
    daily_df, x="date", y="amount", markers=True,
    color_discrete_sequence=["#22c55e"],
)
fig_daily.update_layout(margin=dict(t=10, b=10, l=10, r=10), xaxis_title="Date", yaxis_title="Amount (PKR)")
st.plotly_chart(fig_daily, use_container_width=True)

st.markdown("#### 📈 Weekly Spending Trend")
weekly_series = df.set_index("date").resample("W")["amount"].sum().reset_index()
weekly_series.rename(columns={"date": "week_ending", "amount": "amount"}, inplace=True)
fig_weekly = px.bar(
    weekly_series, x="week_ending", y="amount", color_discrete_sequence=["#f97316"],
)
fig_weekly.update_layout(margin=dict(t=10, b=10, l=10, r=10), xaxis_title="Week Ending", yaxis_title="Amount (PKR)")
st.plotly_chart(fig_weekly, use_container_width=True)

st.divider()

# ----------------------------------------------------------------------------
# Category breakdown table
# ----------------------------------------------------------------------------

st.markdown("#### 🗂️ Category Breakdown")
if category_totals:
    breakdown_df = pd.DataFrame(
        {"Category": list(category_totals.keys()), "Total Spent": list(category_totals.values())}
    ).sort_values("Total Spent", ascending=False)
    breakdown_df["Total Spent"] = breakdown_df["Total Spent"].apply(format_currency)
    st.dataframe(breakdown_df, use_container_width=True, hide_index=True)