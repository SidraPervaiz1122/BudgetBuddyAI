"""
app.py

BudgetBuddy AI - Main Application Entry Point
--------------------------------------------------
Initializes session state, loads global custom CSS, and wires up
Streamlit's multipage navigation. Guests can only reach Login/Signup;
logged-in users get Dashboard, Add Expense, Analytics, AI Advisor,
AI Chat, Reports, and Logout. The actual sidebar UI (logo, nav highlighting,
logout button) is rendered per-page by components/sidebar.py.
"""

import streamlit as st

# ----------------------------------------------------------------------------
# Page configuration
# ----------------------------------------------------------------------------

st.set_page_config(
    page_title="BudgetBuddy AI",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ----------------------------------------------------------------------------
# Session state initialization
# ----------------------------------------------------------------------------

def init_session_state():
    """Ensures all session_state keys BudgetBuddy AI relies on exist."""
    defaults = {
        "logged_in": False,
        "user_id": None,
        "user_name": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


# ----------------------------------------------------------------------------
# Global custom CSS
# ----------------------------------------------------------------------------

def load_custom_css():
    """Loads app-wide custom styling shared across every page."""
    st.markdown(
        """
        <style>
            /* Hide Streamlit's default multipage nav - components/sidebar.py
               renders our own custom navigation instead. */
            div[data-testid="stSidebarNav"] {
                display: none;
            }

            html, body, [class*="css"] {
                font-family: "Segoe UI", "Inter", sans-serif;
            }

            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}

            .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
            }

            ::-webkit-scrollbar {
                width: 8px;
            }
            ::-webkit-scrollbar-thumb {
                background: rgba(150, 150, 150, 0.4);
                border-radius: 10px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


load_custom_css()


# ----------------------------------------------------------------------------
# Page definitions
# ----------------------------------------------------------------------------

login_page = st.Page(
    "pages/login.py", title="Login", icon="🔑", url_path="login",
    default=not st.session_state.logged_in,
)
signup_page = st.Page("pages/signup.py", title="Sign Up", icon="📝", url_path="signup")

dashboard_page = st.Page(
    "pages/dashboard.py", title="Dashboard", icon="🏠", url_path="dashboard",
    default=st.session_state.logged_in,
)
add_expense_page = st.Page("pages/add_expense.py", title="Add Expense", icon="➕", url_path="add-expense")
analytics_page = st.Page("pages/analytics.py", title="Analytics", icon="📊", url_path="analytics")
ai_advisor_page = st.Page("pages/ai_advisor.py", title="AI Advisor", icon="🤖", url_path="ai-advisor")
ai_chat_page = st.Page("pages/ai_chat.py", title="AI Chat", icon="💬", url_path="ai-chat")  # <-- Registered here
reports_page = st.Page("pages/reports.py", title="Reports", icon="📄", url_path="reports")

all_pages = [
    login_page,
    signup_page,
    dashboard_page,
    add_expense_page,
    analytics_page,
    ai_advisor_page,
    ai_chat_page,  # <-- Included in the navigation registry
    reports_page,
]

# Streamlit renders its own top nav based on `all_pages`; we keep it hidden
# (see load_custom_css) and let components/sidebar.py, called from within
# each individual page, provide the visible navigation instead.
current_page = st.navigation(all_pages, position="hidden")
current_page.run()