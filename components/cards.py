"""
cards.py

BudgetBuddy AI - Dashboard Stat Cards
------------------------------------
Reusable, premium metric cards for the dashboard: Total Budget, Total
Expenses, Remaining Budget, Savings, and Number of Expenses. Each card
shows an icon, a large headline number, a small descriptive subtitle, a
colored accent border, and a subtle hover lift animation.

Usage:
    from cards import render_dashboard_cards

    render_dashboard_cards(
        total_budget=50000,
        total_expenses=32500,
        remaining_budget=17500,
        savings_percentage=35.0,
        expense_count=18,
    )
"""

import streamlit as st
from utils.helpers import format_currency

# ----------------------------------------------------------------------------
# Card theme definitions - accent color + soft icon-badge background per card
# ----------------------------------------------------------------------------

_CARD_THEMES = {
    "budget":    {"accent": "#2563eb", "badge_bg": "rgba(37, 99, 235, 0.12)"},
    "expense":   {"accent": "#dc2626", "badge_bg": "rgba(220, 38, 38, 0.12)"},
    "remaining": {"accent": "#0891b2", "badge_bg": "rgba(8, 145, 178, 0.12)"},
    "savings":   {"accent": "#16a34a", "badge_bg": "rgba(22, 163, 74, 0.12)"},
    "count":     {"accent": "#7c3aed", "badge_bg": "rgba(124, 58, 237, 0.12)"},
}


def _inject_card_styles():
    """Injects the shared CSS used by every card, once per page render."""
    st.markdown(
        """
        <style>
            .bb-card {
                background: #ffffff;
                border-radius: 18px;
                padding: 1.2rem 1.3rem;
                min-height: 128px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06);
                border: 1px solid rgba(15, 23, 42, 0.05);
                border-left: 4px solid var(--bb-accent, #2563eb);
                transition: transform 0.18s ease, box-shadow 0.18s ease;
            }
            .bb-card:hover {
                transform: translateY(-4px);
                box-shadow: 0 14px 30px rgba(15, 23, 42, 0.12);
            }
            .bb-card-icon {
                width: 38px; height: 38px;
                border-radius: 10px;
                background: var(--bb-badge-bg, rgba(37,99,235,0.12));
                display: flex; align-items: center; justify-content: center;
                font-size: 1.15rem;
            }
            .bb-card-value {
                font-size: clamp(1.15rem, 2.4vw, 1.55rem);
                font-weight: 800;
                color: #0f172a;
                margin: 0.55rem 0 0.1rem 0;
                line-height: 1.1;
                overflow-wrap: break-word;
            }
            .bb-card-subtitle {
                font-size: clamp(0.72rem, 1.4vw, 0.8rem);
                color: #64748b;
                font-weight: 500;
            }
            @media (max-width: 640px) {
                .bb-card { min-height: 108px; padding: 1rem 1.05rem; }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_card(icon, value, subtitle, theme="budget"):
    """
    Renders a single metric card.

    Args:
        icon (str): Emoji or icon representing the metric.
        value (str): The large headline value to display (pre-formatted).
        subtitle (str): A short descriptive label under the value.
        theme (str): One of "budget", "expense", "remaining", "savings",
            "count" - controls the card's accent color.
    """
    style = _CARD_THEMES.get(theme, _CARD_THEMES["budget"])

    st.markdown(
        f"""
        <div class="bb-card" style="--bb-accent:{style['accent']}; --bb-badge-bg:{style['badge_bg']};">
            <div class="bb-card-icon">{icon}</div>
            <div>
                <div class="bb-card-value">{value}</div>
                <div class="bb-card-subtitle">{subtitle}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard_cards(total_budget, total_expenses, remaining_budget, savings_percentage, expense_count=None):
    """
    Renders the core BudgetBuddy AI dashboard cards side by side: Total
    Budget, Total Expenses, Remaining Budget, and Savings. Pass
    `expense_count` to additionally show a 5th "Expenses Logged" card;
    leave it as None (default) to render exactly the 4 standard cards.

    Args:
        total_budget (float): The user's total/monthly budget.
        total_expenses (float): Total amount spent so far.
        remaining_budget (float): Budget remaining (can be negative).
        savings_percentage (float): Percentage of budget saved.
        expense_count (int | None): Optional number of expense transactions.
    """
    _inject_card_styles()

    num_cards = 5 if expense_count is not None else 4
    cols = st.columns(num_cards)

    with cols[0]:
        render_card(
            icon="💰",
            value=format_currency(total_budget),
            subtitle="Total Budget",
            theme="budget",
        )

    with cols[1]:
        render_card(
            icon="💸",
            value=format_currency(total_expenses),
            subtitle="Total Expenses",
            theme="expense",
        )

    with cols[2]:
        remaining_label = "Remaining Budget" if remaining_budget >= 0 else "Over Budget"
        render_card(
            icon="💵",
            value=format_currency(remaining_budget),
            subtitle=remaining_label,
            theme="remaining",
        )

    with cols[3]:
        render_card(
            icon="🎯",
            value=f"{savings_percentage:.1f}%",
            subtitle="Savings",
            theme="savings",
        )

    if expense_count is not None:
        with cols[4]:
            render_card(
                icon="🧾",
                value=str(expense_count),
                subtitle="Expenses Logged",
                theme="count",
            )