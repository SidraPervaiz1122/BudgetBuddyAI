# 💰 BudgetBuddy AI

**BudgetBuddy AI** is an AI-powered personal expense tracker built for university students. It helps users manage their finances, monitor spending habits, generate insightful analytics, receive AI-powered financial advice, and interact with an intelligent budgeting assistant.

🌐 **Live Demo:**  
https://budgetbuddyaigit-6kzawsvdhrdc7jo6mszwhu.streamlit.app/

📂 **GitHub Repository:**  
https://github.com/SidraPervaiz1122/BudgetBuddyAI

---

# 📌 Problem Statement

Many university students struggle to manage their monthly budgets and often lose track of where their money goes. Existing budgeting applications are either too complicated or lack intelligent guidance.

BudgetBuddy AI solves this by providing a simple expense management platform enhanced with AI that analyzes spending patterns and provides personalized budgeting recommendations.

---

# ✨ Features

## 🔐 User Authentication

- User Registration
- Secure Login
- Logout
- Forgot Password via Email OTP
- Password Reset
- Session Management

---

## 💵 Budget Management

- Add Monthly Budget
- Update Budget
- Remaining Budget Calculation
- Total Spending Calculation
- Budget Overview Cards

---

## 📝 Expense Management

- Add Expenses
- Edit Budget
- Categorize Expenses
- Transaction History
- Interactive Expense Table
- Search Expenses
- Category Filtering

---

## 📊 Analytics Dashboard

- Spending Overview
- Category-wise Expense Analysis
- Monthly Spending Insights
- Responsive Charts
- Spending Statistics
- Interactive Visualizations

---

## 🤖 AI Advisor

BudgetBuddy AI analyzes the user's actual spending history and provides personalized financial advice.

Examples:

- Spending habit analysis
- Saving recommendations
- Budget improvement suggestions
- Category-wise financial insights

---

## 💬 AI Chat Assistant

Users can freely chat with the AI assistant.

Examples:

- How can I save more money?
- Is my spending healthy?
- How should I divide my monthly budget?
- Budgeting tips
- Student financial guidance

---

## 📄 Reports

Generate professional reports containing:

- Total Spending
- Budget Summary
- Category Breakdown
- Financial Overview
- AI-generated Summary

---

## 📱 Responsive UI

The application automatically adapts to:

- Desktop
- Laptop
- Tablet
- Mobile Devices

---

# 🧠 AI Feature

BudgetBuddy AI includes two AI-powered modules:

## 1. AI Advisor

Analyzes real expense history and generates personalized budgeting advice.

## 2. AI Chat

Allows users to ask financial questions naturally.

Example:

> "How can I reduce my monthly expenses?"

The AI responds based on the user's spending history.

---

# 📝 AI System Prompt

```
You are BudgetBuddy AI.

You are an expert financial advisor for university students.

Analyze spending habits.

Identify unnecessary spending.

Suggest realistic saving strategies.

Be encouraging.

Keep responses concise.

Never recommend risky investments.

Focus on budgeting, saving money, and improving financial habits.
```

---

# 🛠 Technologies Used

## Frontend

- Streamlit
- HTML
- CSS

## Backend

- Python

## Database

- SQLite

## AI Model

- Groq LLM

## Libraries

- Pandas
- Plotly
- bcrypt
- ReportLab
- Streamlit

---

# 📂 Project Structure

```
BudgetBuddyAI/
│
├── assets/
├── components/
├── database/
├── pages/
│   ├── login.py
│   ├── signup.py
│   ├── forgot_password.py
│   ├── dashboard.py
│   ├── add_expense.py
│   ├── analytics.py
│   ├── ai_advisor.py
│   ├── ai_chat.py
│   ├── reports.py
│
├── utils/
├── app.py
├── requirements.txt
├── README.md
```

---

# 🚀 Installation

Clone the repository

```bash
git clone https://github.com/SidraPervaiz1122/BudgetBuddyAI.git
```

Move into the project

```bash
cd BudgetBuddyAI
```

Create virtual environment

```bash
python -m venv venv
```

Activate environment

Windows

```bash
venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create

```
.streamlit/secrets.toml
```

Run

```bash
streamlit run app.py
```

> **Note:** The database file (`expenses.db`) is created automatically on first run via `create_tables()` in `database/db.py` — no manual setup needed.

### Reports

![Reports](images/report.png)

---

# 🎯 Future Improvements

- Multi-currency support
- Export to Excel
- Email monthly expense reports
- Dark / Light mode
- Expense reminders
- Goal-based savings tracker
- Cloud database integration
- Multi-device synchronization

---

# 👩‍💻 Author

**Sidra Pervaiz**

BS Computer & Information Sciences

Pakistan Institute of Engineering and Applied Sciences (PIEAS)

GitHub:
https://github.com/SidraPervaiz1122

---

# 📄 License

This project is developed for educational purposes as the Final AI App Project.