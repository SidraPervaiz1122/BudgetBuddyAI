"""
navbar.py

BudgetBuddy AI - Top Navigation Bar
----------------------------------------
A clean, dark, modern top bar shown on every page. Displays the current
page title, today's date, a user avatar (initials-based), and a
notifications icon with an optional unread-count badge.

Usage:
    from navbar import render_navbar
    render_navbar(page_title="Dashboard", user_name="Sidra Khan", notifications_count=2)
"""

from datetime import datetime
import streamlit as st


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


def render_navbar(page_title="Dashboard", user_name="Guest", notifications_count=0):
    """
    Renders the top navigation bar.

    Args:
        page_title (str): Title of the currently active page.
        user_name (str): Name of the logged-in user (used for the avatar).
        notifications_count (int): Number of unread notifications to badge.
    """
    today_str = datetime.now().strftime("%A, %d %B %Y")
    initials = _get_initials(user_name)

    badge_html = ""
    if notifications_count and notifications_count > 0:
        badge_html = f'<span class="bb-nav-badge">{notifications_count}</span>'

    st.markdown(
        """
        <style>
            .bb-navbar {
                display: flex;
                align-items: center;
                justify-content: space-between;
                background: #111827;
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 14px;
                padding: 0.9rem 1.4rem;
                margin-bottom: 1.4rem;
                box-shadow: 0 6px 18px rgba(0, 0, 0, 0.25);
            }
            .bb-nav-left h3 {
                color: #ffffff;
                margin: 0;
                font-size: 1.25rem;
                font-weight: 700;
            }
            .bb-nav-left p {
                color: #9ca3af;
                margin: 2px 0 0 0;
                font-size: 0.8rem;
            }
            .bb-nav-right {
                display: flex;
                align-items: center;
                gap: 1.1rem;
            }
            .bb-nav-icon {
                position: relative;
                font-size: 1.3rem;
                color: #e5e7eb;
                cursor: default;
            }
            .bb-nav-badge {
                position: absolute;
                top: -6px;
                right: -10px;
                background: #ef4444;
                color: white;
                font-size: 0.65rem;
                font-weight: 700;
                border-radius: 999px;
                padding: 1px 6px;
            }
            .bb-nav-avatar {
                width: 38px;
                height: 38px;
                border-radius: 50%;
                background: linear-gradient(135deg, #2563eb, #7c3aed);
                color: #ffffff;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
                font-size: 0.85rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="bb-navbar">
            <div class="bb-nav-left">
                <h3>{page_title}</h3>
                <p>📅 {today_str}</p>
            </div>
            <div class="bb-nav-right">
                <div class="bb-nav-icon">
                    🔔{badge_html}
                </div>
                <div class="bb-nav-avatar">{initials}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )