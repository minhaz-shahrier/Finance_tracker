import tkinter as tk
from calendar import monthrange
from datetime import datetime
from database import get_transactions

def show_month_view():
    def refresh_calendar(year, month):
        for widget in calendar_frame.winfo_children():
            widget.destroy()

        for i, day in enumerate(["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]):
            tk.Label(calendar_frame, text=day, font=("Helvetica", 10, "bold"), bg="white").grid(row=0, column=i, padx=5, pady=5)

        tx_map = {}
        for tx in get_transactions():
            tx_date = tx["date"]
            storage = tx.get("storage_type", "bank")
            tx_map.setdefault(tx_date, {}).setdefault(storage, 0)
            if tx["type"].lower() == "income":
                tx_map[tx_date][storage] += tx["amount"]
            elif tx["type"].lower() == "expense":
                tx_map[tx_date][storage] -= tx["amount"]

        storages = ["bank", "cash", "stock"]
        balances = {s: 0.0 for s in storages}
        start_date = datetime(year, month, 1)

        for tx_date in sorted(tx_map.keys()):
            if tx_date < start_date.strftime("%Y-%m-%d"):
                for s in tx_map[tx_date]:
                    balances[s] += tx_map[tx_date][s]

        start_weekday = (start_date.weekday() + 1) % 7
        num_days = monthrange(year, month)[1]
        row, col = 1, start_weekday

        for day in range(1, num_days + 1):
            date_str = f"{year}-{month:02d}-{day:02d}"
            delta_by_storage = tx_map.get(date_str, {})
            for s in delta_by_storage:
                balances[s] += delta_by_storage[s]

            total = sum(balances.values())

            # Text widget for rich formatting
            text = tk.Text(calendar_frame, width=16, height=6, relief="solid", bg="white", font=("Courier", 9))
            text.grid(row=row, column=col, padx=1, pady=1)
            text.insert("end", f"{day}\n", "header")

            # Define tags
            text.tag_config("red", foreground="red")
            text.tag_config("green", foreground="green")
            text.tag_config("header", font=("Helvetica", 10, "bold"))

            # Insert each storage line with color
            for s in storages:
                value = balances[s]
                color = "green" if value >= 0 else "red"
                label = f"{s[:1].upper()}: ${value:.2f}\n"
                text.insert("end", label, color)

            # Insert total with color
            total_color = "green" if total >= 0 else "red"
            text.insert("end", f"T: ${total:.2f}", total_color)

            text.config(state="disabled")  # Prevent editing

            col += 1
            if col > 6:
                col = 0
                row += 1

        header_label.config(text=f"{datetime(year, month, 1).strftime('%B %Y')} – Running Balances w/ Total")
        grand_total = sum(balances.values())
        total_label.config(text=f"Grand Total (All Accounts): ${grand_total:.2f}")

    def update():
        y, m = selected_year.get(), selected_month.get()
        if 1 <= m <= 12:
            refresh_calendar(y, m)
        else:
            tk.messagebox.showerror("Invalid Month", "Month must be between 1 and 12.")

    def next_month():
        m, y = selected_month.get(), selected_year.get()
        if m == 12:
            selected_month.set(1)
            selected_year.set(y + 1)
        else:
            selected_month.set(m + 1)
        update()

    def prev_month():
        m, y = selected_month.get(), selected_year.get()
        if m == 1:
            selected_month.set(12)
            selected_year.set(y - 1)
        else:
            selected_month.set(m - 1)
        update()

    window = tk.Toplevel()
    window.title("Monthly Calendar View")
    window.configure(bg="white")

    now = datetime.now()
    selected_year = tk.IntVar(value=now.year)
    selected_month = tk.IntVar(value=now.month)

    header_label = tk.Label(window, text="", font=("Helvetica", 14, "bold"), bg="white")
    header_label.pack(pady=5)

    control_frame = tk.Frame(window, bg="white")
    control_frame.pack()

    tk.Button(control_frame, text="◀ Previous", command=prev_month, bg="#f0f0f0").grid(row=0, column=0, padx=5)
    tk.Label(control_frame, text="Year:", bg="white").grid(row=0, column=1)
    tk.Entry(control_frame, textvariable=selected_year, width=6).grid(row=0, column=2)
    tk.Label(control_frame, text="Month:", bg="white").grid(row=0, column=3)
    tk.Entry(control_frame, textvariable=selected_month, width=4).grid(row=0, column=4)
    tk.Button(control_frame, text="Go", command=update, bg="#007bff", fg="white").grid(row=0, column=5, padx=5)
    tk.Button(control_frame, text="Next ▶", command=next_month, bg="#f0f0f0").grid(row=0, column=6, padx=5)

    calendar_frame = tk.Frame(window, bg="white")
    calendar_frame.pack(padx=10, pady=10)

    total_label = tk.Label(window, text="", font=("Helvetica", 12, "bold"), bg="white")
    total_label.pack(pady=5)

    refresh_calendar(selected_year.get(), selected_month.get())
