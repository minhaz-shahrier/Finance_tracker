import tkinter as tk
from tkinter import messagebox
from database import delete_transactions_for_month, get_transactions
from ui.add_transaction_ui import add_transaction_ui
from ui.monthly_view import show_month_view
from ui.table_view import show_table_view

def reset_month_ui(root):
    def perform_reset():
        try:
            month = int(month_entry.get())
            year = int(year_entry.get())
            if not (1 <= month <= 12):
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Month should be 1–12 and year a valid number.")
            return
        delete_transactions_for_month(month, year)
        messagebox.showinfo("Reset", f"Transactions for {month}/{year} deleted.")
        window.destroy()

    window = tk.Toplevel(root)
    window.title("Reset Month")
    window.configure(bg="white")

    tk.Label(window, text="Month (1–12):", bg="white").grid(row=0, column=0, padx=10, pady=5)
    month_entry = tk.Entry(window)
    month_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(window, text="Year:", bg="white").grid(row=1, column=0, padx=10, pady=5)
    year_entry = tk.Entry(window)
    year_entry.grid(row=1, column=1, padx=10, pady=5)

    tk.Button(window, text="Reset", command=perform_reset, bg="#dc3545", fg="white").grid(row=2, column=0, columnspan=2, pady=10)

def launch_main_ui():
    root = tk.Tk()
    root.title("Finance Tracker")
    root.configure(bg="white")

    def create_button(text, command):
        return tk.Button(root, text=text, command=command, bg="white", relief="flat", font=("Helvetica", 10), width=25)

    def show_summary():
        txs = get_transactions()
        summary_text.delete("1.0", tk.END)
        summary_text.insert(tk.END, "{:<12} {:<10} {:<10} {:<12} {:<15}\n".format("Date", "Type", "Amount", "Storage", "Description"))
        summary_text.insert(tk.END, "-"*65 + "\n")
        for tx in txs:
            summary_text.insert(tk.END, "{:<12} {:<10} {:<10} {:<12} {:<15}\n".format(
                tx["date"],
                tx["type"],
                f"${tx['amount']:.2f}",
                tx.get("storage_type", "bank"),  # default if missing
                tx["description"]
            ))

    tk.Label(root, text="Finance Tracker", bg="white", font=("Helvetica", 16, "bold")).pack(pady=10)
    create_button("Add Transaction", lambda: add_transaction_ui(root)).pack(pady=5)
    create_button("Show Transactions", show_summary).pack(pady=5)
    create_button("Month View", show_month_view).pack(pady=5)
    create_button("Table View", lambda: show_table_view(root)).pack(pady=5)
    create_button("Reset Month", lambda: reset_month_ui(root)).pack(pady=5)
    create_button("Exit", root.destroy).pack(pady=5)

    global summary_text
    summary_text = tk.Text(root, height=18, width=80, font=("Helvetica", 10))
    summary_text.pack(pady=10)

    root.mainloop()
