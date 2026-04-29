import sqlite3
import random
from datetime import datetime
from werkzeug.security import generate_password_hash
from db import get_db, DATABASE

# Indian first and last names
first_names = [
    "Rajesh", "Priya", "Amit", "Neha", "Arjun", "Sneha", "Vikram",
    "Isha", "Rohan", "Anjali", "Arun", "Divya", "Sanjay", "Pooja",
    "Aditi", "Nikhil", "Shreya", "Rahul", "Aarav", "Diya"
]

last_names = [
    "Sharma", "Patel", "Singh", "Kumar", "Reddy", "Gupta", "Mishra",
    "Verma", "Nair", "Desai", "Iyer", "Rao", "Bhat", "Malhotra",
    "Chopra", "Bose", "Dutta", "Roy", "Das", "Pandey"
]

def generate_unique_user():
    """Generate a unique user until email is not in database."""
    while True:
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        name = f"{first_name} {last_name}"

        # Derive email from last name + random number
        email = f"{last_name.lower()}{random.randint(10, 99)}@gmail.com"

        # Check if email already exists
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        existing = cursor.fetchone()
        conn.close()

        if not existing:
            # Email is unique, return the user data
            password_hash = generate_password_hash("password123")
            created_at = datetime.now().isoformat()
            return name, email, password_hash, created_at

def seed_single_user():
    """Insert a single random Indian user into the database."""
    name, email, password_hash, created_at = generate_unique_user()

    # Insert the user
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
        (name, email, password_hash, created_at)
    )

    user_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # Print confirmation
    print(f"\nUser created successfully!")
    print(f"  ID:    {user_id}")
    print(f"  Name:  {name}")
    print(f"  Email: {email}\n")

    return user_id, name, email

if __name__ == "__main__":
    seed_single_user()
