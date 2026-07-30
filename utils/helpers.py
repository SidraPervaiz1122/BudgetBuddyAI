"""
utils/helpers.py

BudgetBuddy AI - Helper Functions
---------------------------------
Contains formatting utilities, budget math, cached data loading, the AI
backend integration, and the password-reset email sender.
"""
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import streamlit as st
from groq import Groq

from database.db import get_user_expenses, get_user_budget

# ----------------------------------------------------------------------------
# Formatting & Math Helpers
# ----------------------------------------------------------------------------

def format_currency(amount):
    """Formats a float into a standard PKR currency string."""
    return f"Rs. {float(amount):,.2f}"

def calculate_remaining_budget(budget, expenses):
    """Calculates remaining budget, ensuring it doesn't drop below zero."""
    return max(0.0, float(budget) - float(expenses))

def calculate_savings_percentage(budget, expenses):
    """Calculates the percentage of the budget saved."""
    if float(budget) <= 0:
        return 0.0
    remaining = float(budget) - float(expenses)
    return max(0.0, (remaining / float(budget)) * 100.0)

def calculate_highest_spending_category(category_totals):
    """Returns a tuple of (Category, Amount) for the highest spending category."""
    if not category_totals:
        return None
    return max(category_totals.items(), key=lambda x: x[1])

def calculate_lowest_spending_category(category_totals):
    """Returns a tuple of (Category, Amount) for the lowest spending category."""
    if not category_totals:
        return None
    return min(category_totals.items(), key=lambda x: x[1])

def calculate_monthly_statistics(expenses):
    """Calculates count, total, average, and highest single expense from a list of expenses."""
    if not expenses:
        return {"count": 0, "total": 0.0, "average": 0.0, "highest_expense": 0.0}
    
    amounts = [float(e["amount"]) for e in expenses]
    return {
        "count": len(amounts),
        "total": sum(amounts),
        "average": sum(amounts) / len(amounts),
        "highest_expense": max(amounts)
    }

# ----------------------------------------------------------------------------
# Cached data loading
# ----------------------------------------------------------------------------
# Streamlit reruns the entire script on every widget interaction, which used
# to mean every page re-issued 4-6 separate DB queries per rerun (and the
# Sidebar issued its own on top, on every single page). These two cached
# loaders mean a page only ever hits the database once per ~30s window, no
# matter how many widgets on the page trigger reruns; everything else
# (category totals, monthly totals, daily totals, this-month filtering) is
# computed in plain Python from the already-cached list below.

@st.cache_data(ttl=30, show_spinner=False)
def load_all_expenses(user_id):
    """Cached: every expense for this user. Shared by Dashboard, Analytics, and Sidebar."""
    return get_user_expenses(user_id)


@st.cache_data(ttl=30, show_spinner=False)
def load_budget(user_id):
    """Cached: the user's current monthly budget."""
    return get_user_budget(user_id)


def clear_data_cache():
    """
    Call this right after any mutation (add/edit/delete expense, budget
    set/top-up) so the next page read reflects the change instead of
    serving stale cached data for up to 30s.
    """
    load_all_expenses.clear()
    load_budget.clear()


def filter_by_date_range(expenses, start_date=None, end_date=None):
    """Filters an already-loaded expense list by date (both inclusive, 'YYYY-MM-DD' strings)."""
    if not expenses:
        return []
    filtered = expenses
    if start_date:
        filtered = [e for e in filtered if e["date"] >= start_date]
    if end_date:
        filtered = [e for e in filtered if e["date"] <= end_date]
    return filtered


def compute_total(expenses):
    """Sums amounts for an already-loaded expense list - no DB call needed."""
    return sum(float(e["amount"]) for e in expenses) if expenses else 0.0


def compute_category_totals(expenses):
    """Groups an already-loaded expense list by category - no DB call needed."""
    totals = {}
    for e in expenses:
        totals[e["category"]] = totals.get(e["category"], 0.0) + float(e["amount"])
    return dict(sorted(totals.items(), key=lambda item: item[1], reverse=True))


def compute_monthly_totals(expenses):
    """Groups an already-loaded expense list by 'YYYY-MM' - no DB call needed."""
    totals = {}
    for e in expenses:
        month_key = e["date"][:7]
        totals[month_key] = totals.get(month_key, 0.0) + float(e["amount"])
    return dict(sorted(totals.items()))


def compute_daily_totals(expenses):
    """Groups an already-loaded expense list by exact date - no DB call needed."""
    totals = {}
    for e in expenses:
        totals[e["date"]] = totals.get(e["date"], 0.0) + float(e["amount"])
    return dict(sorted(totals.items()))


def compute_average_daily_spending(expenses):
    """Average spend per day across the full span from first to last logged expense."""
    if not expenses:
        return 0.0
    dates = sorted(set(e["date"] for e in expenses))
    if len(dates) == 1:
        return compute_total(expenses)
    first = datetime.strptime(dates[0], "%Y-%m-%d")
    last = datetime.strptime(dates[-1], "%Y-%m-%d")
    day_span = max((last - first).days + 1, 1)
    return compute_total(expenses) / day_span


def get_highest_expense(expenses):
    """Returns the single largest expense record, or None."""
    return max(expenses, key=lambda e: float(e["amount"])) if expenses else None


def get_lowest_expense(expenses):
    """Returns the single smallest expense record, or None."""
    return min(expenses, key=lambda e: float(e["amount"])) if expenses else None


# ----------------------------------------------------------------------------
# Shared Plotly chart styling
# ----------------------------------------------------------------------------

# Passed as `config=` to every st.plotly_chart call so charts feel like part
# of the app rather than an embedded plotting widget (hides the zoom/pan bar).
CHART_CONFIG = {"displayModeBar": False}

# A consistent color set used across every chart on Dashboard/Analytics.
CHART_PALETTE = ["#6366f1", "#22c55e", "#f97316", "#0891b2", "#a855f7", "#ef4444"]


def style_chart(fig, y_prefix="Rs. ", show_y_grid=True):
    """
    Applies BudgetBuddy AI's shared chart look (transparent background,
    consistent font, subtle gridlines, PKR-prefixed y-axis) to any Plotly
    figure. Call this on every chart before st.plotly_chart(..., config=CHART_CONFIG).
    """
    fig.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#334155", size=13),
        hoverlabel=dict(bgcolor="white", font_size=13),
    )
    fig.update_yaxes(
        tickprefix=y_prefix,
        showgrid=show_y_grid,
        gridcolor="rgba(148,163,184,0.25)",
        zeroline=False,
    )
    fig.update_xaxes(showgrid=False)
    return fig


# ----------------------------------------------------------------------------
# Groq AI Integration
# ----------------------------------------------------------------------------

def ask_groq(prompt, system_instruction=""):
    """
    Sends a prompt to the Groq API using the llama-3.3-70b-versatile model.
    Handles network errors, rate limits, and missing API keys securely.
    
    Returns:
        tuple: (success (bool), response_text_or_error (str), model_name (str))
    """
    api_key = st.secrets.get("GROQ_API_KEY")
    
    if not api_key:
        return False, "⚠️ Groq API key not found. Please add GROQ_API_KEY to your .streamlit/secrets.toml file.", None

    model_name = "llama-3.3-70b-versatile"

    try:
        client = Groq(api_key=api_key)
        
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.7,
        )

        if not response.choices or not response.choices[0].message.content:
            return False, "⚠️ Received an empty response from Groq AI. Please try again.", None

        return True, response.choices[0].message.content.strip(), model_name

    except Exception as e:
        # Broad catch for timeouts, rate limits, and network connection errors
        return False, f"⚠️ Groq API Error: {str(e)}", None


# ----------------------------------------------------------------------------
# Password Reset - Email Delivery
# ----------------------------------------------------------------------------

# Recipients already work for ANY email address, whatever provider a user
# signed up with - standard SMTP delivers to any domain once there's one
# working sender account. This map is what makes the SENDER side work for
# any common provider too, without you needing to know its exact SMTP
# host/port - it's auto-detected from whatever EMAIL_SENDER address you set.
_PROVIDER_SMTP_MAP = {
    "gmail.com": ("smtp.gmail.com", 587),
    "googlemail.com": ("smtp.gmail.com", 587),
    "outlook.com": ("smtp.office365.com", 587),
    "hotmail.com": ("smtp.office365.com", 587),
    "live.com": ("smtp.office365.com", 587),
    "msn.com": ("smtp.office365.com", 587),
    "yahoo.com": ("smtp.mail.yahoo.com", 587),
    "yahoo.co.uk": ("smtp.mail.yahoo.com", 587),
    "icloud.com": ("smtp.mail.me.com", 587),
    "me.com": ("smtp.mail.me.com", 587),
    "mac.com": ("smtp.mail.me.com", 587),
    "zoho.com": ("smtp.zoho.com", 587),
}


def _detect_smtp_settings(sender_email):
    """
    Guesses the right SMTP host/port from the sender's own email domain
    (e.g. someone@outlook.com -> Office365's SMTP server) so BudgetBuddy AI
    isn't locked to Gmail-only sending. Falls back to Gmail's settings for
    any provider not in the map - override with SMTP_HOST/SMTP_PORT in
    secrets.toml if that fallback doesn't fit your provider.
    """
    domain = sender_email.split("@")[-1].strip().lower()
    return _PROVIDER_SMTP_MAP.get(domain, ("smtp.gmail.com", 587))

def send_reset_code_email(to_email, user_name, code):
    """
    Sends a styled password-reset code email via SMTP. Works for ANY
    recipient's email address regardless of provider (Gmail, Yahoo,
    Outlook, a university address, anything) - that's just how SMTP
    delivery works once there's one sender account configured.

    Reads sender credentials from .streamlit/secrets.toml, e.g.:

        EMAIL_SENDER = "your-app-email@gmail.com"
        EMAIL_PASSWORD = "your-16-char-app-password"

    SMTP_HOST/SMTP_PORT are optional - they're auto-detected from
    EMAIL_SENDER's own domain (Gmail, Outlook/Hotmail, Yahoo, iCloud, Zoho
    all work out of the box). Only set SMTP_HOST/SMTP_PORT explicitly if
    you're using a provider not in that list, or a custom/company SMTP
    relay:

        SMTP_HOST = "smtp.yourcompany.com"
        SMTP_PORT = 587

    (Most providers require an app-specific password rather than your
    normal account password - e.g. Gmail's "App Passwords" - since they
    block regular passwords for third-party SMTP logins.)

    Args:
        to_email (str): Recipient's email address.
        user_name (str): Recipient's display name (for personalization).
        code (str): The 6-digit reset code to include.

    Returns:
        tuple: (success (bool), message (str))
    """
    sender_email = st.secrets.get("EMAIL_SENDER")
    sender_password = st.secrets.get("EMAIL_PASSWORD")

    if not sender_email or not sender_password:
        return False, "⚠️ Email is not configured. Add EMAIL_SENDER and EMAIL_PASSWORD to your .streamlit/secrets.toml file."

    detected_host, detected_port = _detect_smtp_settings(sender_email)
    smtp_host = st.secrets.get("SMTP_HOST", detected_host)
    smtp_port = st.secrets.get("SMTP_PORT", detected_port)

    subject = "BudgetBuddy AI - Password Reset Code"

    plain_body = (
        "Hello,\n\n"
        "We received a request to reset your BudgetBuddy AI password.\n\n"
        "Your verification code is:\n\n"
        f"{code}\n\n"
        "This code expires in 10 minutes.\n\n"
        "If you did not request this, you can safely ignore this email.\n\n"
        "BudgetBuddy AI Team"
    )

    html_body = f"""
    <div style="font-family: Inter, Arial, sans-serif; max-width: 480px; margin: auto;
                background:#0a0e1a; padding: 32px; border-radius: 16px; color:#f1f5f9;">
        <h2 style="color:#f8fafc; margin-bottom: 4px;">💰 BudgetBuddy AI</h2>
        <p style="color:#94a3b8; margin-top:0;">Password Reset Code</p>
        <p>Hello,</p>
        <p>We received a request to reset your BudgetBuddy AI password.</p>
        <p>Your verification code is:</p>
        <div style="text-align:center; margin: 28px 0;">
            <span style="display:inline-block; padding: 14px 28px; font-size: 28px;
                         font-weight: 700; letter-spacing: 8px; color:#ffffff;
                         background: linear-gradient(90deg,#6366f1,#8b5cf6); border-radius: 12px;">
                {code}
            </span>
        </div>
        <p>This code expires in 10 minutes.</p>
        <p style="color:#94a3b8; font-size: 0.85rem;">
            If you did not request this, you can safely ignore this email.
        </p>
        <p style="color:#94a3b8; margin-top: 24px;">BudgetBuddy AI Team</p>
    </div>
    """

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = to_email
    message.attach(MIMEText(plain_body, "plain"))
    message.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(smtp_host, int(smtp_port)) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, message.as_string())
        return True, "Email sent."

    except smtplib.SMTPAuthenticationError:
        return False, "SMTP authentication failed. Check EMAIL_SENDER/EMAIL_PASSWORD in secrets.toml."
    except Exception as e:
        return False, f"Could not send email: {e}"