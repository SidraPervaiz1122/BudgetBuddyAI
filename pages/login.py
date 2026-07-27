"""
pages/login.py

BudgetBuddy AI - Login Page
-------------------------------
A premium, centered login card that authenticates users against
database/db.py and stores session state on success before navigating
to the Dashboard.
"""

import streamlit as st
from database.db import login_user

# ----------------------------------------------------------------------------
# Page configuration
# ----------------------------------------------------------------------------

st.set_page_config(page_title="Login | BudgetBuddy AI", page_icon="💰", layout="centered")


# ----------------------------------------------------------------------------
# Session state initialization
# ----------------------------------------------------------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None


# ----------------------------------------------------------------------------
# Styling
# ----------------------------------------------------------------------------

st.markdown(
    """
    <style>
        .login-header {
            text-align: center;
            padding-bottom: 10px;
        }
        .login-header h1 {
            font-size: 2.2rem;
            margin-bottom: 0;
        }
        .login-header p {
            color: #8a8a8a;
            font-size: 1rem;
            margin-top: 4px;
        }
        div[data-testid="stForm"] {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(150, 150, 150, 0.15);
            border-radius: 16px;
            padding: 2rem 2rem 1rem 2rem;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
        }
        div.stButton > button {
            width: 100%;
            border-radius: 10px;
            padding: 0.6rem 0;
            font-weight: 600;
            background: linear-gradient(90deg, #2563eb, #3b82f6);
            color: white;
            border: none;
        }
        div.stButton > button:hover {
            background: linear-gradient(90deg, #1d4ed8, #2563eb);
            color: white;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------------

st.markdown(
    """
    <div class="login-header">
        <h1>💰 BudgetBuddy AI</h1>
        <p>🔐 Welcome back! Log in to manage your budget</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")


# ----------------------------------------------------------------------------
# Login form
# ----------------------------------------------------------------------------

with st.form("login_form", clear_on_submit=False):
    st.markdown("### 🔑 Login")

    email = st.text_input("📧 Email Address", placeholder="you@example.com")
    password = st.text_input("🔒 Password", type="password", placeholder="Your password")

    submitted = st.form_submit_button("➡️ Log In")

    if submitted:
        if not email.strip() or not password:
            st.error("⚠️ Please enter both email and password.")
        else:
            success, message, user_data = login_user(email.strip(), password)

            if success:
                st.session_state.logged_in = True
                st.session_state.user_id = user_data["id"]
                st.session_state.user_name = user_data["name"]

                st.success(f"✅ Welcome back, {user_data['name']}! 🎉")
                st.switch_page("pages/dashboard.py")
            else:
                st.error(f"❌ {message}")


# ----------------------------------------------------------------------------
# Switch to signup
# ----------------------------------------------------------------------------

st.write("")
st.markdown("<div style='text-align:center;'>Don't have an account yet?</div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("📝 Go to Sign Up"):
        st.switch_page("pages/signup.py")