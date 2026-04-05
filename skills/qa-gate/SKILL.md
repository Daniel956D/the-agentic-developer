---
name: qa-gate
description: QA gate for code output. Dispatches review agents based on what was produced. Use after implementation tasks or for PR review.
allowed-tools: Read, Write, Grep, Glob, Bash, Agent
argument-hint: [optional: path-to-output-file]
---

# QA Gate

## Overview

A universal QA gate for all code output — whether from Claude's subagents, PRs, or any other source. Dispatches specialized agents based on output type.

## Trigger

- After completing an implementation task
- The user says "review this" or "QA this"
- Before claiming work is complete
- When reviewing a PR or code contribution

## Process

### Step 1: Identify the Output

Determine what was produced. If an argument was passed (file path), read it. Otherwise, identify the files changed in the current session.

### Step 2: Classify the Output

| Output Type           | How to Identify                                                                |
| --------------------- | ------------------------------------------------------------------------------ |
| New frontend code     | .tsx/.jsx/.html/.css files created/modified                                    |
| New backend/API code  | Routes, controllers, middleware, services                                      |
| Database changes      | Migrations, schema changes, query modifications                                |
| Tests                 | Test files created, test configuration changes                                 |
| Refactoring           | Changes to existing files, no new features                                     |
| Next.js code          | .tsx files in `app/` directory, layout.tsx, page.tsx, route.ts, Server Actions |
| Sanity schema changes | Files in `schemas/` directory, GROQ queries, sanity.config changes             |
| Research/analysis     | Text output, no code files changed                                             |

### Step 3: Dispatch Agents

**Frontend code:**

1. Dispatch `code-reviewer` — quality, patterns, maintainability
2. Dispatch `code-reviewer` with a11y focus — WCAG compliance
3. If security-relevant (auth UI, forms): dispatch `security-auditor`

**Backend/API code:**

1. Dispatch `code-reviewer` — quality, patterns, maintainability
2. Dispatch `security-auditor` — OWASP top 10, injection, auth issues
3. If API design changes: dispatch `api-architect`

**Database changes:**

1. Dispatch `code-reviewer` — verify no regressions
2. Dispatch `database-architect` — schema quality, index strategy

**Tests:**

1. Dispatch `tdd-engineer` — verify tests are meaningful (not tautological)
2. Run the tests locally to verify they pass
3. Check: do tests cover edge cases? Error cases? Or just happy path?

**Refactoring:**

1. Dispatch `code-reviewer` — verify no regressions
2. Dispatch `performance-optimizer` — check for performance changes
3. Run tests to verify nothing broke

**Next.js code:**

1. Dispatch `code-reviewer` — quality, patterns, Next.js-specific checks
2. Dispatch `frontend-specialist` — design system compliance, component patterns
3. If Server Actions or API routes: dispatch `security-auditor`

**Sanity schema/content changes:**

1. Dispatch `database-architect` — schema quality, GROQ query efficiency
2. If frontend integration: dispatch `frontend-specialist`

### Step 3.5: Cross-Review (when 3+ agents dispatched)

**Skip cross-review when:**

- Only 1 or 2 agents were dispatched (use `--thorough` to force with 2 agents)
- All agents returned clean / no issues found
- The user passed `--quick` flag

**If cross-review applies:**
Dispatch each agent again with all other agents' findings and this prompt:

> "Review the other reviewers' findings for this code. Flag anything you disagree with, surface issues they missed from your domain, and confirm findings you agree with. Be specific."

**Organize the combined results into:**

**Consensus Issues** (all agents agree) — high confidence, fix these

**Disputed Issues** — agents disagree, present both sides, the user decides

**Agent-Specific Findings** — unique to one agent's domain

Include a Cross-Review Summary at the end of the report:

```
### Cross-Review Summary
- Agents agreed on X/Y findings
- Z disputed findings need your call
```

### Step 4: Verdict

**APPROVED** — Output is correct, secure, and matches project patterns. Ready to ship.

**APPROVED WITH CHANGES** — Mostly correct but needs modifications:

- List each required change
- Explain why
- Indicate severity (must-fix vs nice-to-have)

**REJECTED** — Significant issues:

- List each issue
- Explain the impact
- Recommend: fix specific issues or take a different approach

### Step 5: Fix & Verify (APPROVED WITH CHANGES only)

After applying fixes, re-run **only the agents that found issues**:

- Tell the re-run agent to focus on specific areas that were fixed
- If re-run finds new issues: fix and re-run again. Loop until clean.

### Step 6: Log Lessons

If the QA process surfaced issues worth remembering, check `~/.claude/lessons-learned.md` and add a new entry if the issue isn't already captured. This prevents repeating the same mistakes across projects.
