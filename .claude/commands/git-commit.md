---
name: git-auto-commit
description:  Analyse ,adds and commits as per code diff
allowed-tools: Read, Bash(git:*), Write
---

# Git Auto-Commit Slash Command

Automatically analyze your code changes, intelligently organize them into logical commit groups, and create conventional commits with proper typing and scoping.

## Overview

When you run `/git-commit`, the command:
1. Analyzes all your modified files
2. Examines the actual code changes (diffs)
3. Detects what type of changes were made (feature, fix, chore, etc.)
4. Groups related files together logically
5. Plans a sequence of conventional commits
6. Stages and commits each group separately
7. Creates properly formatted commit messages
8. Shows you a complete summary

## Usage

```bash
/git-commit
```

**No arguments needed!** The command analyzes your actual code changes and commits intelligently based on what it detects.

---

## Complete Workflow

### Step 1: Verify Git Repository

Check if we're in a valid git repository.

```bash
git rev-parse --git-dir
```

**What it does:**
- Checks for `.git` directory in current or parent directories
- Validates git is properly initialized

**Success:**