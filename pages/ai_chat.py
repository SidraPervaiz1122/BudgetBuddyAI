"""
pages/ai_chat.py
"""
import streamlit as st
from database.db import (
    get_user_expenses, 
    get_category_totals, 
    get_total_expense, 
    get_user_budget
)
from utils.helpers import (
    format_currency,
    calculate_remaining_budget,
    calculate_savings_percentage,
    ask_groq
)
from components.sidebar import render_sidebar
from components.navbar import render_navbar

# ----------------------------------------------------------------------------
# Page configuration & auth guard
# ----------------------------------------------------------------------------

st.set_page_config(page_title="AI Chat | BudgetBuddy AI", page_icon="💬", layout="wide")

if not st.session_state.get("logged_in"):
    st.warning("⚠️ Please log in to use the AI Chat.")
    st.switch_page("pages/login.py")
    st.stop()

user_id = st.session_state["user_id"]
user_name = st.session_state.get("user_name", "there")

# ----------------------------------------------------------------------------
# Layout shell
# ----------------------------------------------------------------------------

render_sidebar(active_page="AI Chat")
render_navbar(page_title="AI Chat", user_name=user_name)

st.markdown("### 💬 BudgetBuddy AI Chat Assistant")
st.caption("Chat with your personal financial advisor about your spending, budget, and saving goals.")

# ----------------------------------------------------------------------------
# Initialize Chat History in Session State
# ----------------------------------------------------------------------------

if "ai_chat_messages" not in st.session_state:
    st.session_state.ai_chat_messages = [
        {
            "role": "assistant", 
            "content": f"Hello {user_name}! I'm your BudgetBuddy AI assistant. Ask me anything about your budget, spending habits, or how to reach your savings goals!"
        }
    ]

# Display existing chat messages
for message in st.session_state.ai_chat_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ----------------------------------------------------------------------------
# Gather User Financial Context
# ----------------------------------------------------------------------------

budget = get_user_budget(user_id) or 0.0
total_spent = get_total_expense(user_id) or 0.0
remaining = calculate_remaining_budget(budget, total_spent)
savings_pct = calculate_savings_percentage(budget, total_spent)
category_totals = get_category_totals(user_id) or {}
expenses = get_user_expenses(user_id) or []

cat_breakdown_str = ", ".join([f"{cat}: {format_currency(amt)}" for cat, amt in category_totals.items()]) if category_totals else "No expenses categorized yet."
recent_exp_str = "\n".join([f"- {e.get('date')}: {format_currency(e.get('amount'))} on {e.get('category')} ({e.get('description', 'No desc')})" for e in expenses[:5]]) if expenses else "No recent expenses recorded."

financial_context = f"""
Student Financial Profile:
- Current Budget: {format_currency(budget)}
- Total Spending: {format_currency(total_spent)}
- Remaining Budget: {format_currency(remaining)}
- Savings Percentage: {savings_pct:.1f}%
- Category Breakdown: {cat_breakdown_str}
- Recent Expenses:
{recent_exp_str}
"""

SYSTEM_PROMPT = """You are BudgetBuddy AI.
You are a friendly financial advisor for university students.
Always answer politely.
Give practical budgeting advice.
Never recommend risky investments.
Keep responses concise.
Use the user's own spending data whenever possible."""

# ----------------------------------------------------------------------------
# Chat Input & AI Response Generation
# ----------------------------------------------------------------------------

if prompt := st.chat_input("Ask me how to save money or analyze your expenses..."):
    # Append user message
    st.session_state.ai_chat_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            full_prompt = f"{financial_context}\n\nUser Question: {prompt}"
            success, response_text, model_used = ask_groq(prompt=full_prompt, system_instruction=SYSTEM_PROMPT)
            
            if success:
                ai_reply = response_text
            else:
                ai_reply = f"⚠️ {response_text}"
            
            st.markdown(ai_reply)
    
    # Append assistant response to history
    st.session_state.ai_chat_messages.append({"role": "assistant", "content": ai_reply})