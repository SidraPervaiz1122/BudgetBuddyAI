"""
cards.py

BudgetBuddy AI - Dashboard Cards
------------------------------------
Reusable, styled metric cards for the dashboard: Total Budget, Total
Expenses, Remaining Budget, and Savings. Each card shows an icon, a
large headline number, and a small descriptive subtitle.

Usage:
    from cards import render_dashboard_cards

    render_dashboard_cards(
        total_budget=50000,
        total_expenses=32500,
        remaining_budget=17500,
        savings_percentage=35.0,
    )
"""

import streamlit as st
from utils.helpers import format_currency

# ----------------------------------------------------------------------------
# Card style definitions
# ----------------------------------------------------------------------------

_CARD_THEMES = {
    "budget": {"gradient": "linear-gradient(135deg, #2563eb, #3b82f6)", "glow": "rgba(37, 99, 235, 0.35)"},
    "expense": {"gradient": "linear-gradient(135deg, #dc2626, #f87171)", "glow": "rgba(220, 38, 38, 0.35)"},
    "remaining": {"gradient": "linear-gradient(135deg, #0891b2, #22d3ee)", "glow": "rgba(8, 145, 178, 0.35)"},
    "savings": {"gradient": "linear-gradient(135deg, #16a34a, #4ade80)", "glow": "rgba(22, 163, 74, 0.35)"},
}


def _inject_card_styles():
    """Injects the shared CSS used by every card, once per page render."""
    st.markdown(
        """
        <style>
            .bb-card {
                border-radius: 16px;
                padding: 1.25rem 1.4rem;
                color: #ffffff;
                min-height: 130px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
                transition: transform 0.15s ease-in-out;
            }
            .bb-card:hover {
                transform: translateY(-3px);
            }
            .bb-card-icon {
                font-size: 1.6rem;
                opacity: 0.9;
            }
            .bb-card-value {
                font-size: 1.9rem;
                font-weight: 700;
                margin: 0.35rem 0 0.1rem 0;
                line-height: 1.1;
            }
            .bb-card-subtitle {
                font-size: 0.8rem;
                opacity: 0.85;
                font-weight: 400;
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
        theme (str): One of "budget", "expense", "remaining", "savings" -
            controls the card's gradient color scheme.
    """
    style = _CARD_THEMES.get(theme, _CARD_THEMES["budget"])

    st.markdown(
        f"""
        <div class="bb-card" style="background:{style['gradient']};
             box-shadow: 0 10px 25px {style['glow']};">
            <div class="bb-card-icon">{icon}</div>
            <div>
                <div class="bb-card-value">{value}</div>
                <div class="bb-card-subtitle">{subtitle}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard_cards(total_budget, total_expenses, remaining_budget, savings_percentage):
    """
    Renders the four core BudgetBuddy AI dashboard cards side by side:
    Total Budget, Total Expenses, Remaining Budget, and Savings.

    Args:
        total_budget (float): The user's total/monthly budget.
        total_expenses (float): Total amount spent so far.
        remaining_budget (float): Budget remaining (can be negative).
        savings_percentage (float): Percentage of budget saved.
    """
    _inject_card_styles()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_card(
            icon="💰",
            value=format_currency(total_budget),
            subtitle="Total Budget",
            theme="budget",
        )

    with col2:
        render_card(
            icon="💸",
            value=format_currency(total_expenses),
            subtitle="Total Expenses",
            theme="expense",
        )

    with col3:
        remaining_label = "Remaining Budget" if remaining_budget >= 0 else "Over Budget"
        render_card(
            icon="💵",
            value=format_currency(remaining_budget),
            subtitle=remaining_label,
            theme="remaining",
        )

    with col4:
        render_card(
            icon="🎯",
            value=f"{savings_percentage:.1f}%",
            subtitle="Savings",
            theme="savings",
        )