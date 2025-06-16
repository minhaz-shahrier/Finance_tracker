def calculate_summary(months):
    transactions = get_transactions()
    storage_types = {"bank", "cash", "stock"}

    # Initialize dictionary: month ➝ storage ➝ {income, expense, balance}
    month_totals = {
        month: {
            storage: {"income": 0, "expense": 0, "balance": 0}
            for storage in storage_types
        }
        for month in months
    }

    for tx in transactions:
        tx_date = datetime.strptime(tx["date"], "%Y-%m-%d")
        tx_type = tx["type"]
        tx_amount = tx["amount"]
        storage = tx.get("storage_type", "bank")  # default to bank if missing

        for month in months:
            month_start = datetime.strptime(f"01 {month}", "%d %B %Y")
            month_end = month_start + timedelta(days=31)
            if month_start <= tx_date < month_end:
                month_totals[month][storage][tx_type] += tx_amount

    # Compute balance per storage per month (cumulative)
    previous_balances = {s: 0 for s in storage_types}
    for month in months:
        for storage in storage_types:
            income = month_totals[month][storage]["income"]
            expense = month_totals[month][storage]["expense"]
            balance = income - expense + previous_balances[storage]
            month_totals[month][storage]["balance"] = balance
            previous_balances[storage] = balance

    return month_totals
