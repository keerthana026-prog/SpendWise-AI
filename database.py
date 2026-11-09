
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(__file__).with_name("spendwise.db")


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_table():
    with get_connection() as connection:

        # Existing expenses table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                expense TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL
            )
        """)

        # Existing savings goals table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS savings_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_name TEXT NOT NULL,
                target_amount REAL NOT NULL,
                saved_amount REAL NOT NULL DEFAULT 0,
                deadline TEXT NOT NULL
            )
        """)

        # New PayPal payments table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS paypal_payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT NOT NULL UNIQUE,
                capture_id TEXT UNIQUE,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'PENDING',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)


# --------------------------------------------------
# EXPENSE FUNCTIONS
# --------------------------------------------------

def add_expense(expense, amount, category, expense_date):
    with get_connection() as connection:
        connection.execute("""
            INSERT INTO expenses
            (expense, amount, category, date)
            VALUES (?, ?, ?, ?)
        """, (
            expense,
            float(amount),
            category,
            str(expense_date)
        ))


def get_expenses():
    with get_connection() as connection:
        return connection.execute("""
            SELECT id, expense, amount, category, date
            FROM expenses
            ORDER BY id DESC
        """).fetchall()


def delete_expense(expense_id):
    with get_connection() as connection:
        connection.execute(
            "DELETE FROM expenses WHERE id = ?",
            (expense_id,)
        )


# --------------------------------------------------
# SAVINGS GOAL FUNCTIONS
# --------------------------------------------------

def add_savings_goal(goal_name, target_amount, deadline):
    with get_connection() as connection:
        connection.execute("""
            INSERT INTO savings_goals
            (goal_name, target_amount, saved_amount, deadline)
            VALUES (?, ?, 0, ?)
        """, (
            goal_name,
            float(target_amount),
            str(deadline)
        ))


def get_savings_goals():
    with get_connection() as connection:
        return connection.execute("""
            SELECT id, goal_name, target_amount,
                   saved_amount, deadline
            FROM savings_goals
            ORDER BY id DESC
        """).fetchall()


def update_saved_amount(goal_id, amount):
    if float(amount) <= 0:
        raise ValueError("Savings contribution must be positive.")

    with get_connection() as connection:
        connection.execute("""
            UPDATE savings_goals
            SET saved_amount = saved_amount + ?
            WHERE id = ?
        """, (float(amount), goal_id))


def delete_savings_goal(goal_id):
    with get_connection() as connection:
        connection.execute(
            "DELETE FROM savings_goals WHERE id = ?",
            (goal_id,)
        )


# --------------------------------------------------
# PAYPAL PAYMENT FUNCTIONS
# --------------------------------------------------

def save_paypal_order(order_id, description, amount, currency="USD"):
    if not order_id:
        raise ValueError("PayPal order ID is required.")

    if float(amount) <= 0:
        raise ValueError("Payment amount must be positive.")

    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        connection.execute("""
            INSERT INTO paypal_payments
            (order_id, description, amount, currency,
             status, created_at, updated_at)
            VALUES (?, ?, ?, ?, 'PENDING', ?, ?)
            ON CONFLICT(order_id) DO NOTHING
        """, (
            order_id,
            description,
            float(amount),
            currency.upper(),
            now,
            now
        ))


def complete_paypal_payment(order_id, capture_id):
    if not order_id or not capture_id:
        raise ValueError("Order ID and capture ID are required.")

    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:

        payment = connection.execute("""
            SELECT status, capture_id
            FROM paypal_payments
            WHERE order_id = ?
        """, (order_id,)).fetchone()

        if payment is None:
            raise ValueError("PayPal order was not found.")

        if payment[0] == "COMPLETED":
            if payment[1] != capture_id:
                raise ValueError("Payment capture ID does not match.")
            return True

        connection.execute("""
            UPDATE paypal_payments
            SET capture_id = ?,
                status = 'COMPLETED',
                updated_at = ?
            WHERE order_id = ?
              AND status = 'PENDING'
        """, (capture_id, now, order_id))

        return True


def update_paypal_payment_status(order_id, status):
    allowed_statuses = {
        "PENDING",
        "APPROVED",
        "COMPLETED",
        "CANCELLED",
        "FAILED"
    }

    status = status.upper()

    if status not in allowed_statuses:
        raise ValueError("Invalid PayPal payment status.")

    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        connection.execute("""
            UPDATE paypal_payments
            SET status = ?, updated_at = ?
            WHERE order_id = ?
        """, (status, now, order_id))


def get_paypal_payments():
    with get_connection() as connection:
        return connection.execute("""
            SELECT id, order_id, capture_id, description,
                   amount, currency, status, created_at
            FROM paypal_payments
            ORDER BY id DESC
        """).fetchall()
