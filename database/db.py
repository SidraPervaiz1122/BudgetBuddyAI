"""
database/db.py

BudgetBuddy AI - Database Layer
---------------------------------
This module manages all interactions with the SQLite database (expenses.db),
including schema creation/migration, user authentication (with bcrypt
password hashing), and full CRUD operations for expenses.
"""

import os
import sqlite3
import bcrypt
from datetime import datetime
from contextlib import contextmanager

# ----------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_NAME = os.path.join(_PROJECT_ROOT, "expenses.db")

_EXPECTED_SCHEMA = {
    "users": {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "name": "TEXT NOT NULL DEFAULT ''",
        "email": "TEXT NOT NULL DEFAULT ''",
        "password": "TEXT NOT NULL DEFAULT ''",
        "monthly_budget": "REAL NOT NULL DEFAULT 0",
    },
    "expenses": {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "user_id": "INTEGER NOT NULL DEFAULT 0",
        "amount": "REAL NOT NULL DEFAULT 0",
        "category": "TEXT NOT NULL DEFAULT 'Other'",
        "description": "TEXT",
        "date": "TEXT NOT NULL DEFAULT ''",
        "created_at": "TEXT NOT NULL DEFAULT ''",
    },
}


# ----------------------------------------------------------------------------
# Connection helper
# ----------------------------------------------------------------------------

@contextmanager
def get_connection():
    """
    Context manager that yields a SQLite connection with foreign keys enabled
    and row access by column name. Ensures the connection is always closed.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


# ----------------------------------------------------------------------------
# Schema creation & automatic migration
# ----------------------------------------------------------------------------

def _table_exists(conn, table_name):
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name = ?", (table_name,)
    )
    return cursor.fetchone() is not None


def _existing_columns(conn, table_name):
    cursor = conn.execute(f"PRAGMA table_info({table_name})")
    return {row[1] for row in cursor.fetchall()}


def _migrate_schema(conn):
    for table_name, expected_columns in _EXPECTED_SCHEMA.items():
        if not _table_exists(conn, table_name):
            continue

        current_columns = _existing_columns(conn, table_name)

        for column_name, column_def in expected_columns.items():
            if column_name in current_columns:
                continue
            if "PRIMARY KEY" in column_def:
                continue

            try:
                conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}")
            except sqlite3.Error as e:
                print(f"[DB MIGRATION ERROR] Could not add '{column_name}' to '{table_name}': {e}")


def create_tables():
    try:
        with get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    monthly_budget REAL NOT NULL DEFAULT 0
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT,
                    date TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            """)

            conn.commit()
            _migrate_schema(conn)
            conn.commit()
            return True

    except sqlite3.Error as e:
        print(f"[DB ERROR] Failed to create/migrate tables: {e}")
        return False


# ----------------------------------------------------------------------------
# User authentication
# ----------------------------------------------------------------------------

def register_user(name, email, password):
    if not name or not email or not password:
        return False, "All fields are required."

    try:
        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name.strip(), email.strip().lower(), hashed_pw.decode("utf-8")),
            )
            conn.commit()
            return True, "Account created successfully."

    except sqlite3.IntegrityError:
        return False, "An account with this email already exists."
    except sqlite3.Error as e:
        return False, f"Database error during registration: {e}"


def login_user(email, password):
    if not email or not password:
        return False, "Email and password are required.", None

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, name, email, password, monthly_budget FROM users WHERE email = ?",
                (email.strip().lower(),),
            )
            row = cursor.fetchone()

            if row is None:
                return False, "No account found with this email.", None

            stored_hash = row["password"].encode("utf-8")
            try:
                password_matches = bcrypt.checkpw(password.encode("utf-8"), stored_hash)
            except ValueError:
                return False, "Incorrect password.", None

            if password_matches:
                user_data = {
                    "id": row["id"],
                    "name": row["name"],
                    "email": row["email"],
                    "monthly_budget": float(row["monthly_budget"] or 0.0),
                }
                return True, "Login successful.", user_data
            else:
                return False, "Incorrect password.", None

    except sqlite3.Error as e:
        return False, f"Database error during login: {e}", None


# ----------------------------------------------------------------------------
# Budget Operations
# ----------------------------------------------------------------------------

def get_user_budget(user_id):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT monthly_budget FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return float(row["monthly_budget"]) if row and row["monthly_budget"] is not None else 0.0

    except sqlite3.Error as e:
        print(f"[DB ERROR] Failed to fetch budget for user {user_id}: {e}")
        return 0.0


def set_user_budget(user_id, budget):
    try:
        budget = float(budget)
        if budget < 0:
            return False, "Budget cannot be negative."
    except (ValueError, TypeError):
        return False, "Invalid budget amount."

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET monthly_budget = ? WHERE id = ?", (budget, user_id)
            )
            conn.commit()

            if cursor.rowcount == 0:
                return False, "User not found."
            return True, "Budget updated successfully."

    except sqlite3.Error as e:
        return False, f"Database error while updating budget: {e}"


def add_to_user_budget(user_id, amount):
    """
    Adds a positive monetary amount to the user's existing monthly budget
    using the established set_user_budget function.
    """
    current_budget = get_user_budget(user_id) or 0.0
    new_budget = float(current_budget) + float(amount)
    success, message = set_user_budget(user_id, new_budget)
    if not success:
        raise sqlite3.OperationalError(message)
    return new_budget


# ----------------------------------------------------------------------------
# Expense CRUD operations
# ----------------------------------------------------------------------------

def add_expense(user_id, amount, category, description, date):
    if not user_id:
        return False, "You must be logged in to add an expense."

    try:
        if amount is None or float(amount) <= 0:
            return False, "Amount must be greater than zero."

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO expenses (user_id, amount, category, description, date, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (user_id, float(amount), category, description, date, created_at),
            )
            conn.commit()
            return True, "Expense added successfully."

    except (ValueError, TypeError):
        return False, "Invalid amount provided."
    except sqlite3.Error as e:
        return False, f"Database error while adding expense: {e}"


def get_expense_by_id(expense_id, user_id=None):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            if user_id is not None:
                cursor.execute(
                    "SELECT * FROM expenses WHERE id = ? AND user_id = ?", (expense_id, user_id)
                )
            else:
                cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    except sqlite3.Error as e:
        print(f"[DB ERROR] Failed to fetch expense {expense_id}: {e}")
        return None


def update_expense(expense_id, amount=None, category=None, description=None, date=None, user_id=None):
    fields = []
    values = []

    if amount is not None:
        try:
            if float(amount) <= 0:
                return False, "Amount must be greater than zero."
            fields.append("amount = ?")
            values.append(float(amount))
        except (ValueError, TypeError):
            return False, "Invalid amount provided."

    if category is not None:
        fields.append("category = ?")
        values.append(category)

    if description is not None:
        fields.append("description = ?")
        values.append(description)

    if date is not None:
        fields.append("date = ?")
        values.append(date)

    if not fields:
        return False, "No fields provided to update."

    values.append(expense_id)

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            query = f"UPDATE expenses SET {', '.join(fields)} WHERE id = ?"
            if user_id is not None:
                query += " AND user_id = ?"
                values.append(user_id)

            cursor.execute(query, values)
            conn.commit()

            if cursor.rowcount == 0:
                return False, "Expense not found."
            return True, "Expense updated successfully."

    except sqlite3.Error as e:
        return False, f"Database error while updating expense: {e}"


def delete_expense(expense_id, user_id=None):
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            if user_id is not None:
                cursor.execute(
                    "DELETE FROM expenses WHERE id = ? AND user_id = ?",
                    (expense_id, user_id),
                )
            else:
                cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            conn.commit()

            if cursor.rowcount == 0:
                return False, "Expense not found or already deleted."
            return True, "Expense deleted successfully."

    except sqlite3.Error as e:
        return False, f"Database error while deleting expense: {e}"


# ----------------------------------------------------------------------------
# Expense retrieval / analytics
# ----------------------------------------------------------------------------

def get_user_expenses(user_id, category=None, start_date=None, end_date=None, search=None):
    try:
        query = "SELECT * FROM expenses WHERE user_id = ?"
        params = [user_id]

        if category and category.lower() != "all":
            query += " AND category = ?"
            params.append(category)

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)

        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        if search:
            query += " AND LOWER(description) LIKE ?"
            params.append(f"%{search.strip().lower()}%")

        query += " ORDER BY date DESC, created_at DESC"

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    except sqlite3.Error as e:
        print(f"[DB ERROR] Failed to fetch user expenses: {e}")
        return []


def get_total_expense(user_id, start_date=None, end_date=None):
    try:
        query = "SELECT SUM(amount) AS total FROM expenses WHERE user_id = ?"
        params = [user_id]

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)

        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            return float(row["total"]) if row and row["total"] is not None else 0.0

    except sqlite3.Error as e:
        print(f"[DB ERROR] Failed to calculate total expense: {e}")
        return 0.0


def get_category_totals(user_id, start_date=None, end_date=None):
    try:
        query = """
            SELECT category, SUM(amount) AS total
            FROM expenses
            WHERE user_id = ?
        """
        params = [user_id]

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)

        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        query += " GROUP BY category ORDER BY total DESC"

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return {row["category"]: float(row["total"]) for row in rows}

    except sqlite3.Error as e:
        print(f"[DB ERROR] Failed to calculate category totals: {e}")
        return {}


def get_monthly_expenses(user_id, year=None):
    try:
        query = """
            SELECT strftime('%Y-%m', date) AS month, SUM(amount) AS total
            FROM expenses
            WHERE user_id = ?
        """
        params = [user_id]

        if year:
            query += " AND strftime('%Y', date) = ?"
            params.append(str(year))

        query += " GROUP BY month ORDER BY month ASC"

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return {row["month"]: float(row["total"]) for row in rows if row["month"]}

    except sqlite3.Error as e:
        print(f"[DB ERROR] Failed to calculate monthly expenses: {e}")
        return {}


# ----------------------------------------------------------------------------
# Module initialization
# ----------------------------------------------------------------------------

create_tables()