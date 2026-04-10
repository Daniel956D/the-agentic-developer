# The Agentic Developer

A production-grade Claude Code configuration with 12 specialized agents, 14 custom skills, 6 loop commands, an advisor-reminder hook, and a self-improving weekly audit system. This is how I build software with AI — not as a novelty, but as core infrastructure.

Built for shipping across Django, Flask, Next.js, React/Vite, Python utilities, and Node.js integrations. Every agent is grounded in real project patterns, real incident history, and real conventions. The setup compounds knowledge over time through persistent expertise files and automated weekly audits.

> **This isn't a collection of generic prompts.** Most Claude Code agent repos are 200 lines of "You are an expert React developer" that Claude already knows. This setup contains only what Claude would get wrong without it — project-specific patterns, real design tokens, actual incident history, and proven conventions.

## What's Inside

### 12 Specialized Agents (`agents/`)

Tiered by model for cost efficiency:

| Tier       | Model          | Agents                                                                                                                                     | Purpose                          |
| ---------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------- |
| **Opus**   | Deep reasoning | ai-integration-specialist, code-reviewer, database-architect, security-auditor, strategic-planner, systematic-debugger, ui-ux-designer (7) | Architecture, security, strategy |
| **Sonnet** | Implementation | api-architect, frontend-specialist, python-django-specialist, tdd-engineer (4)                                                             | Building and testing             |
| **Haiku**  | Fast checks    | performance-optimizer (1)                                                                                                                  | Checklist-driven analysis        |

**Key design principle:** Agents contain only project-specific patterns — not generic best practices Claude already knows. A 120-line agent with real patterns outperforms a 300-line agent padded with textbook content.

### 14 Custom Skills (`skills/`)

| Skill                 | Purpose                                                                |
| --------------------- | ---------------------------------------------------------------------- |
| `qa-gate`             | Universal QA — dispatches review agents based on output type           |
| `decision-brief`      | Multi-agent deliberation with structured debate and voting             |
| `delegate`            | Fire-and-forget multi-agent execution with phased dispatch and retries |
| `status`              | Daily standups or cross-project snapshots from git/calendar/email      |
| `file-emails`         | Auto-file inbox emails into Outlook folders                            |
| `inbox-summary`       | Quick triage of unread inbox                                           |
| `refactor-ui`         | Safely restructure existing UI without breaking functionality          |
| `ui-ux-review`        | Audit pages for design quality and accessibility                       |
| `copy`                | Review text for clarity, tone, and impact                              |
| `brief`               | Translate technical work into executive summaries                      |
| `update-all`          | Staged package updates with dry-run preview                            |
| `ai-digest-agent`     | Weekly AI/automation digest curation                                   |
| `ai-platform-updates` | Log Claude/ChatGPT/Gemini releases into a color-coded spreadsheet      |
| `3d-logo`             | Interactive 3D logos with Three.js                                     |

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

### Advisor Reminder Hook

A `UserPromptSubmit` hook in `~/.claude/settings.json` injects a short reminder at the start of every prompt, nudging Claude to call its `advisor()` second-opinion tool at two checkpoints on non-trivial tasks:

1. **After orientation, before substantive work** — catch bad plans before writing code
2. **Before declaring done** — sanity check the result with the full transcript as context

The reminder explicitly tells Claude to skip the check for simple lookups and short reactive follow-ups, so it doesn't become noise. The hook is a one-line `echo` that emits `hookSpecificOutput.additionalContext` — no external script required. See `docs/advisor-hook.md` for the exact settings.json snippet.

### Self-Improvement System

The setup gets smarter every week through three layers:

1. **Real-time feedback** — When an agent gives stale advice, a `[BASE-UPDATE-NEEDED]` flag is logged to its expertise file
2. **Weekly audit** (`/agent-improvement`) — Every Friday, scans all agents against actual project state, flags drift, auto-fixes minor issues
3. **Monthly Codex cross-review** — First Friday of each month, dispatches an independent AI reviewer to rate all agents 1-10

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
claude-code-setup/
├── README.md
├── agents/                          # 12 specialized agents
│   ├── ai-integration-specialist.md # AI/LLM patterns, prompts, SDKs (opus)
│   ├── api-architect.md             # API design across frameworks (sonnet)
│   ├── code-reviewer.md             # Code quality + security review (opus)
│   ├── database-architect.md        # Schema, queries, migrations (opus)
│   ├── frontend-specialist.md       # React/Next.js/Vite frontend (sonnet)
│   ├── performance-optimizer.md     # Bottleneck analysis (haiku)
│   ├── python-django-specialist.md  # Django/Flask backend (sonnet)
│   ├── security-auditor.md          # OWASP review + incident history (opus)
│   ├── strategic-planner.md         # Architecture + planning (opus)
│   ├── systematic-debugger.md       # Root cause analysis (opus)
│   ├── tdd-engineer.md              # Test-driven development (sonnet)
│   └── ui-ux-designer.md            # Design system + layout (opus)
│
├── skills/                          # 14 custom skills
│   ├── 3d-logo/SKILL.md
│   ├── ai-digest-agent/SKILL.md
│   ├── ai-platform-updates/SKILL.md
│   ├── brief/SKILL.md
│   ├── copy/SKILL.md
│   ├── decision-brief/SKILL.md
│   ├── delegate/SKILL.md
│   ├── file-emails/SKILL.md
│   ├── inbox-summary/SKILL.md
│   ├── qa-gate/SKILL.md
│   ├── refactor-ui/SKILL.md
│   ├── status/SKILL.md
│   ├── ui-ux-review/SKILL.md
│   └── update-all/SKILL.md
│
├── commands/                        # 6 loop commands
│   ├── agent-improvement.md
│   ├── email-drafter.md
│   ├── meeting-prep.md
│   ├── merge-conflict-watch.md
│   ├── vip-watch.md
│   └── weekly-review.md
│
├── templates/                       # Starter templates
│   ├── CLAUDE.md                    # Personal instructions template
│   ├── agent-template.md            # New agent starter
│   └── skill-template.md            # New skill starter
│
└── docs/
    ├── design-philosophy.md         # Deep dive on design decisions
    └── advisor-hook.md              # UserPromptSubmit advisor reminder config
```

## Stats

| Metric                 | Value                               |
| ---------------------- | ----------------------------------- |
| Agents                 | 12 (7 Opus, 4 Sonnet, 1 Haiku)      |
| Skills                 | 14                                  |
| Commands               | 6                                   |
| Hooks                  | 1 (advisor reminder)                |
| Avg agent size         | 150 lines (pure signal, no filler)  |
| Description compliance | 100% under 250 chars                |
| Self-improvement       | Weekly audit + monthly cross-review |

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
