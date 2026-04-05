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
