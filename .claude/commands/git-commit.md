---
name: git-auto-commit
description: Analyze diffs, group related changes by type/scope, create conventional commits. Stages files selectively per group (not all at once) for atomic, logical commits. Use `/git-commit`.
allowed-tools: Read, Bash(git:*), Write
---

# Git Auto-Commit

Automatically analyze code changes, group them logically, and create conventional commits with proper typing and scoping.

## Usage

```bash
/git-commit
```

No arguments. Analyzes diffs and commits intelligently.

## Workflow

1. **Verify repository** — check `.git` exists
2. **Analyze files** — `git status --porcelain`
3. **Examine diffs** — `git diff <file>` to detect type and scope
4. **Group changes** — by type (feat, fix, test, chore) and scope (auth, db, api, etc.)
5. **Stage selectively** — only files for ONE group per commit (not all at once)
6. **Create commit** — conventional format: `type(scope): description`
7. **Repeat** — until all groups committed
8. **Summary** — show all commits created

## Conventional Format

```
feat(auth): add login endpoint
fix(database): resolve pooling issue
test(auth): add test cases
chore: update dependencies
refactor(api): simplify handler
docs(readme): add setup guide
perf(db): optimize queries
```

## Auto-Detected Scopes

Based on file paths: `app` → api, `models` → models, `auth` → auth, `db/database` → database, `tests/test_` → test, `config` → config, `ui/frontend` → ui, `utils` → utils, `middleware` → middleware

## Why Selective Staging?

**Bad:** `git add .` → mixes unrelated changes, unclear commits, hard to revert  
**Good:** `/git-commit` → atomic commits, clear intent, easy to cherry-pick or revert

## Example

**Before:**
```
 M app.py
 M models/user.py
 M requirements.txt
?? tests/test_auth.py
```

**Groups detected:**
- Group 1: auth feature (app.py, models/user.py, tests/test_auth.py)
- Group 2: chore (requirements.txt)

**Result:**
```
git add app.py models/user.py tests/test_auth.py
git commit -m "feat(auth): add login and verification"

git add requirements.txt
git commit -m "chore: update packages"
```

## Benefits

✅ Atomic commits  
✅ Clear history  
✅ Easy reviews  
✅ Better debugging  
✅ Semantic versioning possible  
✅ Easy to revert specific changes  

## Rules

- Lowercase descriptions, imperative mood ("add", not "adds")
- No period at end
- Only stage related files per group
- Skip ignored files (logs, temp, venv, etc.)

## Config

Set git user first:
```bash
git config user.name "Your Name"
git config user.email "your@email.com"
```

## Design

One thing per commit. Atomic. Clear intent. No kitchen-sink commits. Conventional format for automation.