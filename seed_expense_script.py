#!/usr/bin/env python3
import sqlite3
from datetime import datetime, timedelta
import random
import sys

# Add database module to path
sys.path.insert(0, '/c/Users/Lenovo/OneDrive/Desktop/hello_world/expense-tracker/expense-tracker')
from database.db import get_db, DATABASE

def seed_expenses(user_id, count, months):
    """Seed expenses for a user spread across months."""

    # Parse arguments
    try:
        user_id = int(user_id)
        count = int(count)
        months = int(months)
    except (ValueError, TypeError):
        print("usage: /seed-expense <user_id> <count> <months>  example: /seed-expense 1 50 6")
        return

    # Verify user exists
    conn = get_db()
    try:
        cursor = conn.cursor()
        user = cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,)).fetchone()

        if not user:
            print(f"No user found with id {user_id}")
            return

        # Category configuration (weights for distribution)
        categories = {
            "Food": {"weight": 4, "amount_range": (50, 800), "descriptions": [
                "Lunch at restaurant", "Coffee and snacks", "Grocery shopping",
                "Dinner with friends", "Food delivery", "Bakery"
            ]},
            "Transport": {"weight": 2, "amount_range": (20, 500), "descriptions": [
                "Petrol/Diesel", "Auto ride", "Cab fare", "Train ticket", "Bus pass", "Parking"
            ]},
            "Bills": {"weight": 2, "amount_range": (200, 3000), "descriptions": [
                "Electricity bill", "Water bill", "Internet bill", "Mobile recharge",
                "Insurance", "Rent payment"
            ]},
            "Health": {"weight": 1, "amount_range": (100, 2000), "descriptions": [
                "Doctor consultation", "Pharmacy medicines", "Hospital bills",
                "Dental checkup", "Gym membership", "Medical tests"
            ]},
            "Entertainment": {"weight": 1, "amount_range": (100, 1500), "descriptions": [
                "Movie tickets", "Concert", "Streaming subscription", "Gaming",
                "Amusement park", "Sports event"
            ]},
            "Shopping": {"weight": 2, "amount_range": (200, 5000), "descriptions": [
                "Clothes shopping", "Electronics", "Home appliances", "Books",
                "Footwear", "Fashion items"
            ]},
            "Other": {"weight": 1, "amount_range": (50, 1000), "descriptions": [
                "Miscellaneous", "Gifts", "Personal care", "Subscriptions",
                "Hobbies", "Repairs"
            ]}
        }

        # Calculate total weight for distribution
        total_weight = sum(cat["weight"] for cat in categories.values())

        # Generate expenses
        expenses = []
        inserted_dates = []

        for _ in range(count):
            # Random category based on weights
            rand = random.uniform(0, total_weight)
            cumulative = 0
            selected_category = None

            for category_name, cat_data in categories.items():
                cumulative += cat_data["weight"]
                if rand <= cumulative:
                    selected_category = category_name
                    break

            if not selected_category:
                selected_category = "Other"

            cat_data = categories[selected_category]
            amount = round(random.uniform(cat_data["amount_range"][0], cat_data["amount_range"][1]), 2)
            description = random.choice(cat_data["descriptions"])

            # Random date within the past months
            days_back = random.randint(0, months * 30)
            expense_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            inserted_dates.append(expense_date)

            expenses.append((user_id, amount, selected_category, expense_date, description))

        # Insert all expenses in a transaction
        try:
            cursor.executemany(
                "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                expenses
            )
            conn.commit()

            # Print confirmation
            print(f"\n[OK] Successfully inserted {count} expenses for user {user_id}")

            # Date range
            min_date = min(inserted_dates)
            max_date = max(inserted_dates)
            print(f"  Date range: {min_date} to {max_date}")

            # Sample of inserted records
            print(f"\n  Sample of inserted records:")
            records = cursor.execute(
                "SELECT id, category, amount, date, description FROM expenses WHERE user_id = ? ORDER BY id DESC LIMIT 5",
                (user_id,)
            ).fetchall()

            for record in records:
                print(f"    - {record['category']:15} Rs.{record['amount']:8.2f} on {record['date']}  ({record['description']})")

        except Exception as e:
            conn.rollback()
            print(f"Error inserting expenses: {e}")

    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("usage: seed_expense_script.py <user_id> <count> <months>  example: seed_expense_script.py 1 50 6")
        sys.exit(1)

    seed_expenses(sys.argv[1], sys.argv[2], sys.argv[3])
