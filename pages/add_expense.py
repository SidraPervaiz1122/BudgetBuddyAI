"""
pages/add_expense.py

BudgetBuddy AI - Add Expense
--------------------------------
A clean, validated form for logging a new expense. Saves directly to the
database via database/db.py and gives clear success/error feedback.
"""

from datetime import date
import streamlit as st

from database.db import add_expense, get_user_expenses, update_expense, delete_expense
from utils.helpers import format_currency
from components.sidebar import render_sidebar
from components.navbar import render_navbar

# ----------------------------------------------------------------------------
# Page configuration & auth guard
# ----------------------------------------------------------------------------

st.set_page_config(page_title="Add Expense | BudgetBuddy AI", page_icon="➕", layout="wide")

if not st.session_state.get("logged_in"):
    st.warning("⚠️ Please log in to add an expense.")
    st.switch_page("pages/login.py")
    st.stop()

user_id = st.session_state["user_id"]
user_name = st.session_state.get("user_name", "there")

CATEGORIES = [
    "Food",
    "Transport",
    "Education",
    "Shopping",
    "Entertainment",
    "Bills",
    "Health",
    "Other",
]

CATEGORY_ICONS = {
    "Food": "🍔",
    "Transport": "🚗",
    "Education": "📚",
    "Shopping": "🛍️",
    "Entertainment": "🎬",
    "Bills": "🧾",
    "Health": "🏥",
    "Other": "🗂️",
}

# ----------------------------------------------------------------------------
# Layout shell
# ----------------------------------------------------------------------------

render_sidebar(active_page="Add Expense")
render_navbar(page_title="Add Expense", user_name=user_name)

st.markdown(
    """
    <style>
        div[data-testid="stForm"] {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(150, 150, 150, 0.15);
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
        }
        div.stButton > button, div.stFormSubmitButton > button {
            width: 100%;
            border-radius: 10px;
            padding: 0.6rem 0;
            font-weight: 600;
            background: linear-gradient(90deg, #16a34a, #22c55e);
            color: white;
            border: none;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("### ➕ Log a New Expense")
st.caption("💡 Keep your records up to date to get the most accurate insights.")

# ----------------------------------------------------------------------------
# Expense form
# ----------------------------------------------------------------------------

with st.form("add_expense_form", clear_on_submit=True):
    col1, col2 = st.columns(2)

    with col1:
        amount = st.number_input(
            "💵 Amount (PKR)",
            min_value=0.0,
            step=50.0,
            format="%.2f",
            help="Enter the amount you spent.",
        )
        category = st.selectbox(
            "🏷️ Category",
            options=CATEGORIES,
            format_func=lambda c: f"{CATEGORY_ICONS.get(c, '🗂️')} {c}",
        )

    with col2:
        expense_date = st.date_input("📅 Date", value=date.today(), max_value=date.today())
        description = st.text_input("📝 Description", placeholder="e.g. Groceries from the weekly market")

    submitted = st.form_submit_button("✅ Save Expense")

    if submitted:
        # --- Validation ---
        if amount is None or amount <= 0:
            st.error("⚠️ Please enter a valid amount greater than zero.")
        elif not category:
            st.error("⚠️ Please select a category.")
        elif not description or not description.strip():
            st.error("⚠️ Please provide a short description of the expense.")
        elif expense_date is None:
            st.error("⚠️ Please select a valid date.")
        else:
            success, message = add_expense(
                user_id=user_id,
                amount=amount,
                category=category,
                description=description.strip(),
                date=expense_date.strftime("%Y-%m-%d"),
            )

            if success:
                st.success(f"✅ {message} {CATEGORY_ICONS.get(category, '')} {category} - Rs. {amount:,.2f}")
            else:
                st.error(f"❌ {message}")

st.divider()

# ----------------------------------------------------------------------------
# Your Expenses - search, filter, edit, and delete
# ----------------------------------------------------------------------------

st.markdown("### 🧾 Your Expenses")

if "editing_expense_id" not in st.session_state:
    st.session_state.editing_expense_id = None

filter_col1, filter_col2 = st.columns([2, 1])
with filter_col1:
    search_term = st.text_input("🔍 Search by description", placeholder="e.g. groceries, bus, netflix")
with filter_col2:
    filter_category = st.selectbox("🏷️ Filter by category", options=["All"] + CATEGORIES)

expenses = get_user_expenses(
    user_id,
    category=None if filter_category == "All" else filter_category,
    search=search_term.strip() if search_term else None,
)

if not expenses:
    st.info("📭 No expenses match your search/filter yet. Try clearing the filters, or add your first expense above.")
else:
    st.caption(f"Showing {len(expenses)} expense(s).")

    for exp in expenses:
        exp_id = exp["id"]
        is_editing = st.session_state.editing_expense_id == exp_id

        with st.container(border=True):
            if is_editing:
                # --- Inline edit form ---
                st.markdown(f"**✏️ Editing expense #{exp_id}**")
                edit_col1, edit_col2 = st.columns(2)

                with edit_col1:
                    edit_amount = st.number_input(
                        "💵 Amount (PKR)", min_value=0.0, step=50.0, format="%.2f",
                        value=float(exp["amount"]), key=f"edit_amount_{exp_id}",
                    )
                    edit_category = st.selectbox(
                        "🏷️ Category", options=CATEGORIES,
                        index=CATEGORIES.index(exp["category"]) if exp["category"] in CATEGORIES else 0,
                        format_func=lambda c: f"{CATEGORY_ICONS.get(c, '🗂️')} {c}",
                        key=f"edit_category_{exp_id}",
                    )

                with edit_col2:
                    try:
                        current_date = date.fromisoformat(exp["date"])
                    except (ValueError, TypeError):
                        current_date = date.today()
                    edit_date = st.date_input(
                        "📅 Date", value=current_date, max_value=date.today(), key=f"edit_date_{exp_id}",
                    )
                    edit_description = st.text_input(
                        "📝 Description", value=exp.get("description") or "", key=f"edit_desc_{exp_id}",
                    )

                save_col, cancel_col = st.columns(2)
                with save_col:
                    if st.button("💾 Save Changes", key=f"save_{exp_id}", use_container_width=True):
                        if edit_amount <= 0:
                            st.error("⚠️ Amount must be greater than zero.")
                        elif not edit_description.strip():
                            st.error("⚠️ Please provide a description.")
                        else:
                            success, message = update_expense(
                                expense_id=exp_id,
                                amount=edit_amount,
                                category=edit_category,
                                description=edit_description.strip(),
                                date=edit_date.strftime("%Y-%m-%d"),
                                user_id=user_id,
                            )
                            if success:
                                st.session_state.editing_expense_id = None
                                st.success(f"✅ {message}")
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
                with cancel_col:
                    if st.button("✖️ Cancel", key=f"cancel_{exp_id}", use_container_width=True):
                        st.session_state.editing_expense_id = None
                        st.rerun()

            else:
                # --- Read-only row ---
                row_col1, row_col2, row_col3, row_col4 = st.columns([2, 2, 1, 1])

                with row_col1:
                    st.markdown(f"**{CATEGORY_ICONS.get(exp['category'], '🗂️')} {exp['category']}**")
                    st.caption(exp.get("description") or "No description")

                with row_col2:
                    st.write(f"📅 {exp['date']}")
                    st.write(f"💵 {format_currency(exp['amount'])}")

                with row_col3:
                    if st.button("✏️ Edit", key=f"edit_{exp_id}", use_container_width=True):
                        st.session_state.editing_expense_id = exp_id
                        st.rerun()

                with row_col4:
                    confirm_key = f"confirm_delete_{exp_id}"
                    if st.session_state.get(confirm_key):
                        if st.button("⚠️ Confirm", key=f"confirm_btn_{exp_id}", use_container_width=True):
                            success, message = delete_expense(exp_id, user_id=user_id)
                            st.session_state[confirm_key] = False
                            if success:
                                st.success(f"✅ {message}")
                            else:
                                st.error(f"❌ {message}")
                            st.rerun()
                    else:
                        if st.button("🗑️ Delete", key=f"delete_{exp_id}", use_container_width=True):
                            st.session_state[confirm_key] = True
                            st.rerun()

# ----------------------------------------------------------------------------
# Navigation shortcut
# ----------------------------------------------------------------------------

st.write("")
if st.button("⬅️ Back to Dashboard"):
    st.switch_page("pages/dashboard.py")