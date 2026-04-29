# Spec: Login and Logout

## Overview
This step implements user authentication with login and logout functionality. Users can sign in with their email and password, maintain a session, and sign out. This is essential for the expense tracker, as it enables per-user expense tracking and account security. Login comes after registration (Step 2) and enables protected routes for profile and expense management in later steps.

## Depends on
- Step 01: Database Setup — users table must exist with id, email (UNIQUE), password_hash, and created_at columns
- Step 02: Registration — users must be able to create accounts before they can log in

## Routes
- `GET /login` — display login form — public
- `POST /login` — accept email and password, verify against database, establish session on success — public
- `GET /logout` — destroy session and redirect to landing page — any user (logged-in or not)

## Database changes
No database changes. The users table already exists with the necessary id, email (UNIQUE), password_hash, and created_at columns.

## Templates
- **Create:** 
  - `templates/login.html` — login form with email and password fields, error display
- **Modify:**
  - `templates/base.html` — replace hardcoded nav links with session-aware conditional navigation
  - `templates/landing.html` — (no changes required if link already exists)

## Files to change
- `app.py` — add session and check_password_hash imports; set app.secret_key; implement GET /login; implement POST /login with password verification and session management; implement GET /logout with session cleanup
- `templates/login.html` — create new template with login form
- `templates/base.html` — replace hardcoded navigation with conditional display based on session.user_id

## New dependencies
No new dependencies. Flask session management and Werkzeug are already available.

## Rules for implementation
- No SQLAlchemy or ORMs — raw sqlite3 only
- Parameterized queries only — never use string formatting in SQL
- Passwords verified with Werkzeug: `check_password_hash()`
- Use Flask's `session` object for storing user_id after successful login
- All templates extend `base.html`
- Set `app.secret_key` in `app.py` to a secure random value for session encryption: `app.secret_key = "dev-only-32-char-hex-key-12345678"`
- Sessions must clear all user data on logout with `session.clear()`
- Login form must validate email and password are provided before querying database
- Password verification must not reveal whether email exists or password is wrong (use generic "Invalid email or password." message for both cases — prevents user enumeration)
- Always use `try/finally` with `conn.close()` when querying database (matches existing register route pattern)
- Error rendering: `return render_template("login.html", error="...")`
- Redirect on success: `return redirect(url_for("landing"))`

## Implementation Details

### app.py Changes

**Imports (lines 2–3) — add to existing imports:**
```python
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
```

**Secret key (after `app = Flask(__name__)`):**
```python
app.secret_key = "dev-only-32-char-hex-key-12345678"  # Change in production
```

**GET /login handler:**
```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    # POST handler follows below
```

**POST /login handler:**
```python
    # GET handler above...
    
    # POST: Handle login form submission
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    
    # 1. Validate both fields present
    if not email or not password:
        return render_template('login.html', error="Email and password are required.")
    
    # 2. Query database
    conn = get_db()
    try:
        user = conn.execute(
            "SELECT id, password_hash FROM users WHERE email = ?",
            (email,)
        ).fetchone()
        
        # 3. Check password (same error for both cases — no user enumeration)
        if user is None or not check_password_hash(user['password_hash'], password):
            return render_template('login.html', error="Invalid email or password.")
        
        # 4. Set session and redirect
        session['user_id'] = user['id']
        return redirect(url_for('landing'))
    finally:
        conn.close()
```

**GET /logout handler (replace existing stub):**
```python
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landing'))
```

### templates/base.html Changes

Replace hardcoded nav links with session-aware conditional:

```html
<!-- OLD (remove these lines): -->
<a href="{{ url_for('login') }}" class="nav-link">Sign in</a>
<a href="{{ url_for('register') }}" class="nav-link nav-cta">Get started</a>

<!-- NEW (replace with): -->
{% if session.user_id %}
  <a href="{{ url_for('logout') }}" class="nav-link">Sign out</a>
{% else %}
  <a href="{{ url_for('login') }}" class="nav-link">Sign in</a>
  <a href="{{ url_for('register') }}" class="nav-link nav-cta">Get started</a>
{% endif %}
```

**Notes:**
- `session` object is automatically available in Jinja2 templates (no extra imports needed)
- `session.user_id` exists only after successful login
- If session is empty, the `if` evaluates safely to False

### templates/login.html Creation

Create new file `templates/login.html` extending base.html:

```html
{% extends "base.html" %}

{% block content %}
<div class="auth-container">
  <h1>Sign In</h1>
  
  {% if error %}
    <div class="auth-error">{{ error }}</div>
  {% endif %}
  
  <form method="POST" action="{{ url_for('login') }}" class="auth-form">
    <div class="form-group">
      <label for="email">Email</label>
      <input type="email" id="email" name="email" required>
    </div>
    
    <div class="form-group">
      <label for="password">Password</label>
      <input type="password" id="password" name="password" required>
    </div>
    
    <button type="submit" class="btn btn-primary">Sign In</button>
  </form>
  
  <p>Don't have an account? <a href="{{ url_for('register') }}">Create one</a></p>
</div>
{% endblock %}
```

## Implementation Order

1. Update imports in app.py (`session`, `check_password_hash`)
2. Set `app.secret_key` in app.py
3. Implement GET `/login` handler in app.py
4. Implement POST `/login` handler in app.py
5. Implement `/logout` handler in app.py
6. Create `templates/login.html`
7. Update `templates/base.html` nav with session conditional

## Patterns to Follow

From existing registration code:
- Error rendering: `return render_template("login.html", error="...")`
- DB pattern: `conn = get_db()` → query → `finally: conn.close()`
- Redirect on success: `return redirect(url_for("..."))`
- SQL: Always `?` placeholders, never f-strings or `.format()`

## Session Configuration

Flask uses secure cookies by default:
- Session data stored client-side (encrypted cookie)
- Signed with `app.secret_key` (cannot be tampered with)
- No additional configuration needed beyond setting secret_key

## Verification

1. `python app.py` — app starts with no errors
2. Visit GET `/login` → login form renders with email and password fields
3. Submit login form with registered user's correct credentials → redirects to landing, nav shows "Sign out"
4. Click "Sign out" → session cleared, redirects to landing, nav shows "Sign in / Get started"
5. Visit GET `/login` with invalid credentials → same page renders, error shows "Invalid email or password."
6. Submit empty email or password → same page renders, error shows "Email and password are required."
7. Visit `/login` while already logged in → still works (no guard required at this stage)
8. Check browser cookies → session cookie is set with secure defaults
9. Verify page source — no SQL strings visible, no sensitive data leaked to HTML

## Security Checklist

- [ ] `app.secret_key` is set (session will crash without it)
- [ ] `check_password_hash()` used for verification (not string comparison)
- [ ] Same error message for invalid email and wrong password (no user enumeration)
- [ ] All SQL uses `?` placeholders (no SQL injection possible)
- [ ] `session.clear()` fully clears all user data on logout
- [ ] Session cookie set securely by Flask (automatic)
- [ ] Email stripped of whitespace before validation/query
- [ ] `conn.close()` always called in `finally` block
- [ ] `session['user_id']` set only after successful password verification

## Definition of done
- [ ] GET `/login` displays login form with email and password fields
- [ ] POST `/login` with valid credentials establishes session and redirects to landing
- [ ] POST `/login` with invalid email shows "Invalid email or password." error
- [ ] POST `/login` with wrong password shows "Invalid email or password." error (same message)
- [ ] POST `/login` with empty fields shows "Email and password are required." error
- [ ] GET `/logout` clears session and redirects to landing page
- [ ] Navigation shows "Sign out" when logged in
- [ ] Navigation shows "Sign in" and "Get started" when not logged in
- [ ] No SQL injection vulnerabilities — all queries use `?` placeholders
- [ ] Password verification uses `check_password_hash()` from Werkzeug
- [ ] `app.secret_key` is set to enable session encryption
- [ ] App starts without errors after implementation
- [ ] Session persists across page navigation when logged in
- [ ] Session clears completely on logout (user_id no longer accessible)