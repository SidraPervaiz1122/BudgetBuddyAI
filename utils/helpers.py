"""
utils/helpers.py

BudgetBuddy AI - Helper Functions
---------------------------------
Contains formatting utilities, budget math, and the AI backend integration.
"""
import streamlit as st
from groq import Groq

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