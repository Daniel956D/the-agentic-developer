# Design Philosophy

## Why This Setup Exists

Most Claude Code agent collections on GitHub follow the same pattern: hundreds of generic agents with titles like "You are an expert React developer" followed by 200 lines of best practices Claude already knows. They get stars because people want a shortcut, but they add minimal value over Claude's base capabilities.

This setup takes the opposite approach. Every line earns its place by containing information Claude would get wrong without it.

## Core Principles

### 1. Project-Specific Over Generic

Claude already knows React best practices, REST API design, and OWASP top 10. Putting these in an agent prompt wastes context and dilutes the instructions that actually matter — your specific conventions, your design tokens, your error handling patterns, your past incidents.

**Bad agent (generic):**

> Use proper HTTP status codes. 200 for success, 404 for not found...

**Good agent (specific):**

> Error responses use `[error_handler]('message')` — NEVER `f'{str(e)}'` which leaks internals.

### 2. Lean Over Comprehensive

The official Claude Code docs say: "For each line, ask: 'Would removing this cause Claude to make mistakes?' If not, cut it."

Our agents average 150 lines. The top GitHub repos average 50-100 lines of generic content padded to 300+. Shorter agents with real patterns outperform longer agents with textbook filler.

### 3. Right-Size Model Routing

Not every task needs Opus. The three-tier approach:

- **Opus** — Tasks requiring judgment: security audits, architectural decisions, code review, debugging
- **Sonnet** — Tasks requiring execution: implementation, testing, API design
- **Haiku** — Tasks requiring speed: performance checklists, simple analysis

This isn't about cost savings (though it helps). Faster models often produce better results on focused tasks because they're less likely to overthink simple problems.

### 4. Dispatch Threshold

Only dispatch agents for changes touching 3+ files OR security/data-critical code. Single-file changes get inline review. This prevents agent overhead on simple tasks — dispatching a security auditor to review a CSS change is waste, not diligence.

### 5. Expertise Compounds

Every agent reads a persistent expertise file on start and writes learnings on finish. Over hundreds of sessions, this creates a knowledge base specific to your projects that no generic template can match.

The expertise system has two tiers:

- **Recent Learnings** — FIFO queue, max 50 entries, auto-evicts oldest
- **Foundations** — Pinned patterns promoted after 3+ references, never evicted

### 6. Self-Improvement Is Built In

Static setups decay. Your projects evolve, frameworks update, new patterns emerge. Without maintenance, agents go stale.

This setup has three improvement layers:

- **Real-time** — When an agent gives stale advice, a `[BASE-UPDATE-NEEDED]` flag is logged
- **Weekly** — Friday audit scans all agents against actual project state
- **Monthly** — Independent AI cross-review rates all agents for quality

## What We Learned Building This

### Trimming generic content was the highest-impact change

When we rewrote the `api-architect` from 233 to 124 lines, it got better, not worse. The 109 lines we cut were REST best practices Claude already knows. What remained was project-specific patterns Claude needs.

### Skills are harder than agents

Agents have a clear identity and scope. Skills are procedural workflows that run inline — they're more like scripts. The best skills are focused (one thing well) and include error handling for when tools aren't available.

### The community validates this approach

We researched the top Claude Code repos before building:

- **wshobson/agents** (33k stars) uses the same model tiering pattern
- **lst97/claude-code-sub-agents** recommends tool restrictions on read-only agents
- **Anthropic's official docs** say "standard language conventions Claude already knows" should be excluded
- No successful repo uses 300-line generic agents

### Descriptions matter more than you think

Claude Code truncates skill/agent descriptions at 250 characters. If your trigger keywords are at character 260, Claude won't know when to dispatch your agent. Front-load the important words.

## Anti-Patterns We Avoided

1. **The textbook agent** — 200 lines of "always use semantic HTML" that Claude already knows
2. **The kitchen-sink skill** — One skill that tries to do everything
3. **The over-dispatcher** — Dispatching agents for every single change regardless of complexity
4. **The static setup** — Built once, never maintained, slowly going stale
5. **The bloat trap** — Adding agents/skills "just in case" instead of when real friction demands it
