# Spec: Add Expense Via Frontend

## Overview
This step implements the frontend form and backend route to allow logged-in users to create new expenses. Users can input an expense amount, select a category, choose a date, and optionally provide a description. Once submitted, the expense is saved to the database and the user is redirected to their profile page. This feature is essential for core app functionality and builds directly on the database and authentication work from previous steps.

## Depends on
- Step 01: Database Setup — expenses table must exist with required columns
- Step 02: Registration — user accounts must exist
- Step 03: Login and Logout — session management and authentication required
- Step 05: Profile Page Routes — GET /profile route must exist to redirect user after adding expense

## Routes
- `GET /expenses/add` — display form to create a new expense — logged-in only
- `POST /expenses/add` — process form submission, insert expense into database, redirect to profile — logged-in only

## Database changes
No database changes. The expenses table already has all required columns (user_id, amount, category, date, description).

## Templates
- **Create:**
  - `templates/add_expense.html` — form with fields for amount, category dropdown, date, and description; extends `base.html`
- **Modify:**
  - `templates/base.html` — add link to "Add Expense" in navigation (if not already present)
  - `templates/profile.html` — add "Add Expense" button near recent transactions section (optional but recommended for UX)

## Files to change
- `app.py` — implement GET /expenses/add to render form and POST /expenses/add to handle submission
- `templates/add_expense.html` — create new form template with proper validation messages
- `templates/base.html` — add navigation link to add expense route (if needed)

## New dependencies
No new dependencies. Flask, sqlite3, and Werkzeug are already available.

## Rules for implementation
- No SQLAlchemy or ORMs — raw sqlite3 only
- Parameterized queries only — never use string formatting in SQL
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Route must check `session.get("user_id")` and redirect to login if not authenticated
- Amount must be a positive number (greater than 0); validate on form submission
- Amount must be a valid decimal/float; reject non-numeric input
- Category must be selected from a predefined list: Food, Transport, Bills, Health, Entertainment, Shopping, Other
- Date must be in YYYY-MM-DD format (HTML5 date input)
- Date cannot be in the future; show validation error if user selects future date
- Description is optional; limit to 500 characters if provided
- After successful insert, redirect to `/profile` (not `/profile` with query params)
- If form submission fails validation, re-render the form with error messages and preserve user input
- All SQL queries use `?` placeholders with tuple parameters
- Success message should indicate expense was added (can be session flash message or simple redirect with implicit success)

## Definition of done
- [ ] GET /expenses/add renders a form with amount, category, date, and description fields
- [ ] Form extends base.html and includes proper styling using CSS variables
- [ ] Amount field validates that input is numeric and greater than 0
- [ ] Category dropdown includes all valid categories: Food, Transport, Bills, Health, Entertainment, Shopping, Other
- [ ] Date field uses HTML5 date input and prevents future dates
- [ ] Description field is optional and limits input to 500 characters
- [ ] POST /expenses/add inserts new expense with correct user_id into database
- [ ] On successful insert, redirect to /profile (GET)
- [ ] If validation fails, re-render form with error messages and preserve user input
- [ ] If date is in the future, show error "Date cannot be in the future"
- [ ] If amount is zero or negative, show error "Amount must be greater than 0"
- [ ] If category is not selected, show error "Please select a category"
- [ ] If amount is not numeric, show error "Please enter a valid amount"
- [ ] Session check: if user not logged in, redirect to /login
- [ ] All database queries use `?` placeholders (no SQL injection vulnerabilities)
- [ ] New expenses appear immediately on profile page after redirect
- [ ] Feature works with single expenses and multiple expenses in succession
- [ ] App starts without errors after implementation
