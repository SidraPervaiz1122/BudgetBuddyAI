"""
pages/ai_advisor.py
"""
import streamlit as st

from database.db import get_user_expenses, get_category_totals, get_total_expense, get_user_budget
from utils.helpers import ask_groq
from components.sidebar import render_sidebar
from components.navbar import render_navbar

# ----------------------------------------------------------------------------
# Page configuration & auth guard
# ----------------------------------------------------------------------------

st.set_page_config(page_title="AI Advisor | BudgetBuddy AI", page_icon="🤖", layout="wide")

if not st.session_state.get("logged_in"):
    st.warning("⚠️ Please log in to use the AI Advisor.")
    st.switch_page("pages/login.py")
    st.stop()

user_id = st.session_state["user_id"]
user_name = st.session_state.get("user_name", "there")

# ----------------------------------------------------------------------------
# Layout shell
# ----------------------------------------------------------------------------

render_sidebar(active_page="AI Advisor")
render_navbar(page_title="AI Advisor", user_name=user_name)

st.markdown(
    """
    <style>
        .bb-advice-card {
            background: linear-gradient(135deg, #1e1b4b, #312e81);
            border: 1px solid rgba(129, 140, 248, 0.35);
            border-radius: 18px;
            padding: 1.8rem 2rem;
            color: #ede9fe;
            box-shadow: 0 12px 30px rgba(49, 46, 129, 0.35);
            line-height: 1.6;
            font-size: 1.02rem;
        }
        .bb-advice-header {
            display: flex;
            align-items: center;
            gap: 0.6rem;
            margin-bottom: 0.8rem;
        }
        .bb-advice-header h3 {
            margin: 0;
            color: #ffffff;
        }
        div.stButton > button {
            border-radius: 10px;
            font-weight: 600;
            background: linear-gradient(90deg, #4f46e5, #6366f1);
            color: white;
            border: none;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("### 🤖 Your Personal AI Budget Advisor")
st.caption("💡 Powered by Groq AI - advice based entirely on your real spending history.")

# ----------------------------------------------------------------------------
# System prompt
# ----------------------------------------------------------------------------

SYSTEM_PROMPT = """You are BudgetBuddy AI.
You are an expert financial advisor for university students.
Analyze spending habits.
Identify unnecessary spending.
Suggest realistic saving strategies.
Be encouraging.
Keep responses under 150 words.
Never mention investing.
Focus on budgeting."""


def _build_expense_summary(expenses, category_totals, total_spent, monthly_budget=0.0):
    if not expenses:
        return f"This student has a monthly budget of Rs. {monthly_budget:,.2f} but has not logged any expenses yet."

    lines = [
        f"Monthly Budget: Rs. {monthly_budget:,.2f}",
        f"Total spending recorded: Rs. {total_spent:,.2f} across {len(expenses)} transactions.",
    ]

    lines.append("Spending by category:")
    for category, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
        lines.append(f"- {category}: Rs. {amount:,.2f}")

    lines.append("Most recent transactions:")
    for exp in expenses[:10]:
        lines.append(
            f"- {exp['date']}: Rs. {float(exp['amount']):,.2f} on {exp['category']}"
            f" ({exp.get('description') or 'no description'})"
        )

    return "\n".join(lines)

# ----------------------------------------------------------------------------
# Pull live expense data
# ----------------------------------------------------------------------------

expenses = get_user_expenses(user_id)
category_totals = get_category_totals(user_id)
total_spent = get_total_expense(user_id)
monthly_budget = get_user_budget(user_id)

if not expenses:
    st.info("📭 Add a few expenses first so the AI Advisor has something to analyze.")
    if st.button("➕ Add Your First Expense"):
        st.switch_page("pages/add_expense.py")
    st.stop()

# ----------------------------------------------------------------------------
# Trigger AI advice
# ----------------------------------------------------------------------------

if "ai_advice" not in st.session_state:
    st.session_state.ai_advice = None
if "ai_advice_model" not in st.session_state:
    st.session_state.ai_advice_model = None

col1, col2 = st.columns([3, 1])
with col1:
    st.write(f"📊 Analyzing **{len(expenses)}** transactions totaling **Rs. {total_spent:,.2f}**.")
with col2:
    generate_clicked = st.button("✨ Get My Advice", use_container_width=True)

if generate_clicked:
    with st.spinner("🤔 BudgetBuddy AI is reviewing your spending..."):
        summary = _build_expense_summary(expenses, category_totals, total_spent, monthly_budget)
        user_prompt = (
            "Here is this student's expense data:\n\n"
            f"{summary}\n\n"
            "Give me personalized budgeting advice based on this."
        )
        # Replaced ask_gemini with ask_groq
        success, result, model_used = ask_groq(prompt=user_prompt, system_instruction=SYSTEM_PROMPT)

    if success:
        st.session_state.ai_advice = result
        st.session_state.ai_advice_model = model_used
    else:
        st.session_state.ai_advice = None
        st.session_state.ai_advice_model = None
        st.error(result)

# ----------------------------------------------------------------------------
# Display advice card
# ----------------------------------------------------------------------------

if st.session_state.ai_advice:
    st.markdown(
        f"""
        <div class="bb-advice-card">
            <div class="bb-advice-header">
                <span style="font-size:1.6rem;">🧠</span>
                <h3>BudgetBuddy's Advice for You</h3>
            </div>
            {st.session_state.ai_advice}
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.session_state.ai_advice_model:
        st.caption(f"🔧 Generated using Groq model: `{st.session_state.ai_advice_model}`")
else:
    st.info("👆 Click **Get My Advice** to receive personalized budgeting tips based on your spending.")