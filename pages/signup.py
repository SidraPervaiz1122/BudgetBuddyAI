"""
pages/signup.py

BudgetBuddy AI - Signup Page
-------------------------------
A modern, centered signup card for creating a new BudgetBuddy AI account.
Validates input client-side before delegating account creation (with bcrypt
password hashing) to database/db.py.
"""

import re
import streamlit as st
from database.db import register_user

# ----------------------------------------------------------------------------
# Page configuration
# ----------------------------------------------------------------------------

st.set_page_config(page_title="Sign Up | BudgetBuddy AI", page_icon="💰", layout="centered")

EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"


# ----------------------------------------------------------------------------
# Styling (original palette restored, no external font fetch)
# ----------------------------------------------------------------------------

st.markdown(
    """
    <style>
        .block-container { max-width: 460px; padding-top: 3rem; }

        .auth-brand { text-align: center; padding-bottom: 10px; }
        .auth-logo-badge {
            width: 56px; height: 56px; margin: 0 auto 10px auto;
            border-radius: 16px;
            background: linear-gradient(90deg, #16a34a, #22c55e);
            display: flex; align-items: center; justify-content: center;
            font-size: 26px;
            box-shadow: 0 8px 20px rgba(22, 163, 74, 0.3);
        }
        .auth-brand h1 { font-size: 2.2rem; margin-bottom: 0; }
        .auth-brand p { color: #8a8a8a; font-size: 1rem; margin-top: 4px; }

        div[data-testid="stForm"] {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(150, 150, 150, 0.15);
            border-radius: 16px;
            padding: 2rem 2rem 1rem 2rem;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
        }

        .stTextInput input { border-radius: 10px !important; }

        div.stButton > button, div.stFormSubmitButton > button {
            width: 100%;
            border-radius: 10px;
            padding: 0.6rem 0;
            font-weight: 600;
            background: linear-gradient(90deg, #16a34a, #22c55e);
            color: white;
            border: none;
        }
        div.stButton > button:hover, div.stFormSubmitButton > button:hover {
            background: linear-gradient(90deg, #15803d, #16a34a);
            color: white;
        }

        .secondary-btn button {
            background: rgba(150, 150, 150, 0.08) !important;
            border: 1px solid rgba(150, 150, 150, 0.25) !important;
            box-shadow: none !important;
        }
        .secondary-btn button:hover { background: rgba(150, 150, 150, 0.15) !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------------

st.markdown(
    """
    <div class="auth-brand">
        <div class="auth-logo-badge">✨</div>
        <h1>💰 BudgetBuddy AI</h1>
        <p>✨ Create your account and take control of your finances</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")


# ----------------------------------------------------------------------------
# Signup form
# ----------------------------------------------------------------------------

with st.form("signup_form", clear_on_submit=False):
    st.markdown("### 📝 Create Account")

    name = st.text_input("👤 Full Name", placeholder="e.g. Sidra Khan")
    email = st.text_input("📧 Email Address", placeholder="you@example.com")
    password = st.text_input("🔒 Password", type="password", placeholder="At least 8 characters")
    confirm_password = st.text_input(
        "🔒 Confirm Password", type="password", placeholder="Re-enter your password"
    )

    submitted = st.form_submit_button("🚀 Sign Up")

    if submitted:
        # --- Validation ---
        if not name.strip() or not email.strip() or not password or not confirm_password:
            st.error("⚠️ Please fill in all fields before continuing.")

        elif not re.match(EMAIL_REGEX, email.strip()):
            st.error("⚠️ Please enter a valid email address.")

        elif len(password) < 8:
            st.error("⚠️ Password must be at least 8 characters long.")

        elif password != confirm_password:
            st.error("⚠️ Passwords do not match. Please try again.")

        else:
            with st.spinner("Creating your account..."):
                success, message = register_user(name.strip(), email.strip(), password)

            if success:
                st.success(f"✅ {message} You can now log in. 🎉")
                st.info("👉 Head to the Login page to access your dashboard.")
            else:
                st.error(f"❌ {message}")


# ----------------------------------------------------------------------------
# Switch to login
# ----------------------------------------------------------------------------

st.write("")
st.markdown("<div style='text-align:center;'>Already have an account?</div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    st.markdown("<div class='secondary-btn'>", unsafe_allow_html=True)
    if st.button("🔑 Go to Login"):
        st.switch_page("pages/login.py")
    st.markdown("</div>", unsafe_allow_html=True)