---
description   : Create a spec file and feature branch for the next Spendly step
argument-hint : "step number and feature name e.g. 2 registration"
allowed-tools : Read, Write, Glob, Bash(git:*)
---

You are a senior developer planning a new feature for the Spendly expense tracker. Always follow the rules in CLAUDE.md.

User input: $ARGUMENTS

## Step 1 — Parse Arguments

From $ARGUMENTS extract:
- `step_number`   — zero-padded to 2 digits (2 → 02, 11 → 11)
- `feature_title` — human readable Title Case (e.g. "Registration", "Login and Logout")
- `feature_slug`  — lowercase kebab-case, only a-z/0-9/-, max 40 chars (e.g. "registration", "login-logout")

If any cannot be inferred, ask the user to clarify before proceeding.

## Step 2 — Prepare the Branch

### 2a — Switch to main and pull latest

```bash
git checkout main
git pull origin main
```

If `git pull` fails, notify the user and stop. Do not proceed until main is up to date.

### 2b — Determine branch name

Base branch name: `feature/<feature_slug>`
Example: `feature/registration`

Check if branch already exists:
```bash
git branch --list "feature/<feature_slug>"
```

- If branch does **not** exist → use `feature/<feature_slug>`
- If branch **exists** → append incrementing number starting at 01:
  - Check `feature/<feature_slug>-01`
  - Check `feature/<feature_slug>-02`
  - Continue until a free name is found

```bash
git branch --list "feature/<feature_slug>-01"
git branch --list "feature/<feature_slug>-02"
```

Example:
feature/registration       ← taken
feature/registration-01    ← taken
feature/registration-02    ← free → use this

### 2c — Create and switch to branch

```bash
git checkout -b <resolved_branch_name>
```

Confirm to user:
✓ Switched to branch: <resolved_branch_name>

## Step 3 — Research the Codebase

Read these files before writing the spec:
- `CLAUDE.md`       — roadmap, conventions, rules, schema
- `app.py`          — existing routes and application structure
- `database/db.py`  — existing schema, tables, and helper functions
- `.claude/specs/`  — all existing specs to avoid duplicating routes, tables, or logic

## Step 4 — Write the Spec

Generate a spec document with this exact structure:

---

# Spec: <feature_title>

## Overview
One paragraph describing what this feature does and why it exists at this stage of the Spendly roadmap.

## Depends on
Which previous steps must be complete before this can be implemented.
Example:
- Step 01: Database Setup — users table must exist
- Step 02: Registration — user must be able to create an account

## Routes
Every new route needed:
- `METHOD /path` — description — access level (public / logged-in)

If no new routes: state "No new routes."

## Database changes
Any new tables, columns, or constraints needed.
Always verify against `database/db.py` before writing this section.

If none: state "No database changes."

## Templates
- **Create:** list every new template with its full path
- **Modify:** list every existing template and describe what changes

## Files to change
Every file that will be created or modified during implementation.
- `app.py`              — describe what changes
- `database/db.py`      — describe what changes (if any)
- `templates/xyz.html`  — describe what changes

## New dependencies
Any new pip packages required.
If none: state "No new dependencies."

## Rules for implementation
Specific constraints Claude must follow during implementation.
Always include:
- No SQLAlchemy or ORMs — raw sqlite3 only
- Parameterized queries only — never use string formatting in SQL
- Passwords hashed with Werkzeug: `generate_password_hash()`
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`

Add any feature-specific rules below the defaults.

## Definition of done
A specific, testable checklist. Each item must be verifiable by running the app.
- [ ] Happy path works end to end
- [ ] Validation errors show correctly on form
- [ ] Duplicate/invalid data handled gracefully with no crash
- [ ] Redirects go to the correct route on success
- [ ] All queries use `?` placeholders (no SQL injection)
- [ ] App starts without errors after implementation

---

## Step 5 — Save the Spec

Save the spec to:
.claude/specs/<step_number>-<feature_slug>.md

Create the `.claude/specs/` directory if it does not already exist.

## Step 6 — Report to User

Print this exact format:
Spec file : .claude/specs/<step_number>-<feature_slug>.md
Branch    : <resolved_branch_name>
Title     : <feature_title>

Then tell the user:
"Review the spec at `.claude/specs/<step_number>-<feature_slug>.md`
then enter Plan mode with Shift+Tab twice to begin implementation."

Do not print the full spec in chat unless explicitly asked.