# Spec: Date Filter for Profile Page

## Overview
This step adds date range filtering functionality to the profile page, allowing users to view their recent transactions and category breakdown for a specific time period. Users can select a start date and end date to filter the displayed expenses. When no date filter is applied, all expenses are shown. This feature enables users to analyze their spending patterns across different time periods and is a direct enhancement to the profile page completed in Step 04.

## Depends on
- Step 01: Database Setup — expenses table must exist
- Step 02: Registration — user accounts must exist
- Step 03: Login and Logout — session management must be in place
- Step 04: Profile Page Design — profile page template and basic display must exist
- Step 05: Profile Page Routes — GET /profile route must fetch and display expenses

## Routes
- `GET /profile` — display logged-in user's profile page with optional date range filters (query parameters: `start_date` and `end_date` in YYYY-MM-DD format) — logged-in only

If no `start_date` or `end_date` provided, display all expenses (current behavior).

## Database changes
No database changes. The expenses table already has the `date` column required for filtering.

## Templates
- **Modify:**
  - `templates/profile.html` — add date range filter inputs (start date and end date) above the Recent Transactions section; add a "Clear Filter" button to reset to all expenses

## Files to change
- `app.py` — modify GET /profile route to accept optional `start_date` and `end_date` query parameters; filter recent expenses and category breakdown queries based on these dates; pass filter state to template
- `templates/profile.html` — add form with date input fields for start and end date; display active filter state (if any) with a "Clear Filter" button

## New dependencies
No new dependencies. Flask and sqlite3 are already available.

## Rules for implementation
- No SQLAlchemy or ORMs — raw sqlite3 only
- Parameterized queries only — never use string formatting in SQL
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Route must check `session.get("user_id")` and redirect to login if not authenticated
- Date inputs must accept YYYY-MM-DD format
- If `start_date` is provided without `end_date`, filter from start_date to today
- If `end_date` is provided without `start_date`, filter from earliest expense to end_date
- If both dates are provided, filter between them (inclusive on both ends)
- Validate that `end_date` is not before `start_date` (if both provided); show error if invalid
- When a filter is active, show the active filter state on the page (e.g., "Showing expenses from April 1 to April 15, 2026")
- Clear Filter button should redirect to `/profile` without query parameters
- All SQL queries use `?` placeholders with tuple parameters
- Date comparison in SQL: use BETWEEN for efficiency, e.g., `date BETWEEN ? AND ?`

## Definition of done
- [ ] GET /profile accepts optional `start_date` and `end_date` query parameters in YYYY-MM-DD format
- [ ] Recent Transactions are filtered by date range when both dates are provided
- [ ] Category breakdown is filtered by date range when both dates are provided
- [ ] If only `start_date` is provided, expenses from start_date to today (inclusive) are shown
- [ ] If only `end_date` is provided, all expenses up to end_date (inclusive) are shown
- [ ] Profile header stats (Total Spent, Expenses, Categories) are updated based on filtered results
- [ ] If `end_date` is before `start_date`, show validation error without crashing
- [ ] Date filter form displays in profile page above Recent Transactions section
- [ ] Active filter state is displayed to user (e.g., "Filtering: April 1 – April 15, 2026")
- [ ] Clear Filter button removes date parameters and displays all expenses
- [ ] When no filter is active, filter form shows empty/placeholder date inputs
- [ ] Date inputs retain their values when filter is applied
- [ ] All queries use `?` placeholders (no SQL injection vulnerabilities)
- [ ] Feature works with users who have no expenses (empty state)
- [ ] Feature works with users who have one expense
- [ ] Feature works with users who have many expenses spanning multiple months
- [ ] App starts without errors after implementation
