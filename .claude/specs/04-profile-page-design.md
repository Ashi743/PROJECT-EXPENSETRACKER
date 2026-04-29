# Spec: Profile Page Design

## Overview
This step implements a user profile page that displays account information and expense statistics. The profile page shows the logged-in user's name, email, account creation date, and a summary of their expenses (total amount spent, expense count by category). This page is essential for users to manage their account and view their spending overview. It comes after login (Step 3) and enables personal data management in the Spendly app.

## Depends on
- Step 01: Database Setup — users and expenses tables must exist
- Step 02: Registration — users must be able to create accounts
- Step 03: Login and Logout — session management must be in place for route protection

## Routes
- `GET /profile` — display logged-in user's profile page with account info and expense summary — logged-in only

## Database changes
No database changes. The users and expenses tables already exist with the necessary columns.

## Templates
- **Create:**
  - `templates/profile.html` — user profile page with account information and expense statistics
- **Modify:**
  - `templates/base.html` — add navigation link to profile page (visible only when logged in)

## Files to change
- `app.py` — implement GET /profile route with login requirement; fetch user data and expense statistics; render profile template
- `templates/profile.html` — create new template displaying user info and expense summary
- `templates/base.html` — add profile navigation link in session-aware conditional navigation

## New dependencies
No new dependencies. Flask and sqlite3 are already available.

## Rules for implementation
- No SQLAlchemy or ORMs — raw sqlite3 only
- Parameterized queries only — never use string formatting in SQL
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Route must check `session.get("user_id")` and redirect to login if not authenticated
- Profile page must display logged-in user's information only (no access to other users' profiles)
- Use `datetime` module if needed to format created_at dates
- Error handling: if user is deleted (edge case), handle gracefully with redirect to logout
- All SQL queries use `?` placeholders with tuple parameters

## Definition of done
- [ ] GET /profile redirects to login if user is not logged in
- [ ] GET /profile displays logged-in user's name, email, and account creation date
- [ ] Profile page shows expense statistics (total amount spent, count of expenses, count by category)
- [ ] Profile navigation link is visible in header only when user is logged in
- [ ] Profile page layout is clean and readable with proper CSS styling
- [ ] All queries use `?` placeholders (no SQL injection)
- [ ] Created_at date is formatted in a readable way (e.g., "April 29, 2026")
- [ ] App starts without errors after implementation
- [ ] Page displays correctly for user with expenses and for user with no expenses
- [ ] User can navigate back to landing page or other sections from profile
