
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("spendwise.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def create_table():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                expense TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS savings_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal_name TEXT NOT NULL,
                target_amount REAL NOT NULL,
                saved_amount REAL NOT NULL DEFAULT 0,
                deadline TEXT NOT NULL
            )
        """)


# Expense functions

def add_expense(expense, amount, category, expense_date):
    with get_connection() as connection:
        connection.execute("""
            INSERT INTO expenses (expense, amount, category, date)
            VALUES (?, ?, ?, ?)
        """, (expense, float(amount), category, str(expense_date)))


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


# Savings goal functions

def add_savings_goal(goal_name, target_amount, deadline):
    with get_connection() as connection:
        connection.execute("""
            INSERT INTO savings_goals
            (goal_name, target_amount, saved_amount, deadline)
            VALUES (?, ?, 0, ?)
        """, (goal_name, float(target_amount), str(deadline)))


def get_savings_goals():
    with get_connection() as connection:
        return connection.execute("""
            SELECT id, goal_name, target_amount, saved_amount, deadline
            FROM savings_goals
            ORDER BY id DESC
        """).fetchall()


def update_saved_amount(goal_id, amount):
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
