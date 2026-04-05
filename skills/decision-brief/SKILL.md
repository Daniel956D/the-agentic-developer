---
name: decision-brief
description: Multi-agent deliberation for strategic and technical decisions. Dispatches agents to debate, cross-review, and vote on a decision brief. Use for "should we X or Y" decisions.
allowed-tools: Read, Write, Bash, Glob, Agent
argument-hint:
  [
    optional: template-name — tech-stack,
    build-vs-buy,
    architecture,
    migration,
    crisis,
    priority,
  ]
---

# Decision Brief

## Overview

Structured decision-making through multi-agent deliberation. Takes a brief (structured input), dispatches a board of specialized agents to debate it, and produces a decision memo with full observability.

## Process

### Step 1: Parse the Brief

**If a template argument was passed** (e.g., `/decision-brief tech-stack`):

- Map the argument to a template file:
  - `tech-stack` → `~/.claude/decision-templates/tech-stack-evaluation.md`
  - `build-vs-buy` → `~/.claude/decision-templates/build-vs-buy.md`
  - `architecture` → `~/.claude/decision-templates/architecture-decision.md`
  - `migration` → `~/.claude/decision-templates/migration-planning.md`
  - `crisis` → `~/.claude/decision-templates/crisis-incident-response.md`
  - `priority` → `~/.claude/decision-templates/priority-call.md`
- Read the template file
- Present each `{{placeholder}}` to the user as a question, one at a time
- Assemble the completed brief

**If freeform text was provided:**

- Parse it into sections: Decision, Context, Stakes, Constraints, Options
- Ask the user to confirm or fill in any missing sections

**If no argument:**

- Show the 6 available templates:
  1. **Tech Stack Evaluation** — "Should we use X or Y?"
  2. **Build vs Buy** — "Build it ourselves or use a service?"
  3. **Architecture Decision** — "How should we structure this?"
  4. **Migration Planning** — "Should we migrate, and how?"
  5. **Crisis/Incident Response** — "Something happened, what do we do?"
  6. **Priority Call** — "What should I focus on first?"
- Ask the user to pick one, or describe the decision freeform

### Step 2: Select the Board

Based on the template (or decision type if freeform), select the default board:

| Template     | Default Board                                                                                 | Rationale                                                     |
| ------------ | --------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| Tech Stack   | strategic-planner, performance-optimizer, security-auditor                                    | Performance/security trade-offs are core to stack choices     |
| Build vs Buy | strategic-planner, security-auditor, api-architect                                            | Cost/risk/integration complexity matter most                  |
| Architecture | strategic-planner, database-architect, api-architect, performance-optimizer, security-auditor | Full technical board — architecture touches every domain      |
| Migration    | strategic-planner, database-architect, performance-optimizer, security-auditor                | Data integrity + performance regression are primary risks     |
| Crisis       | security-auditor, strategic-planner, systematic-debugger                                      | Triage: security assessment + root cause + strategic response |
| Priority     | strategic-planner, performance-optimizer                                                      | Lightweight — strategy + effort estimation                    |

Show the user the selected board and allow overrides:

- "Add [agent]" to include an additional agent
- "Skip [agent]" to remove one
- Max 5 agents per deliberation

### Step 3: Cost Confirmation

Before dispatching, show the user:

> "This will dispatch **N agents x 2 rounds** (~X agent calls). Estimated cost: **$A-$B**. Proceed?"

Rough estimates per agent call:

- Opus agent: ~$0.30-0.50
- Sonnet agent: ~$0.10-0.20
- Haiku agent: ~$0.02-0.05

Wait for confirmation before proceeding.

### Step 4: Round 1 — Initial Positions

Dispatch all board agents **in parallel** using the Agent tool. Each agent receives:

1. The completed brief (full text)
2. Their expertise file (read from `~/.claude/agent-expertise/<agent-name>.md`)
3. This prompt:

> "You are a board member deliberating on the following decision. Read the brief carefully and take a clear, opinionated stance. Do NOT hedge. Structure your response as:
>
> **Stance:** [your position — one line]
> **Reasoning:** [2-4 paragraphs explaining why, from your domain expertise]
> **Key Risk:** [the biggest risk of your recommendation]
> **Confidence:** [1-10]"

Collect all responses.

### Step 5: Consensus Check

Check if a majority of agents agree (same stance) and average confidence is 7+.

- If **consensus**: skip Round 2, go directly to Step 8 (Synthesis).
- If **no consensus**: proceed to Round 2.

### Step 6: Round 2 — Cross-Review (default final round)

Dispatch all board agents **in parallel** again. Each receives:

1. The original brief
2. ALL agents' Round 1 positions (including their own)
3. This prompt:

> "You've seen every board member's initial position on this decision. Now:
>
> 1. Challenge the weakest argument from another board member — be specific about why it's wrong
> 2. Acknowledge the strongest point from another board member
> 3. Call out anything ALL board members missed from your domain expertise
> 4. Give your **final stance** and **final confidence** (1-10). If you changed your position, explain what changed your mind."

Collect all responses.

### Step 7: Round 3 — Final Vote (opt-in only)

**Only trigger Round 3 if:**

- Agents changed stances in Round 2 but still haven't converged
- The user explicitly requests it ("keep debating", "one more round")

If triggered, dispatch all agents with:

1. All previous rounds
2. Prompt: "Final round. Give your absolute final stance, confidence, and one sentence on what remains unresolved."

**Most deliberations end at Round 2.**

### Step 8: Synthesis

Read all rounds and produce two files:

**Debate Log** → `~/.claude/debate-logs/YYYY-MM-DD-HHMM-<slug>.md`

Use the timestamp from when the deliberation started. The slug is a kebab-case summary of the decision (e.g., `flask-vs-django`, `buy-crm-tool`, `fix-auth-outage`).

Format:

```
# Debate Log: <decision title>
**Date:** YYYY-MM-DD
**Brief:** <template name or "freeform">
**Agents:** <comma-separated list>

## Round 1: Initial Positions

### <agent-name>
**Stance:** <position>
**Reasoning:** <summary>
**Key Risk:** <risk>
**Confidence:** N/10

[repeat for each agent]

## Round 2: Cross-Review

### <agent-name>
**Challenge:** <who they challenged and why>
**Acknowledged:** <strongest point from another agent>
**Missed by all:** <gap they identified>
**Final Stance:** <position>
**Final Confidence:** N/10

[repeat for each agent]

## Vote Tally
| Agent | R1 Stance | R1 Conf | R2 Stance | R2 Conf | Changed? |
|-------|-----------|---------|-----------|---------|----------|

**Result:** X-Y <summary>

## Unresolved Tensions
- <tension 1>
```

**Decision Memo** → `~/.claude/decision-memos/YYYY-MM-DD-HHMM-<slug>-memo.md`

Format:

```
# Decision Memo: <title>
**Date:** YYYY-MM-DD | **Template:** <template name>

## Recommendation
<1-3 sentences synthesizing the board's conclusion>

## Vote: X-Y (<summary>)
- **For:** <agents + confidence>
- **Against:** <agents + reasoning>

## Key Tensions
- <unresolved disagreement with brief context>

## Next Steps
1. <concrete action item>
2. <concrete action item>

---
Full debate log: ../debate-logs/YYYY-MM-DD-HHMM-<slug>.md
```

### Step 9: Present Results

Show the user:

1. The recommendation (1-2 sentences)
2. The vote tally (inline)
3. Key tensions (if any)
4. Links to both files

---

## Notes

- This skill is exempt from the 3-file dispatch threshold — it dispatches agents for decisions, not code changes
- Debate logs are append-only — never edit after creation
- Archive debate logs older than 90 days to `~/.claude/debate-logs/archive/`
