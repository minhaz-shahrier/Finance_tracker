import tkinter as tk
from tkinter import ttk, messagebox
from database import get_transactions, delete_transaction_by_id

def show_table_view(root):
    window = tk.Toplevel(root)
    window.title("Transaction Table View")
    window.geometry("1100x600")

    cols = ["Date", "Type", "Amount", "Storage", "Description", "Bank", "Cash", "Stock", "Total"]
    tree = ttk.Treeview(window, columns=cols, show='headings', selectmode='browse')

    column_widths = {
        "Date": 90,
        "Type": 70,
        "Amount": 80,
        "Storage": 75,
        "Description": 150,
        "Bank": 90,
        "Cash": 90,
        "Stock": 90,
        "Total": 100
    }

    for col in cols:
        tree.column(col, width=column_widths[col], anchor="center")

    # Mapping to track reverse sorting state
    sort_states = {col: False for col in cols}

    def sort_column(col, reverse):
        # Extract column data and associated item IDs
        data = [(tree.set(child, col), child) for child in tree.get_children()]

        # Clean values for numeric sorting
        def try_parse(val):
            val = val.replace("$", "").replace(",", "").strip()
            try:
                return float(val)
            except ValueError:
                return val.lower()

        data.sort(key=lambda item: try_parse(item[0]), reverse=reverse)

        for index, (val, iid) in enumerate(data):
            tree.move(iid, '', index)

        # Toggle sort direction
        sort_states[col] = not reverse

    # Attach sort handler to headers
    for col in cols:
        tree.heading(col, text=col, command=lambda _col=col: sort_column(_col, sort_states[_col]))

    tree.pack(padx=10, pady=10, fill="both", expand=True)

    total_label = tk.Label(window, text="", font=("Helvetica", 12, "bold"), bg="white")
    total_label.pack(pady=5)

    tree_item_to_tx_id = {}
    running_totals = {"bank": 0.0, "cash": 0.0, "stock": 0.0}

    def refresh_table():
        nonlocal running_totals
        nonlocal total_label
        running_totals = {"bank": 0.0, "cash": 0.0, "stock": 0.0}
        tree_item_to_tx_id.clear()
        tree.delete(*tree.get_children())

        transactions = get_transactions()
        for tx in transactions:
            amount = float(tx["amount"])
            storage = tx.get("storage_type", "bank")
            if tx["type"].lower() == "income":
                running_totals[storage] += amount
            else:
                running_totals[storage] -= amount

            total = sum(running_totals.values())

            item_id = tree.insert("", "end", values=(
                tx["date"],
                tx["type"],
                f"${amount:.2f}",
                storage,
                tx["description"],
                f"${running_totals['bank']:.2f}",
                f"${running_totals['cash']:.2f}",
                f"${running_totals['stock']:.2f}",
                f"${total:.2f}",
            ))
            tree_item_to_tx_id[item_id] = tx["id"]

        total_label.config(text=f"Grand Total (All Accounts): ${sum(running_totals.values()):.2f}")

    def delete_selected():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Error", "No transaction selected.")
            return
        item_id = selected[0]
        tx_id = tree_item_to_tx_id.get(item_id)
        if tx_id is None:
            messagebox.showerror("Error", "Transaction ID not found.")
            return
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this transaction?")
        if confirm:
            delete_transaction_by_id(tx_id)
            refresh_table()
            messagebox.showinfo("Deleted", "Transaction deleted successfully.")

    tk.Button(window, text="Delete Selected", command=delete_selected, bg="#dc3545", fg="white").pack(pady=5)

    refresh_table()
