# Spec: Registration (Step 02)

## Overview
Registration enables new users to create a Spendly account by submitting their name, email, and password. The POST handler validates input, hashes the password with Werkzeug, and inserts the user into the database. Duplicate emails are rejected with a friendly error. On success, the user is redirected to /login. This is the entry point of the authentication flow and must work before login (Step 03) can be implemented.

## Depends on
- Step 01: Database Setup — users table with email UNIQUE constraint must exist

## Routes
- **GET /register** — Display registration form — public
- **POST /register** — Process form submission, validate, insert user — public

## Input Validation Rules

**name:**
- Non-empty after strip()
- Max length: 100 characters
- Allowed: letters, spaces, hyphens, apostrophes

**email:**
- Non-empty after strip()
- Must contain @ symbol
- Max length: 255 characters

**password:**
- Minimum 8 characters
- No maximum length requirement
- All characters allowed

## Error Messages

| Scenario | Message |
|----------|---------|
| Empty name | "Name is required." |
| Empty email | "Email is required." |
| Empty password | "Password is required." |
| Invalid email (no @) | "Please enter a valid email address." |
| Password < 8 chars | "Password must be at least 8 characters." |
| Duplicate email | "An account with this email already exists." |

## Database
- Table: `users` (from Step 01)
- Columns: id, name, email (UNIQUE), password_hash, created_at
- No new columns needed

## Template
- Modify: `templates/register.html` — ensure `{{ error }}` displays validation errors

## Files to Change
- `app.py` — split `/register` into GET and POST handlers; add validation and insert logic

## New Dependencies
None. Already available:
- `werkzeug.security.generate_password_hash`
- `flask.request`, `flask.redirect`, `flask.url_for`

## Implementation Rules
- Raw sqlite3 only — no SQLAlchemy
- Parameterized queries: use `?` placeholders, never string formatting
- Password hashing: `generate_password_hash(password)`
- On duplicate email (IntegrityError): show error message (no crash)
- On success: redirect to `/login` (HTTP 302)
- Use CSS variables — no hardcoded hex values
- All templates extend base.html

## Success Flow
1. User submits valid registration form
2. Backend validates all inputs
3. Password is hashed with `generate_password_hash()`
4. User inserted into database
5. Redirect to GET /login

## Definition of Done
- [ ] GET /register displays registration form
- [ ] POST /register with valid data creates user in database
- [ ] Password stored as hash (not plaintext)
- [ ] Duplicate email shows error (no crash)
- [ ] Empty fields show validation error
- [ ] Password < 8 chars shows validation error
- [ ] Success redirects to /login
- [ ] All queries use `?` placeholders (no SQL injection)
- [ ] App starts without errors