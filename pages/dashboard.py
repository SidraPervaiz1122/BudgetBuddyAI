"""
pages/dashboard.py

BudgetBuddy AI - Dashboard
------------------------------
The main finance dashboard: welcome message, key metric cards, a monthly
budget/savings-goal control, recent expenses, top spending category,
quick actions, and Plotly charts (category pie, monthly bar). All figures
are pulled live from database/db.py - nothing here is hard-coded or fake.
"""

import calendar
from datetime import datetime, date
import pandas as pd
import plotly.express as px
import streamlit as st

from database.db import (
    get_user_expenses,
    get_total_expense,
    get_category_totals,
    get_monthly_expenses,
    get_user_budget,
    set_user_budget,
)
from utils.helpers import (
    format_currency,
    calculate_remaining_budget,
    calculate_savings_percentage,
    calculate_highest_spending_category,
)
from components.sidebar import render_sidebar
from components.navbar import render_navbar
from components.cards import render_dashboard_cards

# ----------------------------------------------------------------------------
# Page configuration & auth guard
# ----------------------------------------------------------------------------

st.set_page_config(page_title="Dashboard | BudgetBuddy AI", page_icon="💰", layout="wide")

if not st.session_state.get("logged_in"):
    st.warning("⚠️ Please log in to view your dashboard.")
    st.switch_page("pages/login.py")
    st.stop()

user_id = st.session_state["user_id"]
user_name = st.session_state.get("user_name", "there")

# ----------------------------------------------------------------------------
# Layout shell
# ----------------------------------------------------------------------------

render_sidebar(active_page="Dashboard")
render_navbar(page_title="Dashboard", user_name=user_name)

st.markdown(f"### 👋 Welcome back, {user_name}!")
st.caption("Here's a live snapshot of your finances.")

# ----------------------------------------------------------------------------
# Monthly budget control
# ----------------------------------------------------------------------------

monthly_budget = get_user_budget(user_id)

with st.expander("🎯 Set / Update Your Monthly Budget", expanded=(monthly_budget == 0.0)):
    new_budget = st.number_input(
        "Monthly Budget (PKR)",
        min_value=0.0,
        value=float(monthly_budget),
        step=500.0,
        format="%.2f",
    )
    if st.button("💾 Save Budget"):
        success, message = set_user_budget(user_id, new_budget)
        if success:
            st.session_state["monthly_budget"] = float(new_budget)
            st.success(f"✅ {message}")
            st.rerun()
        else:
            st.error(f"❌ {message}")

# ----------------------------------------------------------------------------
# Pull live data from the database
# ----------------------------------------------------------------------------

today = date.today()
today_str = today.strftime("%Y-%m-%d")
month_start_str = today.replace(day=1).strftime("%Y-%m-%d")
_, last_day = calendar.monthrange(today.year, today.month)
month_end_str = today.replace(day=last_day).strftime("%Y-%m-%d")

all_expenses = get_user_expenses(user_id)
month_expenses = get_user_expenses(user_id, start_date=month_start_str, end_date=month_end_str)

total_expenses_month = get_total_expense(user_id, start_date=month_start_str, end_date=month_end_str)
today_expenses = [e for e in all_expenses if e["date"] == today_str]
today_total = sum(float(e["amount"]) for e in today_expenses)

category_totals = get_category_totals(user_id, start_date=month_start_str, end_date=month_end_str)
monthly_totals = get_monthly_expenses(user_id)

remaining_budget = calculate_remaining_budget(monthly_budget, total_expenses_month)
savings_percentage = calculate_savings_percentage(monthly_budget, total_expenses_month)
top_category = calculate_highest_spending_category(category_totals)

# ----------------------------------------------------------------------------
# Metric cards
# ----------------------------------------------------------------------------

render_dashboard_cards(
    total_budget=monthly_budget,
    total_expenses=total_expenses_month,
    remaining_budget=remaining_budget,
    savings_percentage=savings_percentage,
)

st.write("")

# ----------------------------------------------------------------------------
# Secondary metrics row: today's spending, savings goal progress, top category
# ----------------------------------------------------------------------------

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.metric("📆 Today's Spending", format_currency(today_total))

with col_b:
    st.markdown("**🎯 Savings Goal Progress**")
    progress_value = max(min(savings_percentage, 100.0), 0.0) / 100.0
    st.progress(progress_value)
    st.caption(f"{savings_percentage:.1f}% of your budget saved this month")

with col_c:
    if top_category:
        st.metric(f"🏆 Top Category: {top_category[0]}", format_currency(top_category[1]))
    else:
        st.metric("🏆 Top Category", "No data yet")

st.divider()

# ----------------------------------------------------------------------------
# Quick actions
# ----------------------------------------------------------------------------

st.markdown("### ⚡ Quick Actions")
qa1, qa2, qa3, qa4 = st.columns(4)

with qa1:
    if st.button("➕ Add Expense", use_container_width=True):
        st.switch_page("pages/add_expense.py")
with qa2:
    if st.button("📊 View Analytics", use_container_width=True):
        st.switch_page("pages/analytics.py")
with qa3:
    if st.button("📄 View Reports", use_container_width=True):
        st.switch_page("pages/reports.py")
with qa4:
    if st.button("🤖 Ask AI Advisor", use_container_width=True):
        st.switch_page("pages/ai_advisor.py")

st.divider()

# ----------------------------------------------------------------------------
# Charts
# ----------------------------------------------------------------------------

st.markdown("### 📈 Insights")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("#### 🥧 Spending by Category")
    if category_totals:
        pie_df = pd.DataFrame(
            {"Category": list(category_totals.keys()), "Amount": list(category_totals.values())}
        )
        fig_pie = px.pie(
            pie_df, names="Category", values="Amount", hole=0.45,
            color_discrete_sequence=px.colors.sequential.Teal,
        )
        fig_pie.update_layout(margin=dict(t=10, b=10, l=10, r=10), legend_title_text="")
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("📭 No expenses recorded yet this month.")

with chart_col2:
    st.markdown("#### 📊 Monthly Spending")
    if monthly_totals:
        bar_df = pd.DataFrame(
            {"Month": list(monthly_totals.keys()), "Amount": list(monthly_totals.values())}
        )
        fig_bar = px.bar(
            bar_df, x="Month", y="Amount", color="Amount",
            color_continuous_scale="Teal",
        )
        fig_bar.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("📭 No monthly spending history available yet.")

st.divider()

# ----------------------------------------------------------------------------
# Recent Expenses Table
# ----------------------------------------------------------------------------

st.markdown("### 🕒 Recent Expenses")
if all_expenses:
    recent_df = pd.DataFrame(all_expenses[:5])
    display_df = recent_df[["date", "category", "amount", "description"]].copy()
    display_df["amount"] = display_df["amount"].apply(format_currency)
    display_df.columns = ["Date", "Category", "Amount", "Description"]
    st.dataframe(display_df, use_container_width=True, hide_index=True)
else:
    st.info("📭 No recent expenses found. Click 'Add Expense' above to log your first transaction!")