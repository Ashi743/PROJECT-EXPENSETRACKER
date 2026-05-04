import sqlite3
import random
from datetime import datetime, timedelta

DATABASE = "spendly.db"

def get_db():
    """Open connection to SQLite database with foreign keys enabled."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# Categories with realistic Indian descriptions and amounts
categories = {
    "food": {
        "descriptions": ["Groceries", "Restaurant lunch", "Coffee shop", "Breakfast", "Snacks", "Dinner out", "Sweets", "Bakery"],
        "range": (50, 800)
    },
    "transport": {
        "descriptions": ["Auto/Taxi", "Fuel", "Bus fare", "Train ticket", "Bike maintenance", "Parking", "Uber"],
        "range": (20, 500)
    },
    "bills": {
        "descriptions": ["Electricity bill", "Water bill", "Internet bill", "Mobile recharge", "Insurance", "Rent"],
        "range": (200, 3000)
    },
    "health": {
        "descriptions": ["Medicine", "Doctor visit", "Pharmacy", "Gym membership", "Health checkup"],
        "range": (100, 2000)
    },
    "entertainment": {
        "descriptions": ["Movie tickets", "Concert", "OTT subscription", "Gaming", "Books"],
        "range": (100, 1500)
    },
    "shopping": {
        "descriptions": ["Clothes", "Shoes", "Electronics", "Home decor", "Accessories", "Gadgets"],
        "range": (200, 5000)
    },
    "other": {
        "descriptions": ["Miscellaneous", "Gifts", "Donation", "Stationery", "Tools"],
        "range": (50, 1000)
    }
}

# Distribution weights (food most common, health/entertainment least)
category_weights = {
    "food": 35,
    "transport": 20,
    "bills": 15,
    "shopping": 15,
    "other": 10,
    "health": 3,
    "entertainment": 2
}

def generate_expenses(user_id, count, months):
    """Generate expenses spread across months."""
    expenses = []
    today = datetime.now().date()

    for i in range(count):
        # Random date within the past N months
        days_back = random.randint(0, months * 30)
        expense_date = today - timedelta(days=days_back)

        # Select category based on weights
        category = random.choices(
            list(category_weights.keys()),
            weights=list(category_weights.values()),
            k=1
        )[0]

        # Generate amount and description
        min_amt, max_amt = categories[category]["range"]
        amount = round(random.uniform(min_amt, max_amt), 2)
        description = random.choice(categories[category]["descriptions"])

        expenses.append({
            "user_id": user_id,
            "amount": amount,
            "category": category.capitalize(),
            "date": expense_date.isoformat(),
            "description": description
        })

    return expenses

def insert_expenses(user_id, count, months):
    """Insert expenses for user, rollback on failure."""
    expenses = generate_expenses(user_id, count, months)

    conn = get_db()
    try:
        cursor = conn.cursor()

        for exp in expenses:
            cursor.execute(
                "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                (exp["user_id"], exp["amount"], exp["category"], exp["date"], exp["description"])
            )

        conn.commit()
        return expenses
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

if __name__ == "__main__":
    user_id = 7
    count = 20
    months = 5

    try:
        expenses = insert_expenses(user_id, count, months)

        # Step 4 - Confirm results
        print(f"\n[OK] Inserted {len(expenses)} expenses for user {user_id}")

        dates = sorted([exp["date"] for exp in expenses])
        print(f"[OK] Date range: {dates[0]} to {dates[-1]}")

        print("\n[OK] Sample of 5 inserted records:")
        for i, exp in enumerate(expenses[:5], 1):
            print(f"  {i}. {exp['category']} - Rs.{exp['amount']} on {exp['date']} - {exp['description']}")

    except Exception as e:
        print(f"Error: {e}")
