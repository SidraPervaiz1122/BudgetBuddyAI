"""
navbar.py

BudgetBuddy AI - Top Header Bar
----------------------------------------
A clean, light, premium SaaS-style header shown on every page (matching
the Stripe/Linear/Vercel-inspired design direction) - page title, a
time-aware greeting, today's date, a notifications bell, and a user
avatar. The main content area stays bright and spacious; only the
Sidebar keeps the dark theme.

Usage:
    from navbar import render_navbar
    render_navbar(page_title="Dashboard", user_name="Sidra Khan", notifications_count=2)
"""

from datetime import datetime
import streamlit as st

try:
    from zoneinfo import ZoneInfo
    KARACHI_TZ = ZoneInfo("Asia/Karachi")
except Exception:
    from datetime import timezone, timedelta
    KARACHI_TZ = timezone(timedelta(hours=5))


def _get_karachi_now():
    """Returns the current datetime in Asia/Karachi (UTC+5)."""
    return datetime.now(KARACHI_TZ)


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


def _get_greeting(name):
    """
    Time-aware greeting using Asia/Karachi timezone:
    - 05:00–11:59 -> Good morning
    - 12:00–16:59 -> Good afternoon
    - 17:00–20:59 -> Good evening
    - 21:00–04:59 -> Good night
    """
    hour = _get_karachi_now().hour
    if 5 <= hour < 12:
        time_phrase = "Good morning"
    elif 12 <= hour < 17:
        time_phrase = "Good afternoon"
    elif 17 <= hour < 21:
        time_phrase = "Good evening"
    else:
        time_phrase = "Good night"
    first_name = (name or "there").strip().split(" ")[0]
    return f"{time_phrase}, {first_name} 👋"


def render_navbar(page_title="Dashboard", user_name="Guest", notifications_count=0):
    """
    Renders the top header bar.

    Args:
        page_title (str): Title of the currently active page.
        user_name (str): Name of the logged-in user (used for the greeting/avatar).
        notifications_count (int): Number of unread notifications to badge.
    """
    today_str = _get_karachi_now().strftime("%A, %d %B %Y")
    initials = _get_initials(user_name)
    greeting = _get_greeting(user_name)

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
                background: var(--bb-card, #FFFFFF);
                border: 1px solid var(--bb-border, #E2E8F0);
                border-radius: 16px;
                padding: 1.1rem 1.5rem;
                margin-bottom: 1.5rem;
                box-shadow: 0 2px 10px rgba(15, 23, 42, 0.04);
            }
            .bb-nav-left h3 {
                color: var(--bb-text, #1E293B);
                margin: 0;
                font-size: 1.3rem;
                font-weight: 700;
                letter-spacing: -0.01em;
            }
            .bb-nav-greeting {
                color: var(--bb-text-muted, #64748B);
                margin: 3px 0 0 0;
                font-size: 0.88rem;
                font-weight: 500;
            }
            .bb-nav-date {
                color: #94A3B8;
                margin: 1px 0 0 0;
                font-size: 0.76rem;
            }
            .bb-nav-right {
                display: flex;
                align-items: center;
                gap: 1.2rem;
            }
            .bb-nav-icon {
                position: relative;
                width: 40px; height: 40px;
                border-radius: 12px;
                background: var(--bb-bg-secondary, #F8FAFC);
                border: 1px solid var(--bb-border, #E2E8F0);
                display: flex; align-items: center; justify-content: center;
                font-size: 1.15rem;
                cursor: default;
                transition: background-color 0.15s ease, transform 0.15s ease;
            }
            .bb-nav-icon:hover {
                background: #EEF2FF;
                transform: translateY(-1px);
            }
            .bb-nav-badge {
                position: absolute;
                top: -4px;
                right: -4px;
                background: var(--bb-danger, #EF4444);
                color: white;
                font-size: 0.62rem;
                font-weight: 700;
                border-radius: 999px;
                padding: 1px 5px;
                border: 2px solid #FFFFFF;
            }
            .bb-nav-avatar {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background: linear-gradient(135deg, var(--bb-primary, #6366F1), var(--bb-accent, #8B5CF6));
                color: #ffffff;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
                font-size: 0.85rem;
                box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
            }

            @media (max-width: 640px) {
                .bb-navbar { flex-direction: column; align-items: flex-start; gap: 12px; padding: 1rem 1.1rem; }
                .bb-nav-right { align-self: flex-end; }
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
                <p class="bb-nav-greeting">{greeting}</p>
                <p class="bb-nav-date">📅 {today_str}</p>
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