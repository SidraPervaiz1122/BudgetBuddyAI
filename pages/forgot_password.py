"""
pages/forgot_password.py

BudgetBuddy AI - Forgot Password
-------------------------------------
A professional, real-world-style password reset flow with three distinct
steps:

  Step 1 (request):  user enters the email they signed up with -> if it
                      exists, a 6-digit OTP is generated, hashed and stored
                      with a 10-minute expiry via database/db.py, and
                      emailed to that same address via utils/helpers.py.

  Step 2 (verify):    user enters ONLY the 6-digit code. Distinct, specific
                      errors are shown for a wrong code vs. an expired one,
                      matching how real apps (Gmail, banking apps, etc.)
                      handle this - the user isn't asked to retype a new
                      password until the code itself has been confirmed.

  Step 3 (reset):     user sets a new password (+ confirmation). On
                      success the OTP is deleted and the user is sent back
                      to Login with a clear success message.
"""

import streamlit as st

from database.db import (
    get_user_by_email,
    create_password_reset_code,
    verify_password_reset_code,
    reset_user_password,
)
from utils.helpers import send_reset_code_email

# ----------------------------------------------------------------------------
# Page configuration
# ----------------------------------------------------------------------------

st.set_page_config(page_title="Forgot Password | BudgetBuddy AI", page_icon="🔐", layout="centered")


# ----------------------------------------------------------------------------
# Session state
# ----------------------------------------------------------------------------

if "fp_step" not in st.session_state:
    st.session_state.fp_step = "request"      # "request" -> "verify" -> "reset" -> "done"
if "fp_email" not in st.session_state:
    st.session_state.fp_email = ""
if "fp_user_name" not in st.session_state:
    st.session_state.fp_user_name = ""
if "fp_code_verified" not in st.session_state:
    st.session_state.fp_code_verified = False


# ----------------------------------------------------------------------------
# Styling - same restored palette as login/signup, no external font fetch
# ----------------------------------------------------------------------------

st.markdown(
    """
    <style>
        .block-container { max-width: 460px; padding-top: 3rem; }

        .auth-brand { text-align: center; padding-bottom: 6px; }
        .auth-logo-badge {
            width: 56px; height: 56px; margin: 0 auto 10px auto;
            border-radius: 16px;
            background: linear-gradient(90deg, #2563eb, #3b82f6);
            display: flex; align-items: center; justify-content: center;
            font-size: 26px;
            box-shadow: 0 8px 20px rgba(37, 99, 235, 0.3);
        }
        .auth-brand h1 { font-size: 1.7rem; margin-bottom: 0; }
        .auth-brand p { color: #8a8a8a; font-size: 0.95rem; margin-top: 4px; }

        .fp-steps { display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 1.4rem; }
        .fp-step-dot { width: 8px; height: 8px; border-radius: 50%; background: rgba(150,150,150,0.3); }
        .fp-step-dot.active { background: #2563eb; box-shadow: 0 0 0 4px rgba(37,99,235,0.15); }
        .fp-step-line { width: 32px; height: 2px; background: rgba(150,150,150,0.25); }

        div[data-testid="stForm"] {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(150, 150, 150, 0.15);
            border-radius: 16px;
            padding: 2rem 2rem 1rem 2rem;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
        }
        div[data-testid="stForm"] p.fp-sub { color: #8a8a8a; font-size: 0.86rem; margin-bottom: 1.1rem; }

        .stTextInput input { border-radius: 10px !important; }

        div.stButton > button, div.stFormSubmitButton > button {
            width: 100%;
            border-radius: 10px;
            padding: 0.6rem 0;
            font-weight: 600;
            background: linear-gradient(90deg, #2563eb, #3b82f6);
            color: white;
            border: none;
        }
        div.stButton > button:hover, div.stFormSubmitButton > button:hover {
            background: linear-gradient(90deg, #1d4ed8, #2563eb);
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


def _render_step_indicator(active_step: int):
    """Three-dot progress indicator: Email -> Code -> New Password."""
    dots = []
    for i in (1, 2, 3):
        state = "active" if active_step >= i else ""
        dots.append(f'<div class="fp-step-dot {state}"></div>')
        if i < 3:
            dots.append('<div class="fp-step-line"></div>')
    st.markdown(f'<div class="fp-steps">{"".join(dots)}</div>', unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------------

st.markdown(
    """
    <div class="auth-brand">
        <div class="auth-logo-badge">🔐</div>
        <h1>Reset your password</h1>
        <p>We'll send a verification code to your email</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================================
# STEP 1 - Request reset code
# ============================================================================

if st.session_state.fp_step == "request":
    _render_step_indicator(1)

    with st.form("fp_request_form"):
        st.markdown("### 📧 Enter your email")
        st.markdown(
            "<p class='fp-sub'>Enter the email you signed up with — we'll send a 6-digit code to verify it's you.</p>",
            unsafe_allow_html=True,
        )

        email = st.text_input("Email address", placeholder="you@example.com")
        submitted = st.form_submit_button("Send Reset Code")

        if submitted:
            if not email.strip():
                st.error("⚠️ Please enter your email address.")
            else:
                with st.spinner("Sending code..."):
                    user = get_user_by_email(email.strip())
                    sent, msg = (False, None)
                    if user:
                        code = create_password_reset_code(email.strip())
                        sent, msg = send_reset_code_email(
                            to_email=email.strip(), user_name=user.get("name", ""), code=code
                        )

                if not user:
                    st.error("❌ No account exists with this email.")
                elif sent:
                    st.session_state.fp_email = email.strip()
                    st.session_state.fp_user_name = user.get("name", "")
                    st.session_state.fp_code_verified = False
                    st.session_state.fp_step = "verify"
                    st.success("✅ Code sent! Check your inbox.")
                    st.rerun()
                else:
                    st.error(f"❌ Couldn't send the email: {msg}")

    st.write("")
    st.markdown("<div style='text-align:center;'>Remembered your password?</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown("<div class='secondary-btn'>", unsafe_allow_html=True)
        if st.button("Back to Login", use_container_width=True):
            st.switch_page("pages/login.py")
        st.markdown("</div>", unsafe_allow_html=True)


# ============================================================================
# STEP 2 - Verify the OTP only (password comes after, like a real app)
# ============================================================================

elif st.session_state.fp_step == "verify":
    _render_step_indicator(2)

    with st.form("fp_verify_form"):
        st.markdown("### 🔢 Enter your verification code")
        st.markdown(
            f"<p class='fp-sub'>We sent a 6-digit code to <b>{st.session_state.fp_email}</b>. "
            "It expires 10 minutes after being sent.</p>",
            unsafe_allow_html=True,
        )

        code = st.text_input("Verification code", placeholder="6-digit code", max_chars=6)
        submitted = st.form_submit_button("Verify Code")

        if submitted:
            if not code.strip():
                st.error("⚠️ Please enter the verification code.")
            else:
                is_valid, reason = verify_password_reset_code(st.session_state.fp_email, code.strip())

                if is_valid:
                    st.session_state.fp_code_verified = True
                    st.session_state.fp_step = "reset"
                    st.rerun()
                elif reason == "expired":
                    st.error("❌ Verification code has expired. Please request a new one.")
                elif reason == "locked":
                    st.error("❌ Too many incorrect attempts. Please request a new verification code.")
                else:
                    # Covers "invalid" (wrong code) and "not_found" (no code
                    # was ever requested) with the same friendly message,
                    # so we never reveal which case it is.
                    st.error("❌ Invalid verification code.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='secondary-btn'>", unsafe_allow_html=True)
        if st.button("Resend code", use_container_width=True):
            code = create_password_reset_code(st.session_state.fp_email)
            send_reset_code_email(
                to_email=st.session_state.fp_email,
                user_name=st.session_state.fp_user_name,
                code=code,
            )
            st.success("✅ A new code has been sent.")
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='secondary-btn'>", unsafe_allow_html=True)
        if st.button("Use a different email", use_container_width=True):
            st.session_state.fp_step = "request"
            st.session_state.fp_code_verified = False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


# ============================================================================
# STEP 3 - Set the new password (only reachable after a verified code)
# ============================================================================

elif st.session_state.fp_step == "reset":
    if not st.session_state.fp_code_verified:
        # Guard against someone manually landing on this step without
        # having verified a code first.
        st.session_state.fp_step = "request"
        st.rerun()

    _render_step_indicator(3)

    with st.form("fp_reset_form"):
        st.markdown("### 🔑 Set your new password")
        st.markdown(
            f"<p class='fp-sub'>Verified! Choose a new password for <b>{st.session_state.fp_email}</b>.</p>",
            unsafe_allow_html=True,
        )

        new_password = st.text_input("New password", type="password", placeholder="At least 8 characters")
        confirm_password = st.text_input("Confirm new password", type="password", placeholder="Re-enter new password")

        submitted = st.form_submit_button("Reset Password")

        if submitted:
            if not new_password or not confirm_password:
                st.error("⚠️ Please fill in both password fields.")
            elif len(new_password) < 8:
                st.error("⚠️ Password must be at least 8 characters long.")
            elif new_password != confirm_password:
                st.error("⚠️ Passwords do not match.")
            else:
                success, message = reset_user_password(st.session_state.fp_email, new_password)
                if success:
                    st.session_state.fp_step = "done"
                    st.session_state.fp_code_verified = False
                    st.rerun()
                else:
                    st.error(f"❌ {message}")


# ============================================================================
# DONE - success screen
# ============================================================================

elif st.session_state.fp_step == "done":
    st.success("✅ Your password has been reset successfully. Please log in with your new password.")
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        if st.button("Go to Login", use_container_width=True):
            st.session_state.fp_step = "request"
            st.session_state.fp_email = ""
            st.session_state.fp_user_name = ""
            st.session_state.fp_code_verified = False
            st.switch_page("pages/login.py")