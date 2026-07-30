# 💰 BudgetBuddy AI

**BudgetBuddy AI** is an intelligent personal finance management application built using **Streamlit**, **SQLite**, and **Groq AI**. It helps students track their expenses, manage their monthly budget, analyze their spending habits, and receive personalized financial advice through an AI-powered assistant.

---

# 📌 Problem Statement

Many university students struggle to manage their monthly expenses. They often lose track of where their money is spent, making it difficult to save or stay within budget.

BudgetBuddy AI solves this problem by providing an easy-to-use platform where students can:

* Manage their monthly budget
* Record daily expenses
* Analyze spending habits
* View insightful reports
* Receive personalized AI financial guidance

---

# 🎯 Target Users

* University Students
* Hostel Students
* Fresh Graduates
* Anyone who wants a simple personal expense manager

---

# 🚀 Live Demo

🔗 **Live App:**
https://budgetbuddyaigit-6kzawsvdhrdc7jo6mszwhu.streamlit.app/


---

# 💻 GitHub Repository

🔗 **GitHub Repository:**
https://github.com/SidraPervaiz1122/BudgetBuddyAI

---

# ✨ Features

## 👤 User Authentication

* Secure Signup
* Secure Login
* User-specific data
* Session Management

---

## 💰 Budget Management

* Set Monthly Budget
* Update Budget
* Add Money to Existing Budget
* Remaining Budget Calculation
* Budget Persistence using SQLite

---

## 💸 Expense Management

Users can

* Add Expenses
* Edit Expenses
* Delete Expenses
* Categorize Expenses
* Add Description
* Store Date

Categories include:

* Food
* Transport
* Shopping
* Education
* Entertainment
* Bills
* Healthcare
* Others

---

## 📊 Dashboard

Interactive dashboard showing:

* Monthly Budget
* Total Expenses
* Remaining Budget
* Savings Percentage
* Recent Transactions

---

## 📈 Analytics

Visual insights including:

* Spending by Category
* Monthly Expense Distribution
* Expense Trends
* Financial Summary

---

## 🤖 AI Chat Assistant

BudgetBuddy AI includes a conversational AI assistant powered by **Groq**.

The AI can answer questions such as:

* How can I save more money?
* Where am I overspending?
* Analyze my expenses.
* Suggest a better monthly budget.
* Give me financial tips.

The AI uses the logged-in user's actual spending data to generate personalized responses.

---

## 🧠 AI Financial Advisor

The AI Advisor analyzes:

* Monthly Budget
* Remaining Budget
* Spending Categories
* Recent Expenses
* Total Spending

Then generates personalized financial recommendations to help users improve their budgeting habits.

---

## 📄 Smart Reports

Generate financial reports containing:

* Budget Summary
* Expense Summary
* Spending Categories
* AI Generated Financial Insights

Reports can also be exported.

---

## 💾 Persistent Database

The application stores:

* User Accounts
* Monthly Budgets
* Expenses
* Categories
* AI Context

using **SQLite**.

Data remains available after logout and login.

---

# 🛠 Technologies Used

## Frontend

* Streamlit
* HTML
* CSS

---

## Backend

* Python

---

## Database

* SQLite

---

## AI

* Groq API
* Llama 3.3 70B Versatile

---

## Libraries

* Streamlit
* SQLite3
* Pandas
* Plotly
* bcrypt
* ReportLab
* Groq

---

# 🧠 AI Feature

BudgetBuddy AI includes an intelligent financial assistant powered by **Groq**.

The assistant receives:

* User Budget
* Remaining Budget
* Spending Categories
* Recent Expenses
* Total Spending

and generates personalized financial guidance.

### System Prompt

```
You are BudgetBuddy AI.

You are an expert financial advisor for university students.

Analyze the user's spending habits.

Identify unnecessary expenses.

Suggest realistic saving strategies.

Be friendly, supportive, and practical.

Never recommend risky investments.

Keep responses concise and personalized using the user's financial data.
```

---

# 📂 Project Structure

```
BudgetBuddyAI/

│
├── app.py
│
├── components/
│   ├── sidebar.py
│   ├── navbar.py
│   └── cards.py
│
├── pages/
│   ├── login.py
│   ├── signup.py
│   ├── dashboard.py
│   ├── add_expense.py
│   ├── analytics.py
│   ├── ai_advisor.py
│   ├── ai_chat.py
│   └── reports.py
│
├── database/
│   └── db.py
│
├── utils/
│   └── helpers.py
│
├── assets/
│
├── .streamlit/
│   └── secrets.toml
│
├── requirements.txt
│
└── README.md
```

---

# 📸 Screenshots

Add at least three screenshots.

### Login Page

```
images/login.png
```

### Dashboard

```
images/dashboard.png
```

### Analytics

```
images/analytics.png
```

### AI Advisor

```
images/ai_advisor.png
```

### AI Chat

```
images/ai_chat.png
```

### Reports

```
images/report.png
```

---

# ⚙ Installation

Clone the repository

```bash
git clone <https://github.com/SidraPervaiz1122/BudgetBuddyAI>
```

Move inside the project

```bash
cd BudgetBuddyAI
```

Create a virtual environment

```bash
python -m venv venv
```

Activate the virtual environment

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

Add your Groq API key

```
GROQ_API_KEY="YOUR_API_KEY"
```

Run the application

```bash
streamlit run app.py
```

---

# 📖 Future Improvements

* Dark/Light Theme Toggle
* Budget Notifications
* Monthly Saving Goals
* Email Reports
* Receipt OCR
* Multi-Currency Support
* Cloud Database Integration
* Mobile Application

---

# 👩‍💻 Developed By

**Sidra Pervaiz**

BS Computer and Information Sciences

Pakistan Institute of Engineering and Applied Sciences (PIEAS)

---

# 📜 License

This project was developed for educational purposes as a university final project.

© 2026 BudgetBuddy AI. All rights reserved.
