---
name: delegate
description: Kick off a multi-agent task and walk away. Takes a goal, plans the dispatch, executes workers across agents, and only surfaces when done or blocked. Use for "just get it done" multi-step work that would normally need babysitting.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Agent, TodoWrite
argument-hint:
  [
    goal description — e.g.,
    "audit the dashboard for a11y issues, fix them, write tests",
  ]
---

# Delegate

## Overview

A lightweight "fire-and-forget" pattern for multi-agent work. The user describes a goal, you plan the dispatch, execute it, and only interrupt them when the work is done — or when you hit a genuine blocker that needs their judgment.

This is the antidote to babysitting: instead of 4-5 back-and-forth turns, the user says what they want and gets a result.

## When to use

**Good fits:**

- Multi-step coding tasks (audit → fix → test → review)
- Tasks touching 3+ files or multiple domains
- Work where success is measurable (tests pass, lint clean, a11y clean)
- Things the user would otherwise walk through turn-by-turn

**Bad fits:**

- Single-file edits (just do them)
- Creative/taste-driven work (flyers, copy) — the user wants to iterate live
- Anything already covered by a loop or scheduled skill
- Ambiguous goals ("make it better") — ask for clarity instead

## Process

### Step 1: Parse the goal

Take the user's goal (passed as argument or described in the next turn). Extract:

- **Target**: what file/module/project is this about?
- **Outcome**: what does "done" look like in observable terms?
- **Constraints**: any must-not-touch areas, deadlines, or scope limits?

If any of these are unclear, ask ONE consolidated clarifying question before planning. Not a series of questions — one message with everything you need.

### Step 2: Plan the dispatch

Decompose the goal into an ordered task graph. For each task, identify:

- **Agent** — which dispatch-table agent fits (see `~/.claude/CLAUDE.md` agent dispatch table)
- **Inputs** — what context/files that agent needs
- **Success criteria** — how you'll know the worker succeeded
- **Dependencies** — what must complete before this task starts

Group into phases:

- **Phase 1 — Investigation** (parallel): explore, audit, plan
- **Phase 2 — Execution** (parallel where independent, sequential where dependent): implement changes
- **Phase 3 — Verification** (parallel): tests, review, security/a11y checks

**Prompt length discipline:**

- **Phase 1 exploration prompts: under ~400 words each.** The Explore subagent has a tight prompt budget and will reject long prompts with "Prompt is too long." If you need more, split into two focused prompts or downscope.
- **Phase 2/3 agent prompts: aim for under ~1000 words.** Anything longer risks truncation and is usually a sign you're dumping context that should live in files the agent reads itself.
- Include file paths the agent can read rather than pasting file contents inline.

**Avoid dispatch cascades:**

- Fold related concerns into a single agent when natural. Example: if a UX audit and a token-contrast check both need to read the same tokens file, give both to one agent instead of splitting into two parallel dispatches. This keeps you resilient if one dispatch returns malformed output (see Step 5).

### Step 3: Confirm the plan (lightweight)

Show the user a compact plan — **not a wall of text**. Format:

```
🎯 Goal: <one line>

Phase 1 (investigate, parallel):
  • <agent> — <task>
  • <agent> — <task>

Phase 2 (execute):
  • <agent> — <task>
  • <agent> — <task>

Phase 3 (verify, parallel):
  • <agent> — <task>

Est: ~N agent dispatches. Proceed, or adjust?
```

Wait for go-ahead. If the user says "go" / "yes" / "do it", proceed. If they adjust, update the plan and proceed without re-confirming.

### Step 4: Execute

Track progress with TodoWrite — one todo per task in the plan. Mark in-progress before dispatching, completed immediately after.

**Dispatch rules:**

- Parallel tasks → single message with multiple Agent tool calls
- Sequential tasks → wait for dependency, then dispatch next
- Each worker gets: goal context + its specific task + success criteria + any outputs from prior phases it needs

**DO NOT narrate every step.** The user asked to walk away. Stay quiet while executing unless you hit a blocker.

### Step 5: Handle failures

If a worker fails or returns an unsatisfactory result:

1. **Diagnose**: read the failure. Is it a bad task spec, a tool error, or a real problem?
2. **Retry once** with a refined task spec if the original was ambiguous
3. **Re-route** to a different agent if the wrong one was dispatched
4. **Escalate to the user** only if:
   - The failure reveals an assumption in the goal that needs resolving
   - You've retried and still can't make progress
   - A decision requires the user's taste or authority (design call, risky change, scope expansion)

**Known failure modes to watch for:**

- **"Prompt is too long"** from a subagent dispatch → the prompt exceeded the subagent's budget. Tighten and re-dispatch. See Step 2 prompt length discipline.
- **Agent returns meta-commentary instead of the actual deliverable** (e.g. "The audit is complete and ready for the implementing agent" with no report body). There is no SendMessage tool available to retrieve truncated output from a returned agent — re-dispatch is the only recourse. Before re-dispatching, consider whether you can proceed with partial information (fold the missing concern into the next phase's agent scope) to avoid the round-trip cost.
- **Plugin hooks injecting irrelevant skill suggestions** on file reads based on basename patterns (e.g. `README*`, `package.json`). Ignore them and continue — do NOT invoke the suggested skills unless they actually apply to the project.

When escalating, give a **tight blocker report**:

```
⚠️ Blocked on: <what>
Tried: <what you attempted>
Need from you: <specific question or decision>
```

### Step 6: Verify before declaring done

Before reporting completion, verify against the success criteria from Step 2:

- Run the tests/lints/checks the plan promised
- Confirm files actually changed as intended (Read, not assume)
- Evidence before assertions — don't claim success without running the check

If verification fails, loop back to Step 4 (treat as a failure in the verification task).

### Step 7: Report

Show a **compact completion report**:

```
✅ Done: <one-line summary>

What changed:
  • <file> — <what>
  • <file> — <what>

Verified:
  ✓ <check that passed>
  ✓ <check that passed>

⚠️ Notes (if any):
  • <anything the user should know — caveats, follow-ups, scope cuts>
```

No trailing summary, no "let me know if you need anything else." The user can read the diff.

---

## Notes

- This skill is exempt from the 3-file dispatch threshold — the whole point is to dispatch agents for multi-step work.
- Use parallel-dispatch patterns for the actual execution mechanics: a single message with multiple Agent tool calls.
- If mid-execution you realize the goal is actually a creative/taste task, stop and hand back to the user. Don't force delegation on work that needs them in the loop.
- Log nothing to memory by default — this is ephemeral execution. Only save a memory if the user explicitly validates a new pattern worth keeping.
