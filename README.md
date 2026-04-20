# The Agentic Developer

A production-grade Claude Code configuration with 16 specialized agents (14 local + 2 plugin-inherited), 14 custom skills, 6 loop commands, multiple safety hooks, a two-instrument evaluation harness, and a self-improving weekly audit system. This is how I build software with AI — not as a novelty, but as core infrastructure.

Built for shipping across Django, Flask, Next.js, React/Vite, Python utilities, and Node.js integrations. Every agent is grounded in real project patterns, real incident history, and real conventions. The setup compounds knowledge over time through persistent expertise files and automated weekly audits.

> **This isn't a collection of generic prompts.** Most Claude Code agent repos are 200 lines of "You are an expert React developer" that Claude already knows. This setup contains only what Claude would get wrong without it — project-specific patterns, real design tokens, actual incident history, and proven conventions.

## What's Inside

### 16 Specialized Agents (`agents/`)

Tiered by model for cost efficiency:

| Tier        | Model          | Agents                                                                                                                                                                                         | Purpose                                  |
| ----------- | -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| **Opus**    | Deep reasoning | ai-integration-specialist, canva-specialist, code-reviewer, database-architect, security-auditor, sharepoint-graph-specialist, strategic-planner, systematic-debugger, ui-ux-designer (9)      | Architecture, security, strategy         |
| **Sonnet**  | Implementation | api-architect, frontend-specialist, performance-optimizer, python-django-specialist, tdd-engineer (5)                                                                                          | Building and testing                     |
| **Inherit** | Plugin-sourced | silent-failure-hunter, type-design-analyzer (2) — from the [`pr-review-toolkit`](https://github.com/anthropics/claude-plugins) plugin, kept registered even when the plugin itself is disabled | Error-handling and type-invariant review |

**Key design principle:** Agents contain only project-specific patterns — not generic best practices Claude already knows. A 120-line agent with real patterns outperforms a 300-line agent padded with textbook content.

The two newest local agents — `sharepoint-graph-specialist` and `canva-specialist` — are templated with `[bracketed-placeholders]` so you can drop in your tenant, brand kit, and project paths.

Tier rationale for recent changes:

- `canva-specialist` moved Sonnet→Opus because branded-document work benefits from deeper layout reasoning.
- `performance-optimizer` moved Haiku→Sonnet after finding Haiku under-tiered for the rich output format (profile tables, ranked suggestions).
- `silent-failure-hunter` and `type-design-analyzer` are plugin-inherited — we don't republish them here; see their source plugin.

### 14 Custom Skills (`skills/`)

| Skill             | Purpose                                                                |
| ----------------- | ---------------------------------------------------------------------- |
| `qa-gate`         | Universal QA — dispatches review agents based on output type           |
| `decision-brief`  | Multi-agent deliberation with structured debate and voting             |
| `delegate`        | Fire-and-forget multi-agent execution with phased dispatch and retries |
| `grep-all`        | Cross-project regex search across every repo in `projects.txt`         |
| `status`          | Daily standups or cross-project snapshots from git/calendar/email      |
| `file-emails`     | Auto-file inbox emails into Outlook folders                            |
| `inbox-summary`   | Quick triage of unread inbox                                           |
| `refactor-ui`     | Safely restructure existing UI without breaking functionality          |
| `ui-ux-review`    | Audit pages for design quality and accessibility                       |
| `copy`            | Review text for clarity, tone, and impact                              |
| `brief`           | Translate technical work into executive summaries                      |
| `update-all`      | Staged package updates with dry-run preview                            |
| `ai-digest-agent` | Weekly AI/automation digest curation                                   |
| `3d-logo`         | Interactive 3D logos with Three.js                                     |

Retired: `ai-platform-updates` — the same job (logging Claude/ChatGPT/Gemini releases into a spreadsheet) is better handled by a scheduled script than a model-invoked skill. Moved to a daily launchd job.

### 6 Loop Commands (`commands/`)

Recurring automations that run during active sessions:

| Command                | Interval     | Purpose                                                     |
| ---------------------- | ------------ | ----------------------------------------------------------- |
| `email-drafter`        | 10 min       | Draft replies to unread emails (never sends)                |
| `vip-watch`            | 15 min       | Alert on emails from VIPs                                   |
| `meeting-prep`         | 30 min       | Calendar + attendee context                                 |
| `merge-conflict-watch` | 5 min        | Detect file collisions across worktrees                     |
| `weekly-review`        | Manual       | Weekly status + auto-chains to agent improvement on Fridays |
| `agent-improvement`    | Weekly (Fri) | Audit all agents/skills for drift and staleness             |

### Hooks (`hooks/`)

Three production hooks live in `~/.claude/hooks/`:

1. **Advisor reminder** — `UserPromptSubmit` hook (one-line `echo`) that injects a reminder at the start of every prompt, nudging Claude to call its `advisor()` second-opinion tool at two checkpoints on non-trivial tasks: after orientation (catch bad plans), and before declaring done (sanity-check the result). Tells Claude to skip on simple lookups so it doesn't become noise. See `docs/advisor-hook.md`.

2. **`destructive-guard.sh`** — `PreToolUse:Bash` hook that blocks 12 categories of irreversible commands (force-push to main, `rm -rf /`, hard reset, `mkfs`, `chmod 777`, `kubectl delete namespace`, `docker system prune -a`, etc.). Comes with a fix for two latent bugs that have silently broken this style of hook in many template repos — see `docs/destructive-guard-fix.md` for the post-mortem. **The force-push-to-main blocker was bypassable in the buggy version.**

3. **`lesson-capture-detector.sh`** — `UserPromptSubmit` hook that scans every user prompt for ~17 correction signals (`"that's wrong"`, `"actually,"`, `"you broke"`, etc.) and injects a reminder telling Claude to log the correction to `~/.claude/lessons-learned.md`. Replaces a passive "remember to capture corrections" policy that never actually fired with an in-context trigger that does.

### Self-Improvement System

The setup gets smarter every week through three layers:

1. **Real-time feedback** — When an agent gives stale advice, a `[BASE-UPDATE-NEEDED]` flag is logged to its expertise file
2. **Weekly audit** (`/agent-improvement`) — Every Friday, scans all agents against actual project state, flags drift, auto-fixes minor issues
3. **Monthly Codex cross-review** — First Friday of each month, dispatches an independent AI reviewer to rate all agents 1-10

### Evaluation Harness (`scripts/eval/`, `eval-fixtures/`, `docs/eval-harness.md`)

Most agent repos ship with zero evidence their agents actually work. This one ships with two eval instruments that measure both halves of the system:

| Instrument                | Layer      | Question                                                        | Baseline                                                |
| ------------------------- | ---------- | --------------------------------------------------------------- | ------------------------------------------------------- |
| **Skill-dispatch eval**   | Routing    | Does Claude Code pick the right skill/agent for a prompt?       | ~87% strict accuracy on a 2-skill starter scenario set  |
| **Agent catch-rate eval** | Capability | When the agent _does_ run, does it catch the bug it's meant to? | security-auditor 8/8 (100%) catch, 0% FP on 10 fixtures |

The catch-rate harness — `scripts/eval/agent-eval.py` — invokes `claude -p --system-prompt <agent-body>` against YAML fixtures with planted bugs and clean controls, then grades responses against expected keywords. `--system-prompt` replaces the Claude Code default, so the measurement shape matches a real `Task` dispatch.

**The interesting numbers are the divergences, not the headlines.** Strict (keyword-gated) vs manual review shows where the grader disagrees with a human reader — that's where you learn something. Full story, including honest limitations (small N, keyword vocabulary gap, LLM-as-judge v2 planned), in [`docs/eval-harness.md`](docs/eval-harness.md).

Monthly cadence is wired into `commands/agent-improvement.md` (Phase 4.5) so catch rates trend over time — you find out _before_ the next production bug if an agent silently dropped in quality.

### Templates (`templates/`)

- `CLAUDE.md` — Personal instructions template with dispatch table, self-learning triggers, and model routing
- `agent-template.md` — Starter template for creating new agents
- `skill-template.md` — Starter template for creating new skills

## Design Philosophy

### What makes this different from generic agent collections

Most Claude Code agent repos on GitHub are **generic templates** — "You are an expert React developer" with 200 lines of best practices Claude already knows. They have thousands of stars but add minimal value over Claude's base capabilities.

This setup follows a different approach:

1. **"Would removing this cause Claude to make mistakes?" If not, cut it.** (from official Claude Code best practices)
2. **Project-specific patterns only.** Real error handler names, real design tokens, real incident history.
3. **Descriptions under 250 chars.** Claude Code truncates longer descriptions — front-load trigger keywords.
4. **Right-size model routing.** Opus for reasoning, Sonnet for implementation, Haiku for checklists.
5. **Expertise compounds.** Each agent reads/writes a persistent knowledge file every session.
6. **Dispatch threshold.** Only dispatch agents for 3+ file changes or security-critical code. Single-file changes get inline review.

### Research backing

This setup was validated against:

- [Official Claude Code best practices](https://code.claude.com/docs/en/best-practices)
- [Official skills documentation](https://code.claude.com/docs/en/skills)
- [Official subagents documentation](https://code.claude.com/docs/en/sub-agents)
- [wshobson/agents](https://github.com/wshobson/agents) (33k stars) — model tiering and progressive disclosure patterns
- [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) (16.2k stars) — category organization
- [anthropics/skills](https://github.com/anthropics/skills) (111k stars) — official skill patterns

## How to Use This

### Quick Start

1. Clone this repo
2. Copy agents to `~/.claude/agents/`
3. Copy skills to `~/.claude/skills/`
4. Copy commands to `~/.claude/commands/`
5. Customize `templates/CLAUDE.md` and copy to `~/.claude/CLAUDE.md`
6. **Replace all `[bracketed-values]`** with your project-specific patterns

### Customization Guide

Every file uses `[bracketed-placeholders]` where you need to add your own content:

- `[Your Company]` — Your company or org name
- `[brand-primary]`, `[brand-secondary]` — Your Tailwind design tokens
- `[hosting-provider]` — Render, Railway, Fly.io, etc.
- `[database-provider]` — Supabase, PlanetScale, Neon, etc.
- `[SSO-provider]` — Auth0, Clerk, MSAL, etc.
- `[error_handler]()` — Your error response utility function
- `[search_pattern_helper]()` — Your safe search/LIKE query helper
- Project table entries — Replace with your actual projects and their stacks

### Adding a New Agent

Use `templates/agent-template.md` as a starting point. Key rules:

- Keep it under 140 lines
- Only include patterns Claude would get wrong without the instruction
- Set model based on task complexity (opus for reasoning, sonnet for implementation, haiku for checklists)
- Add `tools:` restriction if the agent should be read-only
- Include the Expertise Memory block at the bottom

### Adding a New Skill

Use `templates/skill-template.md` as a starting point. Key rules:

- Description under 250 chars, front-loaded with trigger keywords
- Use `disable-model-invocation: true` for skills with side effects (deploys, sends)
- Use `allowed-tools:` to restrict what the skill can do

## File Structure

```
the-agentic-developer/
├── README.md
├── agents/                              # 14 local + 2 plugin-inherited
│   ├── ai-integration-specialist.md     # AI/LLM patterns, prompts, SDKs (opus)
│   ├── api-architect.md                 # API design across frameworks (sonnet)
│   ├── canva-specialist.md              # Canva MCP for branded PDFs (opus)
│   ├── code-reviewer.md                 # Code quality + security review (opus)
│   ├── database-architect.md            # Schema, queries, migrations (opus)
│   ├── frontend-specialist.md           # React/Next.js/Vite frontend (sonnet)
│   ├── performance-optimizer.md         # Bottleneck analysis (sonnet)
│   ├── python-django-specialist.md      # Django/Flask backend (sonnet)
│   ├── security-auditor.md              # OWASP review + incident history (opus)
│   ├── sharepoint-graph-specialist.md   # MS Graph + SharePoint Drive/Lists/SPFx (opus)
│   ├── strategic-planner.md             # Architecture + planning (opus)
│   ├── systematic-debugger.md           # Root cause analysis (opus)
│   ├── tdd-engineer.md                  # Test-driven development (sonnet)
│   └── ui-ux-designer.md                # Design system + layout (opus)
│   # Plugin-inherited (not in this repo):
│   #   silent-failure-hunter, type-design-analyzer — from pr-review-toolkit
│
├── skills/                              # 14 custom skills
│   ├── 3d-logo/SKILL.md
│   ├── ai-digest-agent/SKILL.md
│   ├── brief/SKILL.md
│   ├── copy/SKILL.md
│   ├── decision-brief/SKILL.md
│   ├── delegate/SKILL.md
│   ├── file-emails/SKILL.md
│   ├── grep-all/SKILL.md                # cross-project regex search
│   ├── inbox-summary/SKILL.md
│   ├── qa-gate/SKILL.md
│   ├── refactor-ui/SKILL.md
│   ├── status/SKILL.md
│   ├── ui-ux-review/SKILL.md
│   └── update-all/SKILL.md
│
├── commands/                            # 6 loop commands
│   ├── agent-improvement.md
│   ├── email-drafter.md
│   ├── meeting-prep.md
│   ├── merge-conflict-watch.md
│   ├── vip-watch.md
│   └── weekly-review.md
│
├── hooks/                               # Production hooks
│   ├── destructive-guard.sh             # Block 12 categories of irreversible commands
│   └── lesson-capture-detector.sh       # Detect corrections, prompt lesson logging
│
├── scripts/                             # Helper scripts
│   ├── grep-all.sh                      # Backs the /grep-all skill
│   ├── rebuild-projects-txt.sh          # Generates projects.txt (canonical inventory)
│   └── eval/
│       └── agent-eval.py                # Synthetic-bug catch-rate harness
│
├── eval-fixtures/                       # Sample YAML fixtures (adapt for your agents)
│   ├── README.md
│   └── security/
│       ├── 001-sqli-fstring.yaml        # Planted: f-string SQL injection
│       └── 004-clean-parameterized.yaml # Clean: parameterized query (FP test)
│
├── templates/                           # Starter templates
│   ├── CLAUDE.md                        # Personal instructions template
│   ├── agent-template.md                # New agent starter
│   └── skill-template.md                # New skill starter
│
└── docs/
    ├── design-philosophy.md             # Deep dive on design decisions
    ├── advisor-hook.md                  # UserPromptSubmit advisor reminder config
    ├── destructive-guard-fix.md         # Post-mortem on two latent hook bugs
    └── eval-harness.md                  # Two-instrument eval system — architecture + baselines + limitations
```

## Stats

| Metric                 | Value                                                                                 |
| ---------------------- | ------------------------------------------------------------------------------------- |
| Agents                 | 16 (9 Opus, 5 Sonnet, 2 Inherit)                                                      |
| Skills                 | 14                                                                                    |
| Commands               | 6                                                                                     |
| Hooks                  | 3 (advisor reminder, destructive-guard, lesson-capture-detector)                      |
| Evaluation             | 2 instruments (routing + catch-rate), monthly cadence, sample fixtures + harness ship |
| Avg agent size         | ~140 lines (pure signal, no filler)                                                   |
| Description compliance | 100% under 250 chars                                                                  |
| Self-improvement       | Weekly audit + monthly cross-review + catch-rate trend + auto-capture corrections     |

## Contributing

This is a personal setup published as a reference. PRs welcome for:

- Fixing errors in templates
- Improving documentation
- Adding useful starter templates

Not looking for:

- Generic agent additions (keep it focused)
- Framework-specific agents (create your own repo for those)
- Changes to the design philosophy

## License

MIT
