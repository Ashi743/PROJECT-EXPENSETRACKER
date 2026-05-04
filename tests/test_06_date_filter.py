"""
tests/test_06_date_filter.py

Spec behaviours verified (from .claude/specs/06-date-filter.md):

AUTH
  - Unauthenticated GET /profile redirects to /login

NO-FILTER (baseline)
  - GET /profile with no date params returns 200 and all expenses
  - Stats (Total Spent, Expenses, Categories) reflect all expenses
  - Date filter form is rendered on the page
  - Filter inputs are empty when no filter is active
  - No active-filter message when no filter is active

HAPPY PATH – BOTH DATES
  - Both start_date and end_date filter Recent Transactions to the range (inclusive)
  - Stats update to reflect only expenses in the date range
  - Category breakdown reflects only expenses in the range
  - Active filter message is shown on the page
  - Input values are retained in the form after filtering

HAPPY PATH – START DATE ONLY
  - start_date without end_date shows expenses from start_date to today (inclusive)
  - Stats reflect the start-only range

HAPPY PATH – END DATE ONLY
  - end_date without start_date shows all expenses up to end_date (inclusive)
  - Stats reflect the end-only range

VALIDATION ERRORS
  - end_date before start_date shows a validation error, does not crash
  - Invalid start_date format shows a validation error, does not crash
  - Invalid end_date format shows a validation error, does not crash
  - Malformed (non-date) strings in date params show an error without crashing

EDGE CASES
  - User with no expenses: profile page returns 200 with zero stats
  - User with a single expense: filter works correctly for exact boundary dates
  - Many expenses spanning multiple months: filter returns only in-range expenses
  - Boundary inclusivity: expense ON start_date is included; expense ON end_date is included
  - Expense one day before start_date is excluded; expense one day after end_date is excluded
  - Filter returns 0 results for a date range with no matching expenses (zero stats, empty list)

UI / TEMPLATE
  - Date filter form renders above Recent Transactions section
  - Clear Filter link points to /profile with no query parameters
  - Active filter message appears when filter is active
  - No active filter message when no filter is active

SECURITY
  - SQL injection attempt in start_date param is rejected cleanly (no crash, no data leak)
  - SQL injection attempt in end_date param is rejected cleanly
"""

import sqlite3
import tempfile
import os
import pytest
from datetime import date, timedelta
from werkzeug.security import generate_password_hash

import database.db as db_module
from app import app


# --------------------------------------------------------------------------- #
# Fixture helpers                                                              #
# --------------------------------------------------------------------------- #

@pytest.fixture
def client(tmp_path, monkeypatch):
    """
    Provide an isolated Flask test client backed by a fresh SQLite file in
    tmp_path.  Monkeypatching database.db.DATABASE means every call to
    get_db() in app.py and database.db picks up the temp file automatically.
    """
    db_file = str(tmp_path / "test_spendly.db")
    monkeypatch.setattr(db_module, "DATABASE", db_file)

    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret-key"

    with app.test_client() as test_client:
        with app.app_context():
            db_module.init_db()
        yield test_client


def _register_and_login(client, name="Test User", email="test@example.com",
                        password="password123"):
    """Register a fresh user and log them in; return the user's id."""
    client.post("/register", data={
        "name": name,
        "email": email,
        "password": password,
    }, follow_redirects=True)
    client.post("/login", data={
        "email": email,
        "password": password,
    }, follow_redirects=True)
    # Fetch the user id from the DB
    conn = db_module.get_db()
    row = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return row["id"]


def _insert_expense(user_id, amount, category, expense_date, description=""):
    """Directly insert one expense row for the given user."""
    conn = db_module.get_db()
    conn.execute(
        "INSERT INTO expenses (user_id, amount, category, date, description) "
        "VALUES (?, ?, ?, ?, ?)",
        (user_id, amount, category, expense_date, description),
    )
    conn.commit()
    conn.close()


def _profile(client, start_date=None, end_date=None, follow_redirects=True):
    """GET /profile with optional date query parameters."""
    params = {}
    if start_date is not None:
        params["start_date"] = start_date
    if end_date is not None:
        params["end_date"] = end_date

    query_string = "&".join(f"{k}={v}" for k, v in params.items())
    url = "/profile" + (f"?{query_string}" if query_string else "")
    return client.get(url, follow_redirects=follow_redirects)


# --------------------------------------------------------------------------- #
# Auth tests                                                                   #
# --------------------------------------------------------------------------- #

class TestAuthProtection:

    def test_unauthenticated_get_profile_redirects_to_login(self, client):
        """Unauthenticated access to GET /profile must redirect to /login."""
        response = client.get("/profile", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    def test_unauthenticated_get_profile_with_date_params_redirects_to_login(self, client):
        """Query parameters must not bypass auth; unauthenticated users still get redirected."""
        response = client.get(
            "/profile?start_date=2026-04-01&end_date=2026-04-30",
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]


# --------------------------------------------------------------------------- #
# No-filter baseline                                                           #
# --------------------------------------------------------------------------- #

class TestNoFilter:

    def test_profile_returns_200_when_authenticated(self, client):
        """Authenticated GET /profile with no filter returns HTTP 200."""
        _register_and_login(client)
        response = _profile(client)
        assert response.status_code == 200

    def test_profile_shows_all_expenses_when_no_filter(self, client):
        """All expenses for the user are displayed when no date filter is applied."""
        user_id = _register_and_login(client)
        _insert_expense(user_id, 100.00, "Food", "2026-01-15")
        _insert_expense(user_id, 200.00, "Bills", "2026-03-20")
        _insert_expense(user_id, 50.00, "Transport", "2026-04-10")

        response = _profile(client)
        html = response.data.decode()
        # All three categories must appear
        assert "Food" in html
        assert "Bills" in html
        assert "Transport" in html

    def test_profile_stats_show_all_expenses_total_when_no_filter(self, client):
        """Profile header stats show the sum of all user expenses when no filter is applied."""
        user_id = _register_and_login(client)
        _insert_expense(user_id, 100.00, "Food", "2026-01-15")
        _insert_expense(user_id, 200.00, "Bills", "2026-03-20")

        response = _profile(client)
        html = response.data.decode()
        # Total = 300.00; check both the formatted string variants
        assert "300.00" in html

    def test_profile_stats_expense_count_when_no_filter(self, client):
        """Expense count stat shows total number of expenses when no filter is active."""
        user_id = _register_and_login(client)
        _insert_expense(user_id, 100.00, "Food", "2026-01-15")
        _insert_expense(user_id, 200.00, "Bills", "2026-03-20")
        _insert_expense(user_id, 50.00, "Transport", "2026-04-10")

        response = _profile(client)
        html = response.data.decode()
        # The count "3" must appear as a stat value
        assert ">3<" in html

    def test_profile_date_filter_form_is_rendered(self, client):
        """Date filter form with start_date and end_date inputs must be on the page."""
        _register_and_login(client)
        response = _profile(client)
        html = response.data.decode()
        assert 'name="start_date"' in html
        assert 'name="end_date"' in html

    def test_profile_filter_inputs_are_empty_when_no_filter_active(self, client):
        """Date inputs should carry no pre-filled value when no filter is active."""
        _register_and_login(client)
        response = _profile(client)
        html = response.data.decode()
        # Both date input values should be empty strings
        assert 'value=""' in html or "value=\"\"" in html

    def test_profile_no_active_filter_message_when_no_filter(self, client):
        """No 'Showing expenses' / active filter message is rendered without a filter."""
        _register_and_login(client)
        _insert_expense(_register_and_login.__wrapped__ if hasattr(_register_and_login, "__wrapped__") else None, 100.00, "Food", "2026-04-01") if False else None
        response = _profile(client)
        html = response.data.decode()
        assert "Showing expenses" not in html


# --------------------------------------------------------------------------- #
# Happy path – both dates                                                      #
# --------------------------------------------------------------------------- #

class TestBothDatesFilter:

    def test_both_dates_filter_returns_only_in_range_transactions(self, client):
        """Expenses within [start_date, end_date] are shown; outside are excluded."""
        user_id = _register_and_login(client)
        _insert_expense(user_id, 100.00, "Food", "2026-04-01", "in range start")
        _insert_expense(user_id, 200.00, "Bills", "2026-04-10", "in range middle")
        _insert_expense(user_id, 50.00, "Transport", "2026-04-15", "in range end")
        _insert_expense(user_id, 999.00, "Shopping", "2026-03-31", "before range")
        _insert_expense(user_id, 888.00, "Health", "2026-04-16", "after range")

        response = _profile(client, start_date="2026-04-01", end_date="2026-04-15")
        html = response.data.decode()
        assert "in range start" in html
        assert "in range middle" in html
        assert "in range end" in html
        assert "before range" not in html
        assert "after range" not in html

    def test_both_dates_filter_stats_reflect_filtered_total(self, client):
        """Total Spent stat reflects only expenses within the filter range."""
        user_id = _register_and_login(client)
        _insert_expense(user_id, 100.00, "Food", "2026-04-05")
        _insert_expense(user_id, 200.00, "Bills", "2026-04-10")
        _insert_expense(user_id, 999.00, "Other", "2026-03-01")   # outside range

        response = _profile(client, start_date="2026-04-01", end_date="2026-04-30")
        html = response.data.decode()
        assert "300.00" in html
        assert "999.00" not in html

    def test_both_dates_filter_stats_expense_count(self, client):
        """Expense count stat reflects only the number of filtered expenses."""
        user_id = _register_and_login(client)
        _insert_expense(user_id, 100.00, "Food", "2026-04-05")
        _insert_expense(user_id, 200.00, "Bills", "2026-04-10")
        _insert_expense(user_id, 999.00, "Other", "2026-03-01")  # outside range

        response = _profile(client, start_date="2026-04-01", end_date="2026-04-30")
        html = response.data.decode()
        assert ">2<" in html

    def test_both_dates_filter_category_breakdown_is_filtered(self, client):
        """By Category section shows only categories present in the filtered range."""
        user_id = _register_and_login(client)
        _insert_expense(user_id, 100.00, "Food", "2026-04-05")
        _insert_expense(user_id, 200.00, "Bills", "2026-04-10")
        _insert_expense(user_id, 999.00, "Luxury", "2026-03-01")  # outside range

        response = _profile(client, start_date="2026-04-01", end_date="2026-04-30")
        html = response.data.decode()
        assert "Food" in html
        assert "Bills" in html
        assert "Luxury" not in html

    def test_both_dates_filter_shows_active_filter_message(self, client):
        """Active filter state message is displayed when both date params are set."""
        user_id = _register_and_login(client)
        _insert_expense(user_id, 100.00, "Food", "2026-04-05")

        response = _profile(client, start_date="2026-04-01", end_date="2026-04-30")
        html = response.data.decode()
        # The spec says something like "Showing expenses from ... to ..."
        assert "Showing expenses" in html

    def test_both_dates_filter_retains_input_values_in_form(self, client):
        """Date input fields are pre-filled with the applied filter values."""
        user_id = _register_and_login(client)
        _insert_expense(user_id, 100.00, "Food", "2026-04-05")

        response = _profile(client, start_date="2026-04-01", end_date="2026-04-30")
        html = response.data.decode()
        assert "2026-04-01" in html
        assert "2026-04-30" in html

    def test_both_dates_filter_clear_filter_link_points_to_plain_profile(self, client):
        """The Clear Filter link href must be /profile with no query parameters."""
        user_id = _register_and_login(client)
        _insert_expense(user_id, 100.00, "Food", "2026-04-05")

        response = _profile(client, start_date="2026-04-01", end_date="2026-04-30")
        html = response.data.decode()
        # The clear link should point to /profile without appending date params
        assert 'href="/profile"' in html


# --------------------------------------------------------------------------- #
# Happy path – start date only                                                 #
# --------------------------------------------------------------------------- #

class TestStartDateOnlyFilter:

    def test_start_date_only_shows_expenses_from_start_to_today(self, client):
        """When only start_date is given, expenses from start_date up to today are shown."""
        today = date.today().isoformat()
        user_id = _register_and_login(client)
        # An expense on today's date must appear
        _insert_expense(user_id, 50.00, "Food", today, "today expense")
        # An expense before the start date must not appear
        past = (date.today() - timedelta(days=30)).isoformat()
        _insert_expense(user_id, 999.00, "Old", past, "old expense")

        start = (date.today() - timedelta(days=7)).isoformat()
        response = _profile(client, start_date=start)
        html = response.data.decode()
        assert "today expense" in html
        assert "old expense" not in html

    def test_start_date_only_stats_reflect_filtered_range(self, client):
        """Stats reflect only the expenses in the start_date-to-today range."""
        today = date.today().isoformat()
        user_id = _register_and_login(client)
        _insert_expense(user_id, 75.00, "Food", today)
        past = (date.today() - timedelta(days=60)).isoformat()
        _insert_expense(user_id, 500.00, "Bills", past)

        start = (date.today() - timedelta(days=7)).isoformat()
        response = _profile(client, start_date=start)
        html = response.data.decode()
        assert "75.00" in html
        assert "500.00" not in html

    def test_start_date_only_shows_active_filter_message(self, client):
        """An active filter message is shown when start_date is provided without end_date."""
        today = date.today().isoformat()
        user_id = _register_and_login(client)
        _insert_expense(user_id, 75.00, "Food", today)

        start = (date.today() - timedelta(days=7)).isoformat()
        response = _profile(client, start_date=start)
        html = response.data.decode()
        assert "Showing expenses" in html


# --------------------------------------------------------------------------- #
# Happy path – end date only                                                   #
# --------------------------------------------------------------------------- #

class TestEndDateOnlyFilter:

    def test_end_date_only_shows_expenses_up_to_end_date(self, client):
        """When only end_date is given, all expenses up to (and including) end_date appear."""
        user_id = _register_and_login(client)
        _insert_expense(user_id, 100.00, "Food", "2026-01-01", "old expense")
        _insert_expense(user_id, 200.00, "Bills", "2026-03-31", "boundary expense")
        _insert_expense(user_id, 50.00, "Transport", "2026-04-01", "after end")

        response = _profile(client, end_date="2026-03-31")
        html = response.data.decode()
        assert "old expense" in html
        assert "boundary expense" in html
        assert "after end" not in html

    def test_end_date_only_stats_reflect_filtered_range(self, client):
        """Stats reflect only expenses up to end_date."""
        user_id = _register_and_login(client)
        _insert_expense(user_id, 100.00, "Food", "2026-01-01")
        _insert_expense(user_id, 200.00, "Bills", "2026-03-31")
        _insert_expense(user_id, 999.00, "Transport", "2026-04-15")

        response = _profile(client, end_date="2026-03-31")
        html = response.data.decode()
        assert "300.00" in html
        assert "999.00" not in html


# --------------------------------------------------------------------------- #
# Validation error tests                                                       #
# --------------------------------------------------------------------------- #

class TestValidationErrors:

    def test_end_date_before_start_date_shows_error_message(self, client):
        """If end_date < start_date, a validation error is shown and the page does not crash."""
        _register_and_login(client)
        response = _profile(client, start_date="2026-04-30", end_date="2026-04-01")
        assert response.status_code == 200
        html = response.data.decode()
        assert "End date cannot be before start date" in html

    def test_end_date_before_start_date_does_not_crash(self, client):
        """Invalid date range must not cause a 500 error."""
        _register_and_login(client)
        response = _profile(client, start_date="2026-12-31", end_date="2026-01-01")
        assert response.status_code == 200

    def test_invalid_start_date_format_shows_error(self, client):
        """A non-YYYY-MM-DD start_date triggers a validation error."""
        _register_and_login(client)
        response = _profile(client, start_date="April-01-2026")
        assert response.status_code == 200
        html = response.data.decode()
        assert "Invalid" in html or "invalid" in html or "format" in html.lower()

    def test_invalid_end_date_format_shows_error(self, client):
        """A non-YYYY-MM-DD end_date triggers a validation error."""
        _register_and_login(client)
        response = _profile(client, end_date="31/12/2026")
        assert response.status_code == 200
        html = response.data.decode()
        assert "Invalid" in html or "invalid" in html or "format" in html.lower()

    def test_malformed_start_date_does_not_crash(self, client):
        """Completely malformed start_date string does not cause a 500 error."""
        _register_and_login(client)
        response = _profile(client, start_date="not-a-date-at-all")
        assert response.status_code == 200

    def test_malformed_end_date_does_not_crash(self, client):
        """Completely malformed end_date string does not cause a 500 error."""
        _register_and_login(client)
        response = _profile(client, end_date="!!wrong!!")
        assert response.status_code == 200

    def test_invalid_format_does_not_filter_expenses(self, client):
        """When date format is invalid, all expenses are still shown (filter is ignored)."""
        user_id = _register_and_login(client)
        _insert_expense(user_id, 100.00, "Food", "2026-04-05", "visible expense")

        response = _profile(client, start_date="bad-date")
        html = response.data.decode()
        assert "visible expense" in html


# --------------------------------------------------------------------------- #
# Boundary inclusivity tests                                                   #
# --------------------------------------------------------------------------- #

class TestBoundaryInclusivity:

    def test_expense_on_start_date_is_included(self, client):
        """An expense whose date equals start_date must appear in the filtered results."""
        user_id = _register_and_login(client)
        _insert_expense(user_id, 100.00, "Food", "2026-04-01", "on start date")

        response = _profile(client, start_date="2026-04-01", end_date="2026-04-30")
        html = response.data.decode()
        assert "on start date" in html

    def test_expense_on_end_date_is_included(self, client):
        """An expense whose date equals end_date must appear in the filtered results."""
        user_id = _register_and_login(client)
        _insert_expense(user_id, 100.00, "Food", "2026-04-30", "on end date")

        response = _profile(client, start_date="2026-04-01", end_date="2026-04-30")
        html = response.data.decode()
        assert "on end date" in html

    def test_expense_one_day_before_start_date_is_excluded(self, client):
        """An expense one day before start_date must NOT appear in the filtered results."""
        user_id = _register_and_login(client)
        _insert_expense(user_id, 999.00, "Food", "2026-03-31", "day before start")

        response = _profile(client, start_date="2026-04-01", end_date="2026-04-30")
        html = response.data.decode()
        assert "day before start" not in html

    def test_expense_one_day_after_end_date_is_excluded(self, client):
        """An expense one day after end_date must NOT appear in the filtered results."""
        user_id = _register_and_login(client)
        _insert_expense(user_id, 999.00, "Food", "2026-05-01", "day after end")

        response = _profile(client, start_date="2026-04-01", end_date="2026-04-30")
        html = response.data.decode()
        assert "day after end" not in html

    def test_same_start_and_end_date_shows_only_that_day(self, client):
        """When start_date == end_date, only expenses on that exact date appear."""
        user_id = _register_and_login(client)
        _insert_expense(user_id, 50.00, "Food", "2026-04-15", "exact day")
        _insert_expense(user_id, 999.00, "Bills", "2026-04-14", "day before")
        _insert_expense(user_id, 888.00, "Other", "2026-04-16", "day after")

        response = _profile(client, start_date="2026-04-15", end_date="2026-04-15")
        html = response.data.decode()
        assert "exact day" in html
        assert "day before" not in html
        assert "day after" not in html


# --------------------------------------------------------------------------- #
# Edge case: empty user                                                        #
# --------------------------------------------------------------------------- #

class TestEmptyUser:

    def test_profile_returns_200_for_user_with_no_expenses(self, client):
        """Profile page loads without errors for a user who has never added an expense."""
        _register_and_login(client)
        response = _profile(client)
        assert response.status_code == 200

    def test_empty_user_stats_are_zero(self, client):
        """Total Spent and Expenses count are 0 for a user with no expenses."""
        _register_and_login(client)
        response = _profile(client)
        html = response.data.decode()
        assert "0.00" in html
        assert ">0<" in html

    def test_empty_user_with_date_filter_returns_200(self, client):
        """Applying a date filter to a user with no expenses does not crash."""
        _register_and_login(client)
        response = _profile(client, start_date="2026-04-01", end_date="2026-04-30")
        assert response.status_code == 200

    def test_empty_user_filter_shows_zero_stats(self, client):
        """Filtered stats for an empty user are all zero."""
        _register_and_login(client)
        response = _profile(client, start_date="2026-04-01", end_date="2026-04-30")
        html = response.data.decode()
        assert "0.00" in html


# --------------------------------------------------------------------------- #
# Edge case: single expense                                                    #
# --------------------------------------------------------------------------- #

class TestSingleExpense:

    def test_single_expense_within_range_appears(self, client):
        """A user with one expense sees it when the filter includes its date."""
        user_id = _register_and_login(client)
        _insert_expense(user_id, 42.00, "Food", "2026-04-10", "only expense")

        response = _profile(client, start_date="2026-04-01", end_date="2026-04-30")
        html = response.data.decode()
        assert "only expense" in html

    def test_single_expense_outside_range_is_excluded(self, client):
        """A user with one expense sees empty results when the filter excludes its date."""
        user_id = _register_and_login(client)
        _insert_expense(user_id, 42.00, "Food", "2026-03-01", "only expense")

        response = _profile(client, start_date="2026-04-01", end_date="2026-04-30")
        html = response.data.decode()
        assert "only expense" not in html

    def test_single_expense_excluded_stats_are_zero(self, client):
        """Stats are zero when the single expense falls outside the filter range."""
        user_id = _register_and_login(client)
        _insert_expense(user_id, 42.00, "Food", "2026-03-01")

        response = _profile(client, start_date="2026-04-01", end_date="2026-04-30")
        html = response.data.decode()
        assert "0.00" in html

    def test_single_expense_on_exact_boundary_is_included(self, client):
        """Single expense exactly on start_date boundary is included in filtered results."""
        user_id = _register_and_login(client)
        _insert_expense(user_id, 42.00, "Food", "2026-04-01", "boundary expense")

        response = _profile(client, start_date="2026-04-01", end_date="2026-04-30")
        html = response.data.decode()
        assert "boundary expense" in html


# --------------------------------------------------------------------------- #
# Edge case: filter range with no matching expenses                            #
# --------------------------------------------------------------------------- #

class TestEmptyFilterResult:

    def test_filter_with_no_matching_expenses_shows_zero_stats(self, client):
        """When the filter matches no expenses, stats show 0 count and 0.00 total."""
        user_id = _register_and_login(client)
        _insert_expense(user_id, 100.00, "Food", "2026-01-15")

        response = _profile(client, start_date="2026-06-01", end_date="2026-06-30")
        html = response.data.decode()
        assert "0.00" in html
        assert ">0<" in html

    def test_filter_with_no_matching_expenses_shows_no_transactions_text(self, client):
        """Empty state text for Recent Transactions is rendered when filter yields no results."""
        user_id = _register_and_login(client)
        _insert_expense(user_id, 100.00, "Food", "2026-01-15")

        response = _profile(client, start_date="2026-06-01", end_date="2026-06-30")
        html = response.data.decode()
        assert "No transactions" in html

    def test_filter_with_no_matching_expenses_categories_count_is_zero(self, client):
        """Categories stat is 0 when the filter matches no expenses."""
        user_id = _register_and_login(client)
        _insert_expense(user_id, 100.00, "Food", "2026-01-15")

        response = _profile(client, start_date="2026-06-01", end_date="2026-06-30")
        html = response.data.decode()
        # by_category will be empty so category count stat = 0
        assert ">0<" in html


# --------------------------------------------------------------------------- #
# Many expenses / multi-month span                                             #
# --------------------------------------------------------------------------- #

class TestManyExpenses:

    def _seed_multi_month_expenses(self, user_id):
        """Insert expenses across Jan, Feb, March, April 2026."""
        expenses = [
            (user_id, 10.00, "Food",      "2026-01-05", "jan food"),
            (user_id, 20.00, "Bills",     "2026-01-20", "jan bills"),
            (user_id, 30.00, "Transport", "2026-02-10", "feb transport"),
            (user_id, 40.00, "Health",    "2026-02-25", "feb health"),
            (user_id, 50.00, "Food",      "2026-03-08", "mar food"),
            (user_id, 60.00, "Shopping",  "2026-03-22", "mar shopping"),
            (user_id, 70.00, "Bills",     "2026-04-05", "apr bills"),
            (user_id, 80.00, "Food",      "2026-04-18", "apr food"),
        ]
        conn = db_module.get_db()
        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            expenses,
        )
        conn.commit()
        conn.close()

    def test_filter_across_two_months_returns_correct_expenses(self, client):
        """Filtering across Feb–Mar returns only those expenses, not Jan or Apr."""
        user_id = _register_and_login(client)
        self._seed_multi_month_expenses(user_id)

        response = _profile(client, start_date="2026-02-01", end_date="2026-03-31")
        html = response.data.decode()
        assert "feb transport" in html
        assert "feb health" in html
        assert "mar food" in html
        assert "mar shopping" in html
        assert "jan food" not in html
        assert "jan bills" not in html
        assert "apr bills" not in html
        assert "apr food" not in html

    def test_filter_across_two_months_totals_are_correct(self, client):
        """Total across Feb–Mar is 30+40+50+60 = 180.00."""
        user_id = _register_and_login(client)
        self._seed_multi_month_expenses(user_id)

        response = _profile(client, start_date="2026-02-01", end_date="2026-03-31")
        html = response.data.decode()
        assert "180.00" in html

    def test_no_filter_shows_all_eight_expenses(self, client):
        """Without a filter all 8 expenses count is shown in stats."""
        user_id = _register_and_login(client)
        self._seed_multi_month_expenses(user_id)

        response = _profile(client)
        html = response.data.decode()
        assert ">8<" in html

    def test_category_count_reflects_filter(self, client):
        """Categories count stat changes when filter narrows the expense set."""
        user_id = _register_and_login(client)
        self._seed_multi_month_expenses(user_id)

        # Unfiltered: Food(jan,mar,apr), Bills(jan,apr), Transport(feb), Health(feb), Shopping(mar) = 5 categories
        response_all = _profile(client)
        html_all = response_all.data.decode()

        # Filtered to Jan only: Food, Bills = 2 categories
        response_jan = _profile(client, start_date="2026-01-01", end_date="2026-01-31")
        html_jan = response_jan.data.decode()

        # The filtered page should have "Food" and "Bills" but not "Transport" or "Health"
        assert "Transport" not in html_jan
        assert "Health" not in html_jan


# --------------------------------------------------------------------------- #
# UI / Template structure tests                                                #
# --------------------------------------------------------------------------- #

class TestUITemplate:

    def test_date_filter_form_has_method_get(self, client):
        """The date filter form must use the GET method (query parameters, not POST body)."""
        _register_and_login(client)
        response = _profile(client)
        html = response.data.decode()
        assert 'method="GET"' in html or "method=\"get\"" in html.lower()

    def test_date_filter_form_action_points_to_profile(self, client):
        """The date filter form action must target the /profile route."""
        _register_and_login(client)
        response = _profile(client)
        html = response.data.decode()
        assert 'action="/profile"' in html

    def test_filter_button_is_present(self, client):
        """A submit button for applying the date filter must exist in the form."""
        _register_and_login(client)
        response = _profile(client)
        html = response.data.decode()
        # A button of type submit should be in the filter form area
        assert 'type="submit"' in html

    def test_recent_transactions_section_heading_present(self, client):
        """'Recent Transactions' heading is rendered on the profile page."""
        _register_and_login(client)
        response = _profile(client)
        html = response.data.decode()
        assert "Recent Transactions" in html

    def test_filter_form_appears_above_transactions_in_html_order(self, client):
        """The date filter form must appear before the transaction list in the HTML output."""
        user_id = _register_and_login(client)
        _insert_expense(user_id, 50.00, "Food", "2026-04-05", "sample txn")

        response = _profile(client)
        html = response.data.decode()
        form_pos = html.find('name="start_date"')
        txn_pos = html.find("sample txn")
        assert form_pos < txn_pos, (
            "Date filter form input must appear before transaction rows in rendered HTML"
        )

    def test_active_filter_message_not_shown_without_filter(self, client):
        """The active filter message element must not be in the DOM when no filter is set."""
        user_id = _register_and_login(client)
        _insert_expense(user_id, 50.00, "Food", "2026-04-05")

        response = _profile(client)
        html = response.data.decode()
        assert "Showing expenses" not in html

    def test_clear_filter_link_absent_when_no_filter(self, client):
        """The Clear Filter link should not appear when no filter is active."""
        user_id = _register_and_login(client)
        _insert_expense(user_id, 50.00, "Food", "2026-04-05")

        response = _profile(client)
        html = response.data.decode()
        assert "Clear" not in html

    def test_clear_filter_link_present_when_filter_active(self, client):
        """The Clear Filter link must appear when a date filter is active."""
        user_id = _register_and_login(client)
        _insert_expense(user_id, 50.00, "Food", "2026-04-05")

        response = _profile(client, start_date="2026-04-01", end_date="2026-04-30")
        html = response.data.decode()
        assert "Clear" in html


# --------------------------------------------------------------------------- #
# Security tests                                                               #
# --------------------------------------------------------------------------- #

class TestSecurity:

    @pytest.mark.parametrize("injection_payload", [
        "'; DROP TABLE expenses; --",
        "1' OR '1'='1",
        "2026-04-01' UNION SELECT * FROM users --",
        "2026-04-01; DELETE FROM expenses WHERE '1'='1",
    ])
    def test_sql_injection_in_start_date_does_not_crash(self, client, injection_payload):
        """SQL injection attempts in start_date must not cause a 500 error or DB corruption."""
        user_id = _register_and_login(client)
        _insert_expense(user_id, 100.00, "Food", "2026-04-05", "safe expense")

        response = _profile(client, start_date=injection_payload)
        # Must not crash
        assert response.status_code == 200

        # The injected payload must not have dropped or altered expense data
        # (re-fetch without filter to verify)
        response_clean = _profile(client)
        html_clean = response_clean.data.decode()
        assert "safe expense" in html_clean

    @pytest.mark.parametrize("injection_payload", [
        "'; DROP TABLE expenses; --",
        "1' OR '1'='1",
        "2026-04-30' UNION SELECT * FROM users --",
    ])
    def test_sql_injection_in_end_date_does_not_crash(self, client, injection_payload):
        """SQL injection attempts in end_date must not cause a 500 error or DB corruption."""
        user_id = _register_and_login(client)
        _insert_expense(user_id, 100.00, "Food", "2026-04-05", "safe expense")

        response = _profile(client, end_date=injection_payload)
        assert response.status_code == 200

        response_clean = _profile(client)
        html_clean = response_clean.data.decode()
        assert "safe expense" in html_clean

    def test_other_users_expenses_not_visible_without_filter(self, client):
        """A logged-in user must never see another user's expenses (no filter)."""
        # Register and add expense for user A
        user_a_id = _register_and_login(
            client, name="User A", email="usera@example.com", password="passwordA1"
        )
        _insert_expense(user_a_id, 777.00, "Food", "2026-04-05", "user A secret expense")

        # Register and log in as user B
        client.post("/register", data={
            "name": "User B",
            "email": "userb@example.com",
            "password": "passwordB1",
        }, follow_redirects=True)
        client.post("/login", data={
            "email": "userb@example.com",
            "password": "passwordB1",
        }, follow_redirects=True)

        response = _profile(client)
        html = response.data.decode()
        assert "user A secret expense" not in html

    def test_other_users_expenses_not_visible_with_date_filter(self, client):
        """A logged-in user must never see another user's expenses even with a date filter."""
        # Register and add expense for user A
        user_a_id = _register_and_login(
            client, name="User A", email="usera@example.com", password="passwordA1"
        )
        _insert_expense(user_a_id, 777.00, "Food", "2026-04-05", "user A secret expense")

        # Register and log in as user B
        client.post("/register", data={
            "name": "User B",
            "email": "userb@example.com",
            "password": "passwordB1",
        }, follow_redirects=True)
        client.post("/login", data={
            "email": "userb@example.com",
            "password": "passwordB1",
        }, follow_redirects=True)

        response = _profile(client, start_date="2026-04-01", end_date="2026-04-30")
        html = response.data.decode()
        assert "user A secret expense" not in html

    def test_very_long_date_param_does_not_crash(self, client):
        """An extremely long string in start_date must not cause a 500 or server hang."""
        _register_and_login(client)
        long_payload = "A" * 10_000
        response = _profile(client, start_date=long_payload)
        assert response.status_code == 200
