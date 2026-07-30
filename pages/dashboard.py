"""
pages/dashboard.py

BudgetBuddy AI - Dashboard
------------------------------
A clean, minimal financial overview: welcome message, budget control,
four metric cards (Budget / Spent / Remaining / Savings), an
Expense-by-Category pie chart paired with a Budget Utilization gauge,
quick actions, and recent transactions. Deeper analysis (trends,
comparisons, breakdowns, the searchable expense table) lives on the
Analytics page instead, so the two pages no longer duplicate the same
charts.

Performance: all expense/budget reads go through utils.helpers' cached
loaders (load_all_expenses / load_budget), so this page issues at most
two DB queries per 30-second window no matter how many times a widget on
this page triggers a Streamlit rerun. Category totals and month filtering
are computed in plain Python from that cached list - no extra DB calls.
"""

import calendar
from datetime import date
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


from database.db import set_user_budget, add_to_user_budget
from utils.helpers import (
    format_currency,
    calculate_remaining_budget,
    calculate_savings_percentage,
    load_all_expenses,
    load_budget,
    clear_data_cache,
    filter_by_date_range,
    compute_total,
    compute_category_totals,
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

CATEGORY_ICONS = {
    "Food": "🍔", "Transport": "🚗", "Education": "📚", "Shopping": "🛍️",
    "Entertainment": "🎬", "Bills": "🧾", "Health": "🏥", "Other": "🗂️",
}

# ----------------------------------------------------------------------------
# Layout shell
# ----------------------------------------------------------------------------

render_sidebar(active_page="Dashboard")
render_navbar(page_title="Dashboard", user_name=user_name)

# Responsive styling: cards/tx rows never overflow, and stack cleanly on
# tablet/mobile widths.
st.markdown(
    """
    <style>
        .bb-tx-row {
            display: flex; align-items: center; justify-content: space-between;
            background: #ffffff;
            border-radius: 14px;
            padding: 0.8rem 1.1rem;
            margin-bottom: 8px;
            box-shadow: 0 3px 10px rgba(15, 23, 42, 0.05);
            transition: transform 0.15s ease, box-shadow 0.15s ease;
            overflow: hidden;
        }
        .bb-tx-row:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(15, 23, 42, 0.1);
        }
        .bb-tx-left { display: flex; align-items: center; gap: 12px; min-width: 0; }
        .bb-tx-icon {
            width: 40px; height: 40px; flex-shrink: 0; border-radius: 12px;
            background: #f1f5f9;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.2rem;
        }
        .bb-tx-category { font-weight: 700; color: #0f172a; font-size: 0.92rem; margin: 0; }
        .bb-tx-desc {
            font-size: 0.78rem; color: #94a3b8; margin: 1px 0 0 0;
            overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 260px;
        }
        .bb-tx-right { text-align: right; flex-shrink: 0; padding-left: 12px; }
        .bb-tx-amount { font-weight: 700; color: #0f172a; font-size: 0.95rem; margin: 0; }
        .bb-tx-date { font-size: 0.76rem; color: #94a3b8; margin: 1px 0 0 0; }

        @media (max-width: 640px) {
            .bb-tx-row { flex-direction: column; align-items: flex-start; gap: 8px; }
            .bb-tx-right { text-align: left; padding-left: 0; }
            .bb-tx-desc { max-width: 100%; white-space: normal; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# Welcome header + date
# ----------------------------------------------------------------------------

st.markdown(f"### 👋 Welcome back, {user_name}!")
st.caption(f"📅 {date.today().strftime('%A, %d %B %Y')}")

# ----------------------------------------------------------------------------
# Monthly budget control - set an exact amount, or top up what's there
# ----------------------------------------------------------------------------

monthly_budget = load_budget(user_id)

with st.expander("🎯 Set / Update Your Monthly Budget", expanded=(monthly_budget == 0.0)):
    tab_set, tab_add = st.tabs(["✏️ Set Exact Amount", "➕ Add Funds"])

    with tab_set:
        st.caption("Replace your current budget with a new total.")
        new_budget = st.number_input(
            "Monthly Budget (PKR)", min_value=0.0, value=float(monthly_budget),
            step=500.0, format="%.2f", key="set_budget_input",
        )
        if st.button("💾 Save Budget", use_container_width=True):
            success, message = set_user_budget(user_id, new_budget)
            if success:
                clear_data_cache()
                st.success(f"✅ {message}")
                st.rerun()
            else:
                st.error(f"❌ {message}")

    with tab_add:
        st.caption(f"Currently: **{format_currency(monthly_budget)}**. Add extra funds without resetting the total.")
        top_up_amount = st.number_input(
            "Amount to Add (PKR)", min_value=0.0, value=0.0,
            step=500.0, format="%.2f", key="add_budget_input",
        )
        if st.button("➕ Add to Budget", use_container_width=True):
            if top_up_amount <= 0:
                st.error("⚠️ Please enter an amount greater than zero.")
            else:
                try:
                    new_total = add_to_user_budget(user_id, top_up_amount)
                    clear_data_cache()
                    st.success(f"✅ Added {format_currency(top_up_amount)}. New budget: {format_currency(new_total)}")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Couldn't update your budget: {e}")

# ----------------------------------------------------------------------------
# Pull data (cached) and compute this-month figures in plain Python
# ----------------------------------------------------------------------------

today = date.today()
month_start_str = today.replace(day=1).strftime("%Y-%m-%d")
_, last_day = calendar.monthrange(today.year, today.month)
month_end_str = today.replace(day=last_day).strftime("%Y-%m-%d")

all_expenses = load_all_expenses(user_id)
month_expenses = filter_by_date_range(all_expenses, month_start_str, month_end_str)

total_expenses_month = compute_total(month_expenses)
category_totals = compute_category_totals(month_expenses)

remaining_budget = calculate_remaining_budget(monthly_budget, total_expenses_month)
savings_percentage = calculate_savings_percentage(monthly_budget, total_expenses_month)

# ----------------------------------------------------------------------------
# Metric cards (exactly four, as a quick overview)
# ----------------------------------------------------------------------------

render_dashboard_cards(
    total_budget=monthly_budget,
    total_expenses=total_expenses_month,
    remaining_budget=remaining_budget,
    savings_percentage=savings_percentage,
)

st.write("")
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
    if st.button("📄 Generate Report", use_container_width=True):
        st.switch_page("pages/reports.py")
with qa4:
    if st.button("🤖 Open AI Advisor", use_container_width=True):
        st.switch_page("pages/ai_advisor.py")

st.divider()

# ----------------------------------------------------------------------------
# Two charts on this page: Expense by Category + Budget Utilization
# ----------------------------------------------------------------------------

st.markdown("### 📊 This Month at a Glance")

pie_col, gauge_col = st.columns(2)

with pie_col:
    st.markdown("#### 🥧 Expense by Category")
    if category_totals:
        pie_df = pd.DataFrame(
            {"Category": list(category_totals.keys()), "Amount": list(category_totals.values())}
        )
        fig_pie = px.pie(
            pie_df, names="Category", values="Amount", hole=0.45,
            color_discrete_sequence=px.colors.sequential.Teal,
        )
        fig_pie.update_traces(
            textinfo="percent", hovertemplate="%{label}<br>Rs. %{value:,.0f} (%{percent})<extra></extra>"
        )
        fig_pie.update_layout(
            margin=dict(t=10, b=10, l=10, r=10), legend_title_text="",
            paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#334155", size=13),
            height=360,
        )
        st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("📭 No expenses recorded yet this month. Add one to see your breakdown here.")

with gauge_col:
    st.markdown("#### 🎯 Budget Utilization")
    if monthly_budget > 0:
        utilization_pct = (total_expenses_month / monthly_budget) * 100
        # Let the axis stretch past 100 if the user has overspent, instead
        # of silently capping the needle at the top of the dial.
        axis_max = max(100, utilization_pct + 10)

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=round(utilization_pct, 1),
            number={"suffix": "%", "font": {"size": 38, "color": "#0f172a"}},
            gauge={
                "axis": {"range": [0, axis_max], "tickwidth": 1, "tickcolor": "#94a3b8"},
                "bar": {"color": "#6366f1"},
                "bgcolor": "white",
                "borderwidth": 1,
                "bordercolor": "#e2e8f0",
                "steps": [
                    {"range": [0, 70], "color": "rgba(34,197,94,0.18)"},
                    {"range": [70, 90], "color": "rgba(234,179,8,0.18)"},
                    {"range": [90, axis_max], "color": "rgba(239,68,68,0.18)"},
                ],
                "threshold": {
                    "line": {"color": "#ef4444", "width": 3},
                    "thickness": 0.85,
                    "value": 100,
                },
            },
        ))
        fig_gauge.update_layout(
            height=360, margin=dict(t=20, b=10, l=30, r=30),
            paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#334155"),
        )
        st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})

        if utilization_pct >= 100:
            st.caption(f"⚠️ You've used {utilization_pct:.0f}% of this month's budget — you're over.")
        elif utilization_pct >= 90:
            st.caption(f"🟠 You've used {utilization_pct:.0f}% of this month's budget — almost there.")
        else:
            st.caption(f"🟢 You've used {utilization_pct:.0f}% of this month's budget so far.")
    else:
        st.info("📭 Set a monthly budget above to see your utilization here.")

st.divider()

# ----------------------------------------------------------------------------
# Recent Transactions
# ----------------------------------------------------------------------------

st.markdown("### 🕒 Recent Transactions")
if all_expenses:
    for exp in all_expenses[:6]:
        icon = CATEGORY_ICONS.get(exp["category"], "🗂️")
        description = exp.get("description") or "No description"
        st.markdown(
            f"""
            <div class="bb-tx-row">
                <div class="bb-tx-left">
                    <div class="bb-tx-icon">{icon}</div>
                    <div>
                        <p class="bb-tx-category">{exp['category']}</p>
                        <p class="bb-tx-desc">{description}</p>
                    </div>
                </div>
                <div class="bb-tx-right">
                    <p class="bb-tx-amount">{format_currency(exp['amount'])}</p>
                    <p class="bb-tx-date">{exp['date']}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    st.info("📭 No recent expenses found. Click 'Add Expense' above to log your first transaction!")