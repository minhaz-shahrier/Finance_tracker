import tkinter as tk
from tkinter import messagebox
from tkcalendar import Calendar
from datetime import datetime, timedelta
from database import add_transaction, generate_100_day_balance

def add_transaction_ui(root):
    window = tk.Toplevel(root)
    window.title("Add Transaction")
    window.configure(bg="white")

    # --- Date Selection ---
    tk.Label(window, text="Select Date:", bg="white").grid(row=0, column=0, padx=10, pady=5)
    today = datetime.today()
    cal = Calendar(window, selectmode='day', year=today.year, month=today.month, day=today.day, date_pattern="yyyy-mm-dd")
    cal.grid(row=0, column=1, padx=10, pady=5)

    # --- Description ---
    tk.Label(window, text="Description:", bg="white").grid(row=1, column=0, padx=10, pady=5)
    description_entry = tk.Entry(window)
    description_entry.grid(row=1, column=1, padx=10, pady=5)

    # --- Amount ---
    tk.Label(window, text="Amount:", bg="white").grid(row=2, column=0, padx=10, pady=5)
    amount_entry = tk.Entry(window)
    amount_entry.grid(row=2, column=1, padx=10, pady=5)

    # --- Type Buttons ---
    type_var = tk.StringVar(value="")

    def select_type(t):
        type_var.set(t)
        if t == "income":
            income_btn.config(bg="#28a745", fg="white")
            expense_btn.config(bg="white", fg="black")
        elif t == "expense":
            expense_btn.config(bg="#dc3545", fg="white")
            income_btn.config(bg="white", fg="black")

    tk.Label(window, text="Type:", bg="white").grid(row=3, column=0, padx=10, pady=5)
    type_frame = tk.Frame(window, bg="white")
    type_frame.grid(row=3, column=1, padx=10, pady=5)

    income_btn = tk.Button(type_frame, text="Income", width=10,
                           command=lambda: select_type("income"), bg="white", fg="black", relief="solid")
    income_btn.pack(side="left", padx=5)

    expense_btn = tk.Button(type_frame, text="Expense", width=10,
                            command=lambda: select_type("expense"), bg="white", fg="black", relief="solid")
    expense_btn.pack(side="left", padx=5)

    # --- Storage Type ---
    tk.Label(window, text="Storage Type:", bg="white").grid(row=4, column=0, padx=10, pady=5)
    storage_var = tk.StringVar(value="bank")  # default to 'bank'
    storage_menu = tk.OptionMenu(window, storage_var, "bank", "cash", "stock")
    storage_menu.config(bg="white")
    storage_menu.grid(row=4, column=1, padx=10, pady=5, sticky="w")

    # --- Recurrence ---
    tk.Label(window, text="Recurrence:", bg="white").grid(row=5, column=0, padx=10, pady=5)
    recurrence_var = tk.StringVar(value="None")
    recurrence_menu = tk.OptionMenu(window, recurrence_var, "None", "Weekly", "Bi-Weekly", "Monthly")
    recurrence_menu.config(bg="white")
    recurrence_menu.grid(row=5, column=1, padx=10, pady=5, sticky="w")

    tk.Label(window, text="Repeat Count (if recurring):", bg="white").grid(row=6, column=0, padx=10, pady=5)
    repeat_entry = tk.Entry(window)
    repeat_entry.grid(row=6, column=1, padx=10, pady=5)

    # --- Save Logic ---
    def save_transaction():
        base_date_str = cal.get_date()
        description = description_entry.get()

        try:
            amount = float(amount_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid amount.")
            return

        if not type_var.get():
            messagebox.showerror("Error", "Please select a transaction type.")
            return

        recurrence = recurrence_var.get()
        try:
            repeat_count = int(repeat_entry.get()) if recurrence != "None" else 1
            if repeat_count < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Repeat count must be a positive integer.")
            return

        # Determine recurrence interval
        delta_days = {
            "None": 0,
            "Weekly": 7,
            "Bi-Weekly": 14,
            "Monthly": 30  # Approximate
        }

        base_date = datetime.strptime(base_date_str, "%Y-%m-%d")

        for i in range(repeat_count):
            date_to_add = base_date + timedelta(days=i * delta_days[recurrence])
            add_transaction(date_to_add.strftime("%Y-%m-%d"), type_var.get(), amount, description, storage_var.get())

        # Generate 100-day balance using selected storage
        starting_amounts = {"bank": 0, "cash": 0, "stock": 0}
        starting_amounts[storage_var.get()] = amount
        balances = generate_100_day_balance(base_date_str, starting_amounts)

        low = next((b for b in balances if b[storage_var.get()] < 100), None)
        if low:
            messagebox.showwarning("Low Balance", f"{storage_var.get().capitalize()} balance below $100 on {low['date']}")

        messagebox.showinfo("Success", "Transaction(s) added.")
        window.destroy()

    # --- Add Button ---
    tk.Button(window, text="Add", command=save_transaction, bg="#28a745", fg="white").grid(row=7, column=0, columnspan=2, pady=10)
