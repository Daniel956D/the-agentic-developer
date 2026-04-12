First, run `date +%u` to get the day of week (1=Mon, 7=Sun). If it's NOT 5 (Friday), tell the user: "Agent improvement runs on Fridays. Run `/agent-improvement` on Friday, or use `/agent-improvement --force` to run now." If $ARGUMENTS contains "--force", skip the day check and proceed.

Run the full agent & skill improvement cycle. This audits all agents and skills for drift, staleness, and improvement opportunities.

## Phase 1: Codebase Snapshot

Scan active projects to build current-state picture:

```bash
# Read canonical project list (regenerate if missing)
[ -f ~/.claude/projects.txt ] || bash ~/.claude/scripts/rebuild-projects-txt.sh
grep -v '^#\|^$' ~/.claude/projects.txt | while read -r dir; do
  [ -d "$dir/.git" ] || continue
  name=$(basename "$dir")
  last_commit=$(git -C "$dir" log --oneline -1 --format="%ar" 2>/dev/null || echo "unknown")
  stack=""
  [ -f "$dir/manage.py" ] && stack="$stack django"
  { [ -f "$dir/next.config.ts" ] || [ -f "$dir/next.config.js" ]; } && stack="$stack nextjs"
  [ -f "$dir/sanity.config.ts" ] && stack="$stack sanity"
  [ -f "$dir/vite.config.ts" ] && stack="$stack vite"
  [ -f "$dir/requirements.txt" ] && stack="$stack python"
  [ -f "$dir/package.json" ] && stack="$stack node"
  echo "$name | $last_commit |$stack"
done
```

## Phase 2: Agent Drift Detection

For each agent in `~/.claude/agents/*.md`:

1. Read the agent file
2. Check project references against Phase 1 results — flag missing or deleted projects
3. Check stack references — flag frameworks no longer in use or new ones not covered
4. Check description length — flag if over 250 chars
5. Check `~/.claude/agent-expertise/<agent-name>.md` for `[BASE-UPDATE-NEEDED]` flags

Score each: **Green** (matches reality), **Yellow** (minor drift), **Red** (significant drift)

## Phase 3: Skill Health Check

For each skill in `~/.claude/skills/*/SKILL.md`:

1. Check for stale agent references (agents that were renamed or removed)
2. Check description length — flag if over 250 chars
3. Check for hardcoded paths that no longer exist

## Phase 4: Expertise & Lessons Review

1. Read each `~/.claude/agent-expertise/*.md` — count entries, check for `[BASE-UPDATE-NEEDED]` flags, find promotion candidates (3+ references)
2. Read `~/.claude/lessons-learned.md` — check for agent-related corrections, hit counts at 3+ ready for CLAUDE.md promotion

## Phase 5: Codex Cross-Review (monthly — first Friday only)

Run `date +%d` to get day of month. If day is 1-7 (first Friday of the month), dispatch Codex for a quality rating of all agents. Otherwise skip this phase.

When running: use `/codex:rescue` to rate all agents 1-10 with brief justification. Compare to previous month's scores if available.

## Phase 6: Generate Report

```
## Agent & Skill Improvement Report — [date]

### Health Summary
| Agent/Skill | Status | Issue |
|-------------|--------|-------|

### Drift Detected
[List any Yellow/Red items with specific fixes needed]

### Expertise Highlights
[New learnings, promotions, BASE-UPDATE flags]

### Lessons This Week
[Agent-related corrections]

### Codex Review (monthly)
[Scores if first Friday, otherwise "Next review: [date]"]

### Recommendations
[Prioritized improvements — most impactful first]

### Stats
Agents: [N] | Skills: [N] | Expertise entries: [N] | Drift: [N yellow, N red]
```

## Phase 7: Apply Fixes

- **Green items**: No action needed
- **Yellow items**: Apply fixes automatically (update project lists, fix stale references)
- **Red items**: Present to the user for approval before changing

After applying fixes, show a summary of what was changed.

## Rules

- NEVER modify agent behavior/personality — only update facts
- NEVER auto-fix Red issues — always ask the user first
- Keep the report scannable in under 2 minutes
- If a new project is detected that no agent covers, recommend which agent should add it
