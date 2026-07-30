"""
sidebar.py

BudgetBuddy AI - Sidebar Navigation
---------------------------------------
A polished, professional fintech-style sidebar shared across all pages of
the app. Displays the BudgetBuddy AI logo, the logged-in user's avatar and
name, navigation links with active-page highlighting, and a logout control.

Usage:
    from sidebar import render_sidebar
    render_sidebar(active_page="Dashboard")
"""

import calendar
from datetime import date

import streamlit as st

from utils.helpers import load_budget, load_all_expenses, filter_by_date_range, compute_total, format_currency

# ----------------------------------------------------------------------------
# Navigation configuration
# ----------------------------------------------------------------------------

NAV_ITEMS = [
    {"label": "Dashboard", "icon": "🏠", "page": "pages/dashboard.py"},
    {"label": "Add Expense", "icon": "➕", "page": "pages/add_expense.py"},
    {"label": "Analytics", "icon": "📊", "page": "pages/analytics.py"},
    {"label": "AI Advisor", "icon": "🤖", "page": "pages/ai_advisor.py"},
    {"label": "AI Chat", "icon": "💬", "page": "pages/ai_chat.py"},
    {"label": "Reports", "icon": "📄", "page": "pages/reports.py"},
]


def _get_initials(name):
    """Derives up to two uppercase initials from a user's full name."""
    if not name:
        return "U"
    parts = [p for p in name.strip().split(" ") if p]
    if not parts:
        return "U"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def render_sidebar(active_page="Dashboard"):
    """
    Renders the BudgetBuddy AI sidebar with logo, navigation, active-page
    highlighting, the logged-in user's avatar/name, and a logout button.

    Args:
        active_page (str): The label of the currently active page
            (must match one of the entries in NAV_ITEMS, e.g. "Dashboard").
    """

    # -- Styling --------------------------------------------------------
    st.markdown(
        """
        <style>
            section[data-testid="stSidebar"] {
                background: linear-gradient(180deg, #0b0f19 0%, #0a0e1a 100%) !important;
                border-right: 1px solid rgba(255, 255, 255, 0.06);
            }

            section[data-testid="stSidebar"] * {
                font-family: 'Segoe UI', sans-serif;
                color: #f3f4f6;
            }

            /* Note: the sidebar collapse arrow's icon rendering is handled
               globally in app.py (a network-independent CSS triangle),
               which also covers this icon since it lives inside this
               sidebar container. */

            section[data-testid="stSidebar"] > div {
                padding-top: 0.5rem;
            }

            /* ---------------- Logo ---------------- */
            .bb-logo {
                display: flex; align-items: center; gap: 12px;
                padding: 0.9rem 0.4rem 1.1rem 0.4rem;
            }
            .bb-logo-badge {
                width: 42px; height: 42px; flex-shrink: 0;
                border-radius: 12px;
                background: linear-gradient(135deg, #6366f1, #8b5cf6);
                display: flex; align-items: center; justify-content: center;
                font-size: 20px;
                box-shadow: 0 6px 18px rgba(99, 102, 241, 0.4);
            }
            .bb-logo-text h2 {
                font-size: 1.08rem; font-weight: 800; margin: 0;
                color: #ffffff !important; letter-spacing: -0.02em; line-height: 1.2;
            }
            .bb-logo-text p {
                font-size: 0.68rem; color: #7c85a3 !important; margin: 1px 0 0 0;
                text-transform: uppercase; letter-spacing: 0.06em;
            }

            /* ---------------- User Profile Card ---------------- */
            .bb-user-card {
                display: flex; align-items: center; gap: 10px;
                background: rgba(255, 255, 255, 0.045);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 14px;
                padding: 0.7rem 0.85rem;
                margin: 0 0 1.3rem 0;
            }
            .bb-user-avatar {
                width: 38px; height: 38px; flex-shrink: 0;
                border-radius: 50%;
                background: linear-gradient(135deg, #2563eb, #7c3aed);
                color: #ffffff !important;
                display: flex; align-items: center; justify-content: center;
                font-weight: 700; font-size: 0.85rem;
            }
            .bb-user-info p { margin: 0; line-height: 1.25; }
            .bb-user-name {
                font-size: 0.88rem; font-weight: 600; color: #f8fafc !important;
            }
            .bb-user-sub {
                font-size: 0.72rem; color: #7c85a3 !important;
            }

            /* ---------------- Section label ---------------- */
            .bb-section-label {
                font-size: 0.68rem; font-weight: 700; color: #56607a !important;
                text-transform: uppercase; letter-spacing: 0.08em;
                margin: 0.2rem 0 0.55rem 0.3rem;
            }

            /* ---------------- Nav buttons ---------------- */
            section[data-testid="stSidebar"] .stButton {
                width: 100% !important;
                margin-bottom: 4px !important;
            }

            section[data-testid="stSidebar"] .stButton > button {
                width: 100% !important;
                display: flex !important;
                justify-content: flex-start !important;
                align-items: center !important;
                gap: 10px;
                background: transparent !important;
                border: 1px solid transparent !important;
                color: #b6bdd1 !important;
                padding: 0.62rem 0.85rem !important;
                border-radius: 10px !important;
                font-size: 0.9rem !important;
                font-weight: 500 !important;
                box-sizing: border-box !important;
                transition: all 0.15s ease-in-out;
            }

            section[data-testid="stSidebar"] .stButton > button p {
                color: #b6bdd1 !important;
                font-size: 0.9rem !important;
                font-weight: 500 !important;
                margin: 0 !important;
                text-align: left !important;
            }

            section[data-testid="stSidebar"] .stButton > button:hover {
                background: rgba(255, 255, 255, 0.06) !important;
                border-color: rgba(255, 255, 255, 0.08) !important;
            }
            section[data-testid="stSidebar"] .stButton > button:hover p {
                color: #ffffff !important;
            }

            /* ---------------- Active nav pill ---------------- */
            .bb-active-nav {
                position: relative;
                background: linear-gradient(90deg, rgba(99,102,241,0.18), rgba(139,92,246,0.10)) !important;
                color: #ffffff !important;
                border-radius: 10px !important;
                padding: 0.62rem 0.85rem 0.62rem 1.1rem !important;
                margin-bottom: 4px !important;
                font-weight: 600 !important;
                font-size: 0.9rem !important;
                display: flex;
                align-items: center;
                gap: 10px;
                border: 1px solid rgba(139, 130, 246, 0.28);
                box-sizing: border-box;
                width: 100%;
            }
            .bb-active-nav::before {
                content: "";
                position: absolute;
                left: 0; top: 14%; bottom: 14%;
                width: 3px; border-radius: 3px;
                background: linear-gradient(180deg, #818cf8, #a78bfa);
            }

            /* ---------------- Divider ---------------- */
            section[data-testid="stSidebar"] hr {
                border-color: rgba(255, 255, 255, 0.07) !important;
                margin: 1.1rem 0 !important;
            }

            /* ---------------- Logout ---------------- */
            .bb-logout .stButton > button {
                color: #f87171 !important;
                background: rgba(239, 68, 68, 0.06) !important;
                border: 1px solid rgba(239, 68, 68, 0.18) !important;
            }
            .bb-logout .stButton > button p { color: #f87171 !important; }
            .bb-logout .stButton > button:hover {
                background: rgba(239, 68, 68, 0.16) !important;
                border-color: rgba(239, 68, 68, 0.35) !important;
            }
            .bb-logout .stButton > button:hover p { color: #fca5a5 !important; }

            /* ---------------- Bottom overview stats ---------------- */
            .bb-stats-box {
                background: rgba(255, 255, 255, 0.04);
                border: 1px solid rgba(255, 255, 255, 0.07);
                border-radius: 12px;
                padding: 0.65rem 0.85rem;
                margin-bottom: 0.4rem;
            }
            .bb-stat-row {
                display: flex; justify-content: space-between; align-items: center;
                font-size: 0.78rem; padding: 0.3rem 0;
            }
            .bb-stat-row:not(:last-child) {
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            }
            .bb-stat-row span:first-child { color: #8b93ab !important; }
            .bb-stat-row span:last-child { font-weight: 600; color: #f1f5f9 !important; }
            .bb-stat-positive { color: #4ade80 !important; }
            .bb-stat-negative { color: #f87171 !important; }

            /* ---------------- Footer tag ---------------- */
            .bb-sidebar-footer {
                text-align: center; color: #3f4863 !important;
                font-size: 0.68rem; margin-top: 1rem; letter-spacing: 0.03em;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        # -- Logo ---------------------------------------------------------
        st.markdown(
            """
            <div class="bb-logo">
                <div class="bb-logo-badge">💰</div>
                <div class="bb-logo-text">
                    <h2>BudgetBuddy AI</h2>
                    <p>Smart Money, Smarter You</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # -- Logged-in user -------------------------------------------------
        user_name = st.session_state.get("user_name", "Guest")
        initials = _get_initials(user_name)
        st.markdown(
            f"""
            <div class="bb-user-card">
                <div class="bb-user-avatar">{initials}</div>
                <div class="bb-user-info">
                    <p class="bb-user-name">{user_name}</p>
                    <p class="bb-user-sub">Welcome back 👋</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # -- Navigation -------------------------------------------------
        st.markdown('<p class="bb-section-label">Menu</p>', unsafe_allow_html=True)

        for item in NAV_ITEMS:
            is_active = item["label"] == active_page

            if is_active:
                st.markdown(
                    f'<div class="bb-active-nav"><span>{item["icon"]}</span> <span>{item["label"]}</span></div>',
                    unsafe_allow_html=True,
                )
            else:
                if st.button(f'{item["icon"]}    {item["label"]}', key=f"nav_{item['label']}"):
                    st.switch_page(item["page"])

        st.markdown("---")

        # -- Bottom overview: current budget, remaining, current month ------
        user_id = st.session_state.get("user_id")
        if user_id:
            today = date.today()
            month_start = today.replace(day=1).strftime("%Y-%m-%d")
            _, last_day = calendar.monthrange(today.year, today.month)
            month_end = today.replace(day=last_day).strftime("%Y-%m-%d")

            budget = load_budget(user_id) or 0.0
            all_expenses = load_all_expenses(user_id)
            month_expenses = filter_by_date_range(all_expenses, month_start, month_end)
            spent = compute_total(month_expenses)
            remaining = budget - spent
            remaining_class = "bb-stat-positive" if remaining >= 0 else "bb-stat-negative"

            st.markdown('<p class="bb-section-label">Overview</p>', unsafe_allow_html=True)
            st.markdown(
                f"""
                <div class="bb-stats-box">
                    <div class="bb-stat-row"><span>💰 Current Budget</span><span>{format_currency(budget)}</span></div>
                    <div class="bb-stat-row"><span>💵 Remaining</span><span class="{remaining_class}">{format_currency(remaining)}</span></div>
                    <div class="bb-stat-row"><span>📅 Month</span><span>{today.strftime('%B %Y')}</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # -- Logout -------------------------------------------------
        st.markdown('<div class="bb-logout">', unsafe_allow_html=True)
        if st.button("🚪    Logout", key="nav_logout"):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.user_name = None
            st.switch_page("pages/login.py")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="bb-sidebar-footer">BudgetBuddy AI · v1.0</div>', unsafe_allow_html=True)