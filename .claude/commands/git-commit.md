---
name: git-auto-commit
description: Analyze diffs, group related changes by type/scope, stage files selectively per group, create conventional commits. Use `/git-commit` to orchestrate the full staging→commit workflow for atomic, logical commits. Handles features, fixes, `.claude` updates, cleanups, and all change types.
allowed-tools: Read, Bash(git:*), Write
---

# Git Auto-Commit — Intelligent Staging & Conventional Commits

Automatically analyze code changes, **stage files selectively by logical group**, and create conventional commits with proper typing and scoping. Each group gets its own atomic commit.

Includes proper handling of:
- ✅ **Feature commits** (new functionality)
- ✅ **Bug fixes** (solving problems)
- ✅ **`.claude` updates** (agent specs, prompts, guidelines — treated as documentation)
- ✅ **Test commits** (test code)
- ✅ **Cleanup commits** (removing unused code)
- ✅ **Chore commits** (dependencies, config)

## Usage

```bash
/git-commit
```

No arguments. Analyzes diffs, stages, and commits intelligently.

---

## Workflow (5 Core Steps)

### 1. **Verify Repository**
Check that `.git/` exists and the working directory is ready.
```bash
git status
```

### 2. **Analyze Unstaged Changes**
Identify all modified and untracked files.
```bash
git status --porcelain
```

Example output:
```
 M app.py                                    # Modified
 M database/db.py                            # Modified
 M templates/profile.html                    # Modified
 M static/css/style.css                      # Modified
 M .claude/quality-reviewer.md               # Modified (UPDATE, NOT DELETE!)
 M .claude/security-reviewer.md              # Modified (UPDATE, NOT DELETE!)
 M requirements.txt                          # Modified
?? tests/test_profile.py                     # Untracked (new)
```

### 3. **Examine Diffs to Detect Type & Scope**
For each modified file, read the actual diff to understand:
- **Type**: `feat` (feature), `fix` (bug fix), `test` (test code), `docs` (documentation), `chore` (dependencies), `refactor`, `perf`, `cleanup`, `ci`, `revert`
- **Scope**: Which part of the codebase? `auth`, `db`, `api`, `ui`, `profile`, `claude`, etc.

```bash
git diff app.py
git diff database/db.py
git diff .claude/quality-reviewer.md    # This is a DOCUMENTATION update
git diff requirements.txt
```

### 4. **Group Changes Logically** ← **CRITICAL STEP**

**Do NOT stage everything at once.** Group related changes by type+scope:

**Example grouping (with `.claude` documentation updates):**

| Group | Files | Type | Scope | Commit Message |
|-------|-------|------|-------|-----------------|
| 1 | `app.py`, `database/db.py` | `feat` | `profile` | `feat(profile): add date range filtering logic` |
| 2 | `templates/profile.html`, `static/css/style.css` | `feat` | `ui` | `feat(ui): add date filter form and styles` |
| 3 | `tests/test_profile.py` | `test` | `profile` | `test(profile): add date filter test cases` |
| 4 | `.claude/quality-reviewer.md`, `.claude/security-reviewer.md`, `.claude/test-runner.md` | `docs` | `claude` | `docs(.claude): update agent guidelines for profile date filter feature` |
| 5 | `requirements.txt` | `chore` | — | `chore: update dependencies` |

Each group becomes **ONE atomic commit.**

### 5. **Stage Selectively Per Group** ← **THE STAGING WORKFLOW**

**For Group 1 (Feature: Profile logic):**
```bash
git add app.py database/db.py
git status  # verify only these 2 files are staged
git commit -m "feat(profile): add date range filtering logic"
```

**For Group 2 (Feature: Profile UI):**
```bash
git add templates/profile.html static/css/style.css
git status  # verify only these 2 files are staged
git commit -m "feat(ui): add date filter form and styles"
```

**For Group 3 (Tests: Profile feature tests):**
```bash
git add tests/test_profile.py
git status  # verify only test file is staged
git commit -m "test(profile): add date filter test cases"
```

**For Group 4 (Docs: Update `.claude` agent guides) ← KEY EXAMPLE**
```bash
git add .claude/quality-reviewer.md .claude/security-reviewer.md .claude/test-runner.md
git status  # verify ONLY .claude documentation files are staged (git add, NOT git rm!)
git commit -m "docs(.claude): update agent guidelines for profile date filter feature"
```

**For Group 5 (Chore: Dependencies):**
```bash
git add requirements.txt
git status  # verify only requirements.txt is staged
git commit -m "chore: update dependencies"
```

### 6. **Verify All Changes Committed**
```bash
git status  # should show "nothing to commit, working tree clean"
git log --oneline -n 10  # show last 10 commits
```

### 7. **Summary**
Display all commits created in this session.

---

## Proper Handling of `.claude` Files

### ✅ **`.claude` files are DOCUMENTATION**

Files like `.claude/quality-reviewer.md`, `.claude/security-reviewer.md`, etc. are:
- **Agent specifications** and **prompt definitions**
- **Team guidelines** for how agents review code
- **Part of your project source code**

### ✅ **Update them using `git add` (NOT `git rm`)**

```bash
# CORRECT: Stage for update/commit
git add .claude/quality-reviewer.md
git commit -m "docs(.claude): update quality reviewer guidelines"

# WRONG: Do NOT delete them
git rm .claude/quality-reviewer.md  # ❌ DON'T DO THIS
```

### ✅ **Use `docs(.claude)` scope**

When committing `.claude` updates:
```bash
git commit -m "docs(.claude): update agent prompts and specifications"
git commit -m "docs(.claude): add new quality reviewer rules"
git commit -m "docs(.claude): refine security reviewer scope for auth features"
```

### ✅ **Example: Real workflow with `.claude` updates**

```bash
# Feature implementation
git add app.py database/db.py
git commit -m "feat(profile): add date range filtering"

# Update agent guidelines that cover this feature
git add .claude/quality-reviewer.md .claude/security-reviewer.md
git commit -m "docs(.claude): update guidelines for date filter features"

# Tests for the feature
git add tests/test_profile.py
git commit -m "test(profile): add date filter tests"
```

**Result in git log:**
```
a1b2c3d test(profile): add date filter tests
d4e5f6g docs(.claude): update guidelines for date filter features
g7h8i9j feat(profile): add date range filtering
```

---

## Conventional Commit Format

```
type(scope): description
```

### Types
| Type | Use Case | Example |
|------|----------|---------|
| `feat` | New feature | `feat(auth): add two-factor authentication` |
| `fix` | Bug fix | `fix(database): resolve pooling issue` |
| `test` | Test files only | `test(auth): add test cases for login` |
| `docs` | Documentation (including `.claude` updates) | `docs(.claude): update agent guidelines` |
| `chore` | Dependencies, config, build | `chore: update Flask to 2.3.0` |
| `refactor` | Code improvement (no behavior change) | `refactor(api): simplify handler logic` |
| `perf` | Performance improvement | `perf(db): optimize expense queries` |
| `style` | Formatting only (rare) | `style: run prettier on templates` |
| `ci` | CI/CD pipeline, build scripts | `ci: add GitHub Actions workflow` |
| `cleanup` | Remove unused code | `cleanup: remove dead code and imports` |
| `revert` | Undo a previous commit | `revert: feat(auth): remove faulty login` |

### Scopes (Auto-Detected from File Paths)

| Scope | File Paths | Note |
|-------|-----------|------|
| `auth` | `app.py` (login/logout), `models/user.py` | Authentication feature |
| `database` \| `db` | `database/db.py`, schema changes | Database operations |
| `api` | Route handlers, endpoints in `app.py` | API endpoints |
| `test` | `tests/test_*.py` | Test files |
| `ui` | `templates/`, `static/css/`, `static/js/` | User interface |
| `profile` | `templates/profile.html`, profile routes | Profile page feature |
| `config` | `config.py`, `.env`, `requirements.txt` | Configuration |
| **`claude`** | **`.claude/quality-reviewer.md`**, **`.claude/security-reviewer.md`**, etc. | **Agent specs & guidelines** |
| *(no scope)* | `chore:`, `ci:`, `cleanup:`, `revert:` | Global/cross-cutting |

### Rules for Descriptions
- **Imperative mood**: "add", "update", "remove" (not "adds", "added", "removed")
- **Lowercase**: `feat(auth)`, not `Feat(Auth)`
- **No period at end**: `feat(auth): add login` not `feat(auth): add login.`
- **Be specific**: `feat(profile): add date filter` not `feat: update profile`
- **For `.claude` updates**: Be clear about what changed: `docs(.claude): update quality reviewer rules for database changes`

---

## Example Walkthrough (Real Project Scenario)

### Before `/git-commit`
```
On branch main
Changes not staged for commit:
  modified:   app.py
  modified:   database/db.py
  modified:   templates/profile.html
  modified:   static/css/style.css
  modified:   .claude/quality-reviewer.md
  modified:   .claude/security-reviewer.md
  modified:   requirements.txt

Untracked files:
  new file:   tests/test_profile.py
```

### Analysis & Grouping
- **Group 1**: `app.py` + `database/db.py` → feat(profile) — date filter logic
- **Group 2**: `templates/profile.html` + `static/css/style.css` → feat(ui) — filter UI
- **Group 3**: `tests/test_profile.py` → test(profile) — feature tests
- **Group 4**: `.claude/quality-reviewer.md` + `.claude/security-reviewer.md` → docs(.claude) — update agent guidelines
- **Group 5**: `requirements.txt` → chore — dependency update

### Staging & Commits

**Commit 1 — Feature: Profile filtering logic**
```bash
git add app.py database/db.py
git commit -m "feat(profile): add date range filtering logic"
```

**Commit 2 — Feature: Profile filter UI**
```bash
git add templates/profile.html static/css/style.css
git commit -m "feat(ui): add date filter form and styles"
```

**Commit 3 — Tests: Profile feature tests**
```bash
git add tests/test_profile.py
git commit -m "test(profile): add date filter test cases"
```

**Commit 4 — Docs: Update agent guidelines** ← **KEY: `.claude` updates**
```bash
git add .claude/quality-reviewer.md .claude/security-reviewer.md
git status  # Verify .claude files are staged (should see 2 files)
git commit -m "docs(.claude): update reviewer guidelines for date filter features"
```

**Commit 5 — Chore: Update dependencies**
```bash
git add requirements.txt
git commit -m "chore: update dependencies"
```

**Final result:**
```bash
$ git log --oneline
e5f6g7h chore: update dependencies
d4e5f6g docs(.claude): update reviewer guidelines for date filter features
c3d4e5f test(profile): add date filter test cases
b2c3d4e feat(ui): add date filter form and styles
a1b2c3d feat(profile): add date range filtering logic
```

**Perfect atomic history.** Each commit is clear and self-contained. The `.claude` updates are explicit and intentional. 🎯

---

## Why Selective Staging Matters

### ❌ **Bad Practice: `git add .` (all at once)**
```bash
git add .        # DON'T DO THIS
git commit -m "changes"
```
**Problems:**
- Mixes features, fixes, documentation, and config in one commit
- Unclear what each commit does
- Hard to review ("why are we updating agent guidelines in the same commit as adding a feature?")
- Hard to revert one change without affecting others
- Breaks semantic versioning
- `git blame` becomes useless

### ✅ **Good Practice: Stage by group**
```bash
git add app.py database/db.py
git commit -m "feat(profile): add date filtering"

git add .claude/quality-reviewer.md
git commit -m "docs(.claude): update guidelines"

git add tests/test_profile.py
git commit -m "test(profile): add tests"

git add requirements.txt
git commit -m "chore: update dependencies"
```
**Benefits:**
- Each commit is atomic (one logical unit)
- Clear history that's easy to understand
- Easy to cherry-pick specific fixes
- Easy to revert a bad change without affecting others
- Supports semantic versioning (`major.minor.patch`)
- `git blame` and `git bisect` work effectively
- Code reviews are clearer
- **Agent guideline updates are explicit and traceable**

---

## Verification Checklist

Before running `/git-commit`:

- [ ] Working directory has changes: `git status` shows modified files
- [ ] No merge conflicts: `git status` doesn't show "both modified"
- [ ] User is configured: `git config user.name` and `git config user.email` are set
- [ ] On the right branch: `git branch` shows `main` or intended branch
- [ ] `.claude` files should be **updated/committed**, not deleted

After `/git-commit`:

- [ ] All changes committed: `git status` shows "working tree clean"
- [ ] Commits are correct: `git log --oneline -n 15` shows expected commits
- [ ] No typos: Verify commit messages are readable and accurate
- [ ] Grouped logically: Each commit has one semantic purpose
- [ ] `.claude` updates have `docs(.claude)` scope: Check agent documentation commits

---

## Git Configuration (Run Once)

```bash
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

Or per-project:
```bash
cd /path/to/project
git config user.name "Your Name"
git config user.email "your@email.com"
```

---

## Design Philosophy

**One thing per commit.** Atomic. Clear intent. No kitchen-sink commits.

Each commit should:
1. Pass tests
2. Have one semantic purpose
3. Be easy to understand in a code review
4. Be safe to revert if needed

**This includes `.claude` updates.** An agent guideline change is a meaningful part of your project history. It deserves its own commit.

This enables:
- **Bisecting** (`git bisect`) to find bugs
- **Cherry-picking** fixes to other branches
- **Reverting** without side effects
- **Blame** (`git blame`) to understand why code exists
- **Semantic versioning** (major.minor.patch)
- **Traceability** of when and why agent guidelines changed

---

## Common Pitfalls

### ❌ Pitfall 1: Adding all files at once
```bash
git add .        # DON'T DO THIS
git commit -m "stuff"
```
**Fix:** Add by group
```bash
git add app.py
git commit -m "feat(auth): add login"

git add .claude/quality-reviewer.md
git commit -m "docs(.claude): update guidelines"
```

### ❌ Pitfall 2: Mixing features and `.claude` updates
```bash
git add app.py .claude/quality-reviewer.md
git commit -m "feat(auth): add login + update guidelines"  # TWO THINGS!
```
**Fix:** Separate into two commits
```bash
git add app.py
git commit -m "feat(auth): add login endpoint"

git add .claude/quality-reviewer.md
git commit -m "docs(.claude): update guidelines for auth features"
```

### ❌ Pitfall 3: Treating `.claude` files as deletions
```bash
git rm .claude/quality-reviewer.md  # DON'T DO THIS!
git commit -m "delete: remove claude files"
```
**Fix:** Update them as documentation
```bash
git add .claude/quality-reviewer.md
git commit -m "docs(.claude): refine quality reviewer scope"
```

### ❌ Pitfall 4: Unclear `.claude` commit messages
```bash
git add .claude/quality-reviewer.md
git commit -m "docs: update"  # Too vague, no scope
```
**Fix:** Be specific
```bash
git add .claude/quality-reviewer.md
git commit -m "docs(.claude): add rules for date filter features"
```

---

## Helpful Git Commands

```bash
# Check what's changed
git status                    # Overview
git diff                      # All unstaged changes
git diff --staged             # All staged changes
git diff app.py               # Changes in app.py only
git diff .claude/             # Changes in .claude/ directory

# Stage intelligently
git add app.py                # Add specific file
git add app.py db.py          # Add multiple files
git add .claude/*             # Add all .claude files
git add -p                    # Interactive: stage by hunk

# Commit
git commit -m "feat(auth): add login"
git commit -m "docs(.claude): update guidelines"

# Check history
git log --oneline             # Short log
git log -n 10                 # Last 10 commits
git log -- .claude/           # Commits affecting .claude/
git show <commit>             # Show a commit

# Undo (if needed)
git reset HEAD~1              # Undo last commit (keep changes)
git revert <commit>           # Create new commit that undoes old commit
git checkout -- <file>        # Discard changes in working dir
git restore --staged <file>   # Unstage file
```

---

## Summary

**The staging workflow is the heart of good Git hygiene:**

1. **Analyze** what changed (features, fixes, `.claude` updates, cleanup)
2. **Group** logically by type + scope (including `docs(.claude)` scope)
3. **Stage** ONE group at a time (use `git add`, never `git rm` for `.claude` files)
4. **Verify** with `git status` before committing
5. **Commit** with a clear conventional message
6. **Repeat** until all groups are committed

**Include `.claude` documentation updates explicitly.** They're part of your project. Commit them with `docs(.claude)` scope alongside your code changes.

This creates a clean, understandable, and traceable history that serves your project for years.
