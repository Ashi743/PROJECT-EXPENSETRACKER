# Spec: Profile Page Backend Routes

## Overview
This step implements five essential backend routes that support the profile page functionality and expense management. These routes enable users to view their profile, update their account information, and manage their expenses (add, edit, delete). These routes transform the static profile display from Step 04 into a fully functional backend that powers both the profile page and future expense management features.

## Depends on
- Step 01: Database Setup — users and expenses tables must exist
- Step 02: Registration — user accounts must exist with validated data
- Step 03: Login and Logout — session management must be in place for route protection
- Step 04: Profile Page Design — profile page template exists to consume these routes

## Routes
- `GET /profile` — display logged-in user's profile page with account info and expense summary — logged-in only
- `POST /profile` — update logged-in user's profile information (name, email, password) — logged-in only
- `GET /expenses` — retrieve list of all expenses for logged-in user (JSON API endpoint) — logged-in only
- `POST /expenses` — create a new expense for logged-in user — logged-in only
- `DELETE /expenses/<int:id>` — delete an expense belonging to logged-in user — logged-in only

## Database changes
No database changes. The users and expenses tables already have all required columns:
- users table: id, name, email, password_hash, created_at
- expenses table: id, user_id, amount, category, date, description, created_at

## Templates
No new templates required. The existing profile.html template will be used with the routes above.

## Files to change
- `app.py` — add/update POST /profile, GET /expenses, POST /expenses, and DELETE /expenses/<id> routes; ensure all route handlers authenticate users and validate input
- `database/db.py` — no changes needed (existing schema is sufficient)

## New dependencies
No new dependencies. Flask and sqlite3 are already available.

## Rules for implementation
- No SQLAlchemy or ORMs — raw sqlite3 only
- Parameterized queries only — never use string formatting in SQL
- Passwords hashed with Werkzeug: `generate_password_hash()`
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- All protected routes must check `session.get("user_id")` and redirect to login if not authenticated
- POST /profile must validate email uniqueness (except for current user's email)
- POST /profile must validate new password is at least 8 characters if provided
- POST /expenses must validate: amount > 0, category is not empty, date is valid format (YYYY-MM-DD)
- DELETE /expenses/<id> must verify the expense belongs to the logged-in user before deletion
- GET /expenses must return JSON with proper Content-Type header
- All responses should handle edge cases gracefully (user deleted, expense not found, etc.)
- All SQL queries use `?` placeholders with tuple parameters — no string concatenation in SQL

## Definition of done
- [ ] GET /profile displays logged-in user's profile page (from Step 04)
- [ ] POST /profile accepts name, email, and password fields; updates user record on success
- [ ] POST /profile validates email uniqueness and shows error if email already exists (for other users)
- [ ] POST /profile validates password length (minimum 8 characters) if password field is provided
- [ ] POST /profile redirects to /profile on success with confirmation message
- [ ] POST /profile shows validation errors without losing user input
- [ ] GET /expenses returns JSON array of all user's expenses with proper headers
- [ ] POST /expenses accepts amount, category, date, and description; creates new expense
- [ ] POST /expenses validates amount > 0, category not empty, date is valid
- [ ] POST /expenses returns JSON response with created expense data on success
- [ ] POST /expenses shows validation errors in JSON format
- [ ] DELETE /expenses/<id> deletes the expense only if it belongs to logged-in user
- [ ] DELETE /expenses/<id> returns 404 if expense not found or doesn't belong to user
- [ ] DELETE /expenses/<id> returns JSON success response after deletion
- [ ] All protected routes redirect to /login if user is not authenticated
- [ ] All routes handle edge cases: user deleted mid-session, invalid IDs, concurrent updates
- [ ] All queries use `?` placeholders (no SQL injection vulnerabilities)
- [ ] App starts without errors after implementation
