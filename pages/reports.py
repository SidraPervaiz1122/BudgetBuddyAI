"""
pages/reports.py

BudgetBuddy AI - Monthly Reports
-------------------------------------
Generates a monthly spending report (total expenses, highest/lowest
category, a written summary, and an optional AI-generated summary via
Gemini) and lets the user download it as a formatted PDF using ReportLab.
"""

import io
from datetime import date, datetime
import calendar

import streamlit as st

from database.db import get_user_expenses, get_category_totals, get_total_expense, get_user_budget
from utils.helpers import (
    format_currency,
    calculate_monthly_statistics,
    calculate_highest_spending_category,
    calculate_lowest_spending_category,
    ask_groq,
    calculate_remaining_budget,
)
from components.sidebar import render_sidebar
from components.navbar import render_navbar

# ----------------------------------------------------------------------------
# Optional dependency: ReportLab
# ----------------------------------------------------------------------------

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# ----------------------------------------------------------------------------
# Page configuration & auth guard
# ----------------------------------------------------------------------------

st.set_page_config(page_title="Reports | BudgetBuddy AI", page_icon="📄", layout="wide")

if not st.session_state.get("logged_in"):
    st.warning("⚠️ Please log in to view your reports.")
    st.switch_page("pages/login.py")
    st.stop()

user_id = st.session_state["user_id"]
user_name = st.session_state.get("user_name", "there")

# ----------------------------------------------------------------------------
# Layout shell
# ----------------------------------------------------------------------------

render_sidebar(active_page="Reports")
render_navbar(page_title="Reports", user_name=user_name)

st.markdown("### 📄 Monthly Report")
st.caption("Generate a clean, shareable summary of a month's spending.")

# ----------------------------------------------------------------------------
# Month selection
# ----------------------------------------------------------------------------

today = date.today()
years = list(range(today.year - 3, today.year + 1))

col_y, col_m = st.columns(2)
with col_y:
    selected_year = st.selectbox("📅 Year", options=years, index=len(years) - 1)
with col_m:
    month_names = list(calendar.month_name)[1:]
    selected_month_name = st.selectbox("🗓️ Month", options=month_names, index=today.month - 1)
    selected_month = month_names.index(selected_month_name) + 1

start_date = date(selected_year, selected_month, 1)
last_day = calendar.monthrange(selected_year, selected_month)[1]
end_date = date(selected_year, selected_month, last_day)

start_str = start_date.strftime("%Y-%m-%d")
end_str = end_date.strftime("%Y-%m-%d")

# ----------------------------------------------------------------------------
# Pull live data for the selected month
# ----------------------------------------------------------------------------

monthly_budget = get_user_budget(user_id)
month_expenses = get_user_expenses(user_id, start_date=start_str, end_date=end_str)
category_totals = get_category_totals(user_id, start_date=start_str, end_date=end_str)
total_spent = get_total_expense(user_id, start_date=start_str, end_date=end_str)
stats = calculate_monthly_statistics(month_expenses)
remaining_budget = calculate_remaining_budget(monthly_budget, total_spent)

if not month_expenses:
    st.info(f"📭 No expenses recorded for {selected_month_name} {selected_year}.")
    st.stop()

highest_result = calculate_highest_spending_category(category_totals)
lowest_result = calculate_lowest_spending_category(category_totals)
highest_category = highest_result[0] if highest_result else None
lowest_category = lowest_result[0] if lowest_result else None

# ----------------------------------------------------------------------------
# On-screen summary
# ----------------------------------------------------------------------------

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("💸 Total Expenses", format_currency(total_spent))
with c2:
    st.metric("📈 Highest Category", highest_category or "N/A")
with c3:
    st.metric("📉 Lowest Category", lowest_category or "N/A")
with c4:
    st.metric("🔢 Transactions", stats["count"])

summary_text = (
    f"In {selected_month_name} {selected_year}, you logged {stats['count']} transactions "
    f"totaling {format_currency(total_spent)}. Your average expense was {format_currency(stats['average'])}, "
    f"and your single highest expense was {format_currency(stats['highest_expense'])}. "
    f"{highest_category or 'No category'} was your biggest spending area"
    + (f", while {lowest_category} saw the least spending." if lowest_category and lowest_category != highest_category else ".")
)

st.markdown("#### 📝 Monthly Summary")
st.write(summary_text)

st.markdown("#### 🗂️ Category Breakdown")
if category_totals:
    import pandas as pd
    breakdown_df = pd.DataFrame(
        {"Category": list(category_totals.keys()), "Total Spent": list(category_totals.values())}
    ).sort_values("Total Spent", ascending=False)
    breakdown_df["Total Spent"] = breakdown_df["Total Spent"].apply(format_currency)
    st.dataframe(breakdown_df, use_container_width=True, hide_index=True)


# ----------------------------------------------------------------------------
# Optional AI-generated summary (Gemini)
# ----------------------------------------------------------------------------

REPORT_SYSTEM_PROMPT = (
    "You are BudgetBuddy AI, a friendly budgeting assistant for university students. "
    "Focus only on budgeting, never mention investing, and keep it under 100 words."
)


def _build_report_prompt(month_label, total_spent, category_totals, stats, monthly_budget, remaining_budget):
    category_lines = "\n".join(f"- {c}: {format_currency(a)}" for c, a in category_totals.items())
    return (
        f"Month: {month_label}\n"
        f"Monthly budget: {format_currency(monthly_budget)}\n"
        f"Total spent: {format_currency(total_spent)}\n"
        f"Remaining budget: {format_currency(remaining_budget)}\n"
        f"Average expense: {format_currency(stats['average'])}\n"
        f"Category breakdown:\n{category_lines}\n\n"
        "Write a short, encouraging 3-4 sentence summary of this student's spending for a monthly report."
    )


st.markdown("#### 🤖 AI Summary")
if st.button("✨ Generate AI Summary"):
    with st.spinner("🤔 BudgetBuddy AI is summarizing your month..."):
        prompt = _build_report_prompt(
            f"{selected_month_name} {selected_year}", 
            total_spent, 
            category_totals, 
            stats,
            monthly_budget,
            remaining_budget
        )
        success, result, model_used = ask_groq(
            prompt=prompt, system_instruction=REPORT_SYSTEM_PROMPT
        )

    if success:
        st.session_state["report_ai_summary"] = result
        st.session_state["report_ai_summary_model"] = model_used
    else:
        st.session_state["report_ai_summary"] = None
        st.session_state["report_ai_summary_model"] = None
        st.warning(f"⚠️ {result} The rest of your report is unaffected.")

ai_summary = st.session_state.get("report_ai_summary")
ai_summary_model = st.session_state.get("report_ai_summary_model")
if ai_summary:
    st.info(ai_summary)
    if ai_summary_model:
        st.caption(f"🔧 Generated using Gemini model: `{ai_summary_model}`")

st.divider()


# ----------------------------------------------------------------------------
# PDF generation (ReportLab)
# ----------------------------------------------------------------------------

if not REPORTLAB_AVAILABLE:
    st.error(
        "📄 PDF download isn't available right now because the `reportlab` package "
        "isn't installed. Run `pip install reportlab` (it's already listed in "
        "`requirements.txt`) and restart the app to enable PDF reports."
    )
    st.stop()


def build_pdf_report(month_label, user_name, total_spent, highest_category, lowest_category,
                      summary_text, category_totals, stats, monthly_budget, remaining_budget, ai_summary=None):
    """
    Builds a formatted PDF report in memory using ReportLab.

    Returns:
        bytes: The generated PDF file content.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=2 * cm, bottomMargin=2 * cm, leftMargin=2 * cm, rightMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "BBTitle", parent=styles["Title"], textColor=colors.HexColor("#1e293b"), fontSize=22,
    )
    heading_style = ParagraphStyle(
        "BBHeading", parent=styles["Heading2"], textColor=colors.HexColor("#2563eb"), spaceBefore=14, spaceAfter=6,
    )
    body_style = ParagraphStyle("BBBody", parent=styles["BodyText"], leading=16)

    elements = []

    elements.append(Paragraph("💰 BudgetBuddy AI - Monthly Report", title_style))
    elements.append(Paragraph(f"{month_label} | Prepared for {user_name}", styles["Normal"]))
    elements.append(Spacer(1, 0.6 * cm))

    elements.append(Paragraph("Overview", heading_style))
    overview_data = [
        ["Monthly Budget", format_currency(monthly_budget)],
        ["Total Expenses", format_currency(total_spent)],
        ["Remaining Budget", format_currency(remaining_budget)],
        ["Highest Spending Category", highest_category or "N/A"],
        ["Lowest Spending Category", lowest_category or "N/A"],
        ["Total Transactions", str(stats["count"])],
        ["Average Expense", format_currency(stats["average"])],
    ]
    overview_table = Table(overview_data, colWidths=[8 * cm, 8 * cm])
    overview_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eff6ff")),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#1e293b")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ])
    )
    elements.append(overview_table)

    elements.append(Paragraph("Monthly Summary", heading_style))
    elements.append(Paragraph(summary_text, body_style))

    if category_totals:
        elements.append(Paragraph("Category Breakdown", heading_style))
        cat_data = [["Category", "Amount"]] + [
            [cat, format_currency(amt)] for cat, amt in
            sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
        ]
        cat_table = Table(cat_data, colWidths=[8 * cm, 8 * cm])
        cat_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ])
        )
        elements.append(cat_table)

    if ai_summary:
        elements.append(Paragraph("AI Summary", heading_style))
        elements.append(Paragraph(ai_summary, body_style))

    elements.append(Spacer(1, 0.8 * cm))
    elements.append(
        Paragraph(
            f"Generated by BudgetBuddy AI on {datetime.now().strftime('%d %B %Y, %H:%M')}",
            ParagraphStyle("Footer", parent=styles["Normal"], textColor=colors.grey, fontSize=8),
        )
    )

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


month_label = f"{selected_month_name} {selected_year}"
pdf_bytes = build_pdf_report(
    month_label=month_label,
    user_name=user_name,
    total_spent=total_spent,
    highest_category=highest_category,
    lowest_category=lowest_category,
    summary_text=summary_text,
    category_totals=category_totals,
    stats=stats,
    monthly_budget=monthly_budget,
    remaining_budget=remaining_budget,
    ai_summary=ai_summary,
)

st.download_button(
    label="⬇️ Download PDF Report",
    data=pdf_bytes,
    file_name=f"BudgetBuddy_Report_{selected_year}_{selected_month:02d}.pdf",
    mime="application/pdf",
    use_container_width=True,
)