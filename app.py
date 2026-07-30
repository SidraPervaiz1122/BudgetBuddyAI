"""
app.py

BudgetBuddy AI - Main Application Entry Point
--------------------------------------------------
Initializes session state, loads global custom CSS, and wires up
Streamlit's multipage navigation. Guests can only reach Login/Signup/
Forgot Password; logged-in users get Dashboard, Add Expense, Analytics,
AI Advisor, AI Chat, Reports, and Logout. The actual sidebar UI (logo, nav
highlighting, logout button) is rendered per-page by components/sidebar.py.
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

            html, body {
                font-family: "Segoe UI", "Inter", sans-serif;
            }

            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}

            /* Streamlit's own chrome icons (sidebar collapse arrow, expander
               toggle chevron, etc.) render as a literal ligature word like
               "keyboard_double_arrow_right" whenever the Material Symbols
               web font fails to load (e.g. no network access to Google
               Fonts from wherever this app is hosted). Trying to force the
               right font-family isn't reliable since it depends on that
               font actually downloading - so instead we hide the raw text
               completely and draw a small triangle with plain CSS borders.
               This can never render as broken text again, on any page,
               regardless of network conditions or Streamlit version. */
            [data-testid="stIconMaterial"] {
                font-size: 0 !important;
                color: transparent !important;
                display: inline-block !important;
                position: relative;
                width: 14px;
                height: 14px;
                vertical-align: middle;
            }
            [data-testid="stIconMaterial"]::before {
                content: "";
                position: absolute;
                top: 50%; left: 50%;
                width: 0; height: 0;
                border-top: 5px solid transparent;
                border-bottom: 5px solid transparent;
                border-left: 7px solid #94a3b8;
                transform: translate(-50%, -50%);
            }

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

            /* ---------------- Global responsiveness ---------------- */
            /* Prevent any element from forcing horizontal scroll. */
            * { box-sizing: border-box; }
            img, .stPlotlyChart, .stDataFrame { max-width: 100%; }

            /* Buttons scale down slightly and stay full-width on small screens. */
            @media (max-width: 768px) {
                .block-container { padding-left: 1rem !important; padding-right: 1rem !important; }
                div.stButton > button, div.stFormSubmitButton > button {
                    font-size: 0.88rem !important;
                    padding: 0.55rem 0 !important;
                }
                h1 { font-size: 1.5rem !important; }
                h2 { font-size: 1.25rem !important; }
                h3 { font-size: 1.05rem !important; }
            }

            @media (max-width: 480px) {
                .block-container { padding-left: 0.75rem !important; padding-right: 0.75rem !important; }
                div[data-testid="stMetricValue"] { font-size: 1.1rem !important; }
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
forgot_password_page = st.Page(
    "pages/forgot_password.py", title="Forgot Password", icon="🔐", url_path="forgot-password"
)

dashboard_page = st.Page(
    "pages/dashboard.py", title="Dashboard", icon="🏠", url_path="dashboard",
    default=st.session_state.logged_in,
)
add_expense_page = st.Page("pages/add_expense.py", title="Add Expense", icon="➕", url_path="add-expense")
analytics_page = st.Page("pages/analytics.py", title="Analytics", icon="📊", url_path="analytics")
ai_advisor_page = st.Page("pages/ai_advisor.py", title="AI Advisor", icon="🤖", url_path="ai-advisor")
ai_chat_page = st.Page("pages/ai_chat.py", title="AI Chat", icon="💬", url_path="ai-chat")
reports_page = st.Page("pages/reports.py", title="Reports", icon="📄", url_path="reports")

all_pages = [
    login_page,
    signup_page,
    forgot_password_page,   # <-- newly registered
    dashboard_page,
    add_expense_page,
    analytics_page,
    ai_advisor_page,
    ai_chat_page,
    reports_page,
]

# Streamlit renders its own top nav based on `all_pages`; we keep it hidden
# (see load_custom_css) and let components/sidebar.py, called from within
# each individual page, provide the visible navigation instead.
current_page = st.navigation(all_pages, position="hidden")
current_page.run()