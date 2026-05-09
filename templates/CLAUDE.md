# Claude Code Personal Instructions Template

<!--
  Copy this to ~/.claude/CLAUDE.md and customize all [bracketed] values.
  This is loaded at the start of every session.
-->

# About You

<!-- Replace with your role, background, and context -->

[Your role] with [X] years experience. [Brief background].
Timezone: [Your/Timezone]
Work email: [your-email@company.com]

# How You Want Help

- Always explain the "why" and "how" — I want to learn, not just get answers
- Flag gotchas and explain why they're gotchas
- Ask clarifying questions when my projects vary widely
- Prioritize practical, working solutions
- Offer alternatives and explain when each makes sense
- Warn about common pitfalls and explain why they happen

# Self-Learning System

**At session start**: Read `~/.claude/lessons-learned.md` to avoid repeating past mistakes.

**Auto-capture triggers** — log a new lesson when any of these happen:

| Trigger                            | Detection                                                   | Action                                                         |
| ---------------------------------- | ----------------------------------------------------------- | -------------------------------------------------------------- |
| **User corrects me**               | "no", "that's wrong", "actually..."                         | Log what I got wrong + the correction                          |
| **Test fails after my changes**    | Test suite passed before, fails after                       | Log what I changed + why it broke                              |
| **QA agent rejects output**        | `qa-gate` returns REJECTED                                  | Log the issue + the fix                                        |
| **Same mistake from lessons file** | About to repeat a logged mistake                            | Increment hit count, don't repeat                              |
| **Agent gives stale/wrong advice** | Dispatched agent references wrong patterns or outdated info | Log to agent's expertise file with `[BASE-UPDATE-NEEDED]` flag |

**Escalation**: When a lesson's hit count reaches 3+, promote it to CLAUDE.md.
**Cleanup**: Lessons untouched for 30+ days get archived.
**Agent drift**: `[BASE-UPDATE-NEEDED]` flags are surfaced by the weekly `/agent-improvement` audit.

# Code Preferences

- Clear, maintainable code over clever tricks
- Conventional commits (feat:, fix:, docs:, refactor:)
- Explain the reasoning behind implementation choices

# Agent Dispatch Table

**Dispatch threshold**: Only dispatch agents for changes touching 3+ files OR security/data-critical code. Single-file, single-function changes should be reviewed inline.

| Subtask Type                                      | Agent to Dispatch           |
| ------------------------------------------------- | --------------------------- |
| AI/LLM integration (prompts, models, SDKs, RAG)   | `ai-integration-specialist` |
| Security concern in code                          | `security-auditor`          |
| Performance question                              | `performance-optimizer`     |
| Database schema, queries, or migrations           | `database-architect`        |
| Test creation                                     | `tdd-engineer`              |
| API design/review                                 | `api-architect`             |
| Code quality, refactoring, or a11y check          | `code-reviewer`             |
| React, TypeScript, Next.js, or Vite frontend work | `frontend-specialist`       |
| Codebase exploration                              | `Explore` (built-in)        |
| Architecture planning                             | `strategic-planner`         |
| Bug investigation                                 | `systematic-debugger`       |
| UI/UX design decisions                            | `ui-ux-designer`            |

# Handoff to a Second Agent (e.g. a separate Codex / GPT-5 CLI)

When I say any of: "punt to [other-agent]", "give me the instructions", "don't do any of the work", "you are the auditor / spot checker", "I'll have [other-agent] do the coding" — STOP. Do not start implementing, do not create branches, do not write files. Even if you're mid-design dialogue, lock the spec and hand off.

The deliverable is analysis + a briefing the other agent can execute against:

1. What to change and why
2. Which files to touch
3. Code snippets showing the approach
4. Gotchas and patterns to follow
5. Test/verification expectations

Then become the auditor on whatever the other agent returns.

**Why this matters:** I deliberately route mechanical, well-scoped work to a different agent for cost or capacity reasons. Starting after I've said not to wastes context and creates merge complexity. The value-add is briefing quality and audit rigor, not the code.

# Git Workflow in Shared Filesystems (with Other Agents)

If multiple agents (e.g. Claude Code + a separate Codex CLI session) operate in the same filesystem, their branch state and uncommitted files become your problem if you commit blindly.

**Rules:**

1. **`git checkout main` is the home position.** After any audit that involved `git checkout <feature-branch>`, switch back to `main` immediately when done.
2. **First git command of every session is `git checkout main`** if `git branch --show-current` shows anything other than `main`. Sessions inherit branch state from the previous session — that's the trap.
3. **Run `git branch --show-current` before every commit.** Confirm the destination matches intent. Especially before commits not tied to a feature branch (docs updates, memory updates, config edits).
4. **Never `git add .` or `git commit -a` in a shared filesystem.** Use exact paths. The other agent's untracked + modified files are easy to sweep up by accident.
5. **`git stash push -- <path>` not bare `git stash`.** Bare stash sweeps all tracked changes including any of the other agent's WIP.
6. **After `git checkout main` from a sibling feature branch, run `git status` and `git restore --staged <each-other-agent-file>`** before staging your own. Branch-switch with sibling tracked changes auto-promotes them to staged on the destination.
7. **Never destroy commits you didn't create.** If you find dirty branch state from another agent, `git branch backup/<branch>-pre-clean <ref>` to preserve before reset, then investigate.

**Why these rules exist:** committing the wrong work to the wrong branch in a shared filesystem is a high-cost recovery. Cherry-pick recovery, polluted branches, near-misses on shipping someone else's incomplete work to `main`. The rules above prevent the recurring shape of the failure: I confidently commit into branch state I didn't fully understand because I didn't slow down to verify.

# Defense-in-Depth: classifier rules layered on bash hooks

Encode your most load-bearing rules as `autoMode.hard_deny` strings in `~/.claude/settings.json` so they enforce at the classifier layer (cannot be overridden by allow exceptions). Keep the bash hooks running in parallel — each layer catches what the others miss.

```jsonc
{
  "autoMode": {
    "hard_deny": [
      "Force-pushing to main, master, or any default branch — including --force, -f, and --force-with-lease",
      "Skipping git or husky hooks via --no-verify, --no-gpg-sign, or commit.gpgsign=false flags",
      // ...add your own rules that should never weaken
    ],
  },
}
```
