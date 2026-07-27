"""
sidebar.py

BudgetBuddy AI - Sidebar Navigation
---------------------------------------
A professional fintech-style sidebar shared across all pages of the app.
Displays the BudgetBuddy AI logo, the logged-in user's name, navigation
links with active-page highlighting, and a logout control.

Usage:
    from sidebar import render_sidebar
    render_sidebar(active_page="Dashboard")
"""

import streamlit as st

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


def render_sidebar(active_page="Dashboard"):
    """
    Renders the BudgetBuddy AI sidebar with logo, navigation, active-page
    highlighting, the logged-in user's name, and a logout button.

    Args:
        active_page (str): The label of the currently active page
            (must match one of the entries in NAV_ITEMS, e.g. "Dashboard").
    """

    # -- Styling --------------------------------------------------------
    st.markdown(
        """
        <style>
            /* Force solid, high-contrast background for the sidebar */
            section[data-testid="stSidebar"] {
                background-color: #0b0f19 !important;
                border-right: 1px solid rgba(255, 255, 255, 0.08);
            }
            
            section[data-testid="stSidebar"] * {
                color: #f3f4f6;
            }

            /* Logo Container */
            .bb-logo {
                text-align: center;
                padding: 1.2rem 0 0.8rem 0;
            }
            .bb-logo h2 {
                font-size: 1.35rem;
                font-weight: 700;
                margin-bottom: 0px;
                color: #ffffff !important;
                letter-spacing: -0.025em;
            }
            .bb-logo p {
                font-size: 0.75rem;
                color: #9ca3af !important;
                margin-top: 4px;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }

            /* User Profile Card */
            .bb-user-card {
                background: rgba(255, 255, 255, 0.04);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 12px;
                padding: 0.75rem 1rem;
                margin: 0.75rem 0 1.25rem 0;
                text-align: center;
                font-size: 0.9rem;
            }
            .bb-user-card strong {
                color: #60a5fa !important;
            }

            /* Force ALL sidebar buttons to match full-width container dimensions */
            section[data-testid="stSidebar"] .stButton {
                width: 100% !important;
            }

            section[data-testid="stSidebar"] .stButton > button {
                width: 100% !important;
                display: flex !important;
                justify-content: flex-start !important;
                align-items: center !important;
                background: rgba(255, 255, 255, 0.03) !important;
                border: 1px solid rgba(255, 255, 255, 0.06) !important;
                color: #e5e7eb !important;
                padding: 0.65rem 0.85rem !important;
                margin-bottom: 8px !important;
                border-radius: 10px !important;
                font-size: 0.92rem !important;
                font-weight: 500 !important;
                box-sizing: border-box !important;
                transition: all 0.2s ease-in-out;
            }
            
            section[data-testid="stSidebar"] .stButton > button p {
                color: #e5e7eb !important;
                font-size: 0.92rem !important;
                font-weight: 500 !important;
                margin: 0 !important;
                text-align: left !important;
            }

            section[data-testid="stSidebar"] .stButton > button:hover {
                background: rgba(255, 255, 255, 0.08) !important;
                color: #ffffff !important;
                border-color: rgba(255, 255, 255, 0.15) !important;
            }
            
            section[data-testid="stSidebar"] .stButton > button:hover p {
                color: #ffffff !important;
            }

            /* Active Navigation Box matching button dimensions perfectly */
            .bb-active-nav {
                background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
                color: #ffffff !important;
                border-radius: 10px !important;
                padding: 0.65rem 0.85rem !important;
                margin-bottom: 8px !important;
                font-weight: 600 !important;
                font-size: 0.92rem !important;
                box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
                display: flex;
                align-items: center;
                gap: 10px;
                border: 1px solid rgba(59, 130, 246, 0.4);
                box-sizing: border-box;
                width: 100%;
            }

            /* Logout Button Specific Styling */
            .bb-logout .stButton > button {
                color: #f87171 !important;
                background: rgba(239, 68, 68, 0.05) !important;
                border: 1px solid rgba(239, 68, 68, 0.2) !important;
                margin-top: 1rem !important;
            }
            .bb-logout .stButton > button p {
                color: #f87171 !important;
            }
            .bb-logout .stButton > button:hover {
                background: rgba(239, 68, 68, 0.15) !important;
                border-color: rgba(239, 68, 68, 0.4) !important;
            }
            .bb-logout .stButton > button:hover p {
                color: #fca5a5 !important;
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
                <h2>💰 BudgetBuddy AI</h2>
                <p>Smart Money, Smarter You</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # -- Logged-in user -------------------------------------------------
        user_name = st.session_state.get("user_name", "Guest")
        st.markdown(
            f"""
            <div class="bb-user-card">
                👋 Hello, <strong>{user_name}</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # -- Navigation -------------------------------------------------
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

        # -- Logout -------------------------------------------------
        st.markdown('<div class="bb-logout">', unsafe_allow_html=True)
        if st.button("🚪    Logout", key="nav_logout"):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.user_name = None
            st.switch_page("pages/login.py")
        st.markdown("</div>", unsafe_allow_html=True)