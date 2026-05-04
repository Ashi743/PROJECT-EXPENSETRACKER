import sqlite3
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db, init_db, seed_db

app = Flask(__name__)
app.secret_key = "dev-only-32-char-hex-key-12345678"

# Initialize database on startup
with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("profile"))

    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not name:
        return render_template("register.html", error="Name is required.")
    if len(name) > 100:
        return render_template("register.html", error="Name must be 100 characters or fewer.")
    if not email:
        return render_template("register.html", error="Email is required.")
    if "@" not in email:
        return render_template("register.html", error="Please enter a valid email address.")
    if len(email) > 255:
        return render_template("register.html", error="Email address is too long.")
    if not password:
        return render_template("register.html", error="Password is required.")
    if len(password) < 8:
        return render_template("register.html", error="Password must be at least 8 characters.")

    password_hash = generate_password_hash(password)
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return render_template("register.html", error="An account with this email already exists.")
    finally:
        conn.close()

    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("profile"))

    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    if not email or not password:
        return render_template("login.html", error="Email and password are required.")

    conn = get_db()
    try:
        user = conn.execute(
            "SELECT id, name, password_hash FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if user is None or not check_password_hash(user["password_hash"], password):
            return render_template("login.html", error="Invalid email or password.")

        session["user_id"] = user["id"]
        session["username"] = user["name"]
        return redirect(url_for("profile"))
    finally:
        conn.close()


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing", logged_out=True))


@app.route("/dashboard")
def dashboard():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    return render_template("dashboard.html", current_page="dashboard")


@app.route("/analytics")
def analytics():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    return render_template("analytics.html", current_page="analytics")


@app.route("/settings")
def settings():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    return render_template("settings.html", current_page="settings")


@app.route("/profile")
def profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    # --- Read and validate date filter query params ---
    raw_start = request.args.get("start_date", "").strip()
    raw_end = request.args.get("end_date", "").strip()

    filter_error = None
    start_date = None
    end_date = None

    if raw_start:
        try:
            start_date = datetime.strptime(raw_start, "%Y-%m-%d").date()
        except ValueError:
            filter_error = "Invalid start date. Please use YYYY-MM-DD format."

    if raw_end and not filter_error:
        try:
            end_date = datetime.strptime(raw_end, "%Y-%m-%d").date()
        except ValueError:
            filter_error = "Invalid end date. Please use YYYY-MM-DD format."

    if start_date and end_date and end_date < start_date and not filter_error:
        filter_error = "End date cannot be before start date."

    # If validation failed, clear the filter so we fall back to showing all expenses
    if filter_error:
        start_date = None
        end_date = None

    # --- Resolve the effective date bounds for SQL ---
    # Spec rules:
    #   start only  → start_date to today
    #   end only    → earliest possible date to end_date
    #   both        → between them inclusive
    #   neither     → no date filter (show all)
    today_str = date.today().isoformat()

    if start_date and end_date:
        sql_start = start_date.isoformat()
        sql_end = end_date.isoformat()
        filter_active = True
    elif start_date:
        sql_start = start_date.isoformat()
        sql_end = today_str
        filter_active = True
        # Normalise end_date for display purposes
        end_date = date.today()
    elif end_date:
        sql_start = "1900-01-01"  # earliest realistic date for open-ended end_date filters
        sql_end = end_date.isoformat()
        filter_active = True
    else:
        sql_start = None
        sql_end = None
        filter_active = False

    conn = get_db()
    try:
        user = conn.execute(
            "SELECT id, name, email, created_at FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()

        if not user:
            session.clear()
            return redirect(url_for("login"))

        if filter_active:
            totals = conn.execute(
                """SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total
                   FROM expenses
                   WHERE user_id = ? AND date BETWEEN ? AND ?""",
                (user_id, sql_start, sql_end),
            ).fetchone()

            recent = conn.execute(
                """SELECT id, category, amount, date, description
                   FROM expenses
                   WHERE user_id = ? AND date BETWEEN ? AND ?
                   ORDER BY date DESC
                   LIMIT 6""",
                (user_id, sql_start, sql_end),
            ).fetchall()

            by_category = conn.execute(
                """SELECT category, COUNT(*) as count, SUM(amount) as total
                   FROM expenses
                   WHERE user_id = ? AND date BETWEEN ? AND ?
                   GROUP BY category
                   ORDER BY total DESC""",
                (user_id, sql_start, sql_end),
            ).fetchall()
        else:
            totals = conn.execute(
                "SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total FROM expenses WHERE user_id = ?",
                (user_id,)
            ).fetchone()

            recent = conn.execute(
                """SELECT id, category, amount, date, description
                   FROM expenses WHERE user_id = ?
                   ORDER BY date DESC LIMIT 6""",
                (user_id,)
            ).fetchall()

            by_category = conn.execute(
                """SELECT category, COUNT(*) as count, SUM(amount) as total
                   FROM expenses WHERE user_id = ?
                   GROUP BY category ORDER BY total DESC""",
                (user_id,)
            ).fetchall()
    finally:
        conn.close()

    try:
        joined = datetime.strptime(user["created_at"], "%Y-%m-%d %H:%M:%S").strftime("%B %d, %Y")
    except (ValueError, TypeError):
        joined = user["created_at"]

    # --- Build human-readable filter label for the template ---
    filter_label = None
    if filter_active:
        def fmt(d):
            # Removes leading zeros from day: "April 01" → "April 1"
            return d.strftime("%B %d, %Y").replace(" 0", " ")
        if start_date and end_date:
            filter_label = f"{fmt(start_date)} – {fmt(end_date)}"
        elif start_date:
            filter_label = f"From {fmt(start_date)}"
        elif end_date:
            filter_label = f"Up to {fmt(end_date)}"

    return render_template(
        "profile.html",
        user=user,
        totals=totals,
        recent=recent,
        by_category=by_category,
        joined=joined,
        has_filter=filter_active,
        filter_message=filter_label,
        date_error=filter_error,
        start_date=raw_start,
        end_date=raw_end,
        current_page="profile",
    )


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/expenses/add", methods=["GET", "POST"])
def add_expense():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    VALID_CATEGORIES = ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]

    if request.method == "GET":
        today = date.today().isoformat()
        return render_template("add_expense.html", current_page="add_expense", today=today)

    # --- Validate POST fields ---
    amount_raw = request.form.get("amount", "").strip()
    category   = request.form.get("category", "").strip()
    date_raw   = request.form.get("date", "").strip()
    description = request.form.get("description", "").strip()

    def fail(msg):
        today = date.today().isoformat()
        return render_template("add_expense.html",
                               current_page="add_expense",
                               error=msg,
                               amount=amount_raw,
                               category=category,
                               date=date_raw,
                               description=description,
                               today=today)

    if not amount_raw:
        return fail("Amount is required.")
    try:
        amount = float(amount_raw)
    except ValueError:
        return fail("Please enter a valid amount.")
    if amount <= 0:
        return fail("Amount must be greater than 0.")

    if not category or category not in VALID_CATEGORIES:
        return fail("Please select a valid category.")

    if not date_raw:
        return fail("Date is required.")
    try:
        expense_date = datetime.strptime(date_raw, "%Y-%m-%d").date()
    except ValueError:
        return fail("Please enter a valid date.")
    if expense_date > date.today():
        return fail("Date cannot be in the future.")

    if len(description) > 500:
        return fail("Description must be 500 characters or fewer.")

    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            (user_id, amount, category, date_raw, description or None),
        )
        conn.commit()
    finally:
        conn.close()

    return redirect(url_for("profile"))


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)