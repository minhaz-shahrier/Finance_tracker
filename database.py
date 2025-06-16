import sqlite3
from datetime import datetime, timedelta

def get_connection():
    conn = sqlite3.connect("finance_data.db")
    conn.row_factory = sqlite3.Row
    return conn

def setup_database():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        type TEXT,
        amount REAL,
        description TEXT,
        storage_type TEXT  -- NEW: "bank", "cash", or "stock"
    )
    """)
    conn.commit()
    conn.close()

def add_transaction(date, t_type, amount, description, storage_type):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO transactions (date, type, amount, description, storage_type) 
        VALUES (?, ?, ?, ?, ?)
    """, (date, t_type, amount, description, storage_type))
    conn.commit()
    conn.close()

def delete_transactions_for_month(month, year):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        DELETE FROM transactions 
        WHERE strftime('%m', date) = ? AND strftime('%Y', date) = ?
    """, (f"{int(month):02d}", str(year)))
    conn.commit()
    conn.close()

def get_transactions():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM transactions ORDER BY date")
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_transaction_by_id(tx_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
    conn.commit()
    conn.close()


def generate_100_day_balance(start_date_str, starting_amounts):
    transactions = get_transactions()
    storage_types = {"bank", "cash", "stock"}

    # Prepare daily change per storage
    daily_changes = {}
    for tx in transactions:
        date = tx["date"]
        storage = tx.get("storage_type", "bank")
        amount = tx["amount"] if tx["type"] == "income" else -tx["amount"]
        if date not in daily_changes:
            daily_changes[date] = {}
        daily_changes[date][storage] = daily_changes[date].get(storage, 0) + amount

    balances = []
    current_balances = {
        storage: starting_amounts.get(storage, 0.0)
        for storage in storage_types
    }

    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    for i in range(100):
        current_date = start_date + timedelta(days=i)
        date_str = current_date.strftime('%Y-%m-%d')

        if date_str in daily_changes:
            for storage, delta in daily_changes[date_str].items():
                current_balances[storage] += delta

        balances.append({
            "date": date_str,
            **{s: round(b, 2) for s, b in current_balances.items()}
        })

    return balances
