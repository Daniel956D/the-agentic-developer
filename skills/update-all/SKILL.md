---
name: update-all
description: Update all packages, libraries, and dependencies — Homebrew, npm global, pip, Claude Code, and plugins. Use when the user says "update everything", "update packages", "update dependencies", or "run updates".
allowed-tools: Bash
disable-model-invocation: true
---

# Update All Packages

Staged package manager updates with dry-run preview before executing.

## Process

### Step 1: Capture current state

Run `claude --version`, `node --version`, `python3 --version` to capture before state.

### Step 2: Dry-run preview (ALWAYS do this first)

Show what would be updated WITHOUT executing:

1. **Homebrew:** `brew update && brew outdated`
2. **npm global:** `npm outdated -g`
3. **pip:** `pip3 list --outdated --format=columns 2>/dev/null`
4. **Claude Code:** `claude update --check 2>&1 || echo "Check claude --version manually"`

### Step 3: Present summary and get approval

Show the user a preview table:

```
## Update Preview — [date]

| Manager | Outdated | Key Packages |
|---------|----------|-------------|
| Homebrew | N packages | [list notable ones] |
| npm global | N packages | [list notable ones] |
| pip | N packages | [list notable ones] |
| Claude Code | current → available | |

Proceed with all updates? (or specify which to skip)
```

**Wait for approval before proceeding.** If the user says to skip a manager, skip it.

### Step 4: Execute approved updates

Only run what was approved. Execute sequentially (not in parallel) so failures are isolated:

1. **Homebrew:** `brew upgrade 2>&1 | tail -20`
2. **npm global:** `npm update -g 2>&1 | tail -20`
3. **pip:** Only update the specific packages from the preview — `pip3 install --upgrade <package1> <package2> ...` — NOT a blind `xargs` of everything
4. **Claude Code:** `claude update 2>&1`

### Step 5: Verify and report

Capture after-state versions and show results:

```
## Update Summary — [date]

| Manager | Before | After | Updated |
|---------|--------|-------|---------|
| Homebrew | — | — | N packages |
| npm global | — | — | N packages |
| pip | — | — | N packages |
| Claude Code | vX.X.X | vX.X.X | yes/no |

### Action Needed
- [ ] Restart Claude Code if version changed
- [ ] Run `/plugin update superpowers` for plugin updates
```

## Rules

- NEVER run blind global upgrades without preview
- NEVER pipe outdated package lists through xargs for bulk install
- If any update fails, report the error and continue with the rest
- pip updates should be explicit packages, not wildcards
