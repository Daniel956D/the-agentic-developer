---
name: status
description: Status updates from git, calendar, and email. Use for daily standups (/status) or cross-project snapshots (/status overview).
allowed-tools: Bash, mcp__ms365__get-calendar-view, mcp__ms365__list-mail-folder-messages
argument-hint: [daily|overview]
---

# Mode Detection

- `/status` or `/status daily` → **Daily mode** (last 24h, personal update)
- `/status overview` → **Overview mode** (last 7 days, cross-project snapshot)
- Default: **daily**

---

# Shared Data Sources

Both modes pull from these sources:

1. **Git repos** — daily uses current directory; overview scans all project directories
2. **Calendar** — MS365 MCP `get-calendar-view` with `timezone: "[Your/Timezone]"`
3. **Email** — MS365 MCP `list-mail-folder-messages` with `mailFolderId: "sentitems"`
4. **PM tool** — if your PM tool MCP tools are available, query for task movements; otherwise skip silently

---

# Daily Mode

## Gather Activity

### Git Activity

- Git log (last 24h): !`git log --oneline --since="yesterday" --all 2>/dev/null || echo "No git repo detected"`
- Changed files: !`git diff --stat HEAD~5 2>/dev/null || echo "No recent changes"`
- Current branch: !`git branch --show-current 2>/dev/null || echo "N/A"`
- Uncommitted work: !`git status --short 2>/dev/null || echo "Clean"`

### Calendar (Today)

Pull today's calendar using `get-calendar-view` with `timezone: "[Your/Timezone]"`. List meetings attended or upcoming.

### Email Activity

Check sent items for threads the user replied to or sent in the last 24 hours using `list-mail-folder-messages` with `mailFolderId: "sentitems"`. Summarize the top 3-5 threads by subject.

### PM Tool

If your PM tool MCP tools are available, query for tasks moved to "Done" or "In Progress" in the last 24 hours. If unavailable, skip silently.

## Output Format

From ALL activity above, write a concise status update:

1. **Completed**: What was finished — meetings attended, emails handled, code shipped, tasks closed
2. **In progress**: What's actively being worked on — open threads, current branch, upcoming meetings
3. **Blockers**: Anything preventing progress (if none, omit this section)

Rules:

- Write for a non-technical audience
- Use plain language — describe impact, not implementation details
- Keep it under 200 words
- Group by topic (e.g., project name, "Team Coordination", "Admin") not by source
- If a source has no activity, skip it silently

---

# Overview Mode

## Step 1: Scan Active Projects

Scan git repos in your project directories:

```bash
# Known project directories — customize this list
PROJECT_DIRS=(
  ~/projects/*/
  ~/Projects/*/
)

for dir in "${PROJECT_DIRS[@]}"; do
  [ -d "$dir/.git" ] || continue
  name=$(basename "$dir")
  echo "=== $name ==="
  git -C "$dir" log --oneline --since="7 days ago" --all 2>/dev/null | head -5
  echo "Branch: $(git -C "$dir" branch --show-current 2>/dev/null || echo 'N/A')"
  echo "Last commit: $(git -C "$dir" log -1 --format='%s (%ar)' 2>/dev/null || echo 'None')"
  echo ""
done
```

## Step 2: Check PM Tool

If your PM tool MCP tools are available, pull items updated in the last 7 days. If unavailable, skip silently.

## Step 3: Check Calendar Context

Pull this week's calendar using `get-calendar-view` with `timezone: "[Your/Timezone]"` to identify project-related meetings.

## Step 4: Check Recent Email Threads

Use `list-mail-folder-messages` with `mailFolderId: "sentitems"`, `top: 20` to see what the user has been responding to — indicates active project engagement.

## Output Format

```
## Project Status — Week of [date]

### [Project Name]
- **Activity:** [X commits this week / no commits]
- **Last change:** [most recent commit message + date]
- **Branch:** [current branch]
- **Status:** Active / Stale / Idle

### Summary
- [X] projects active this week
- Key focus areas: [topics from commits + meetings]
```

---

# Rules (Both Modes)

- Skip sources with no activity silently — never say "no git activity detected"
- **Stale** = no commits in 7+ days
- Keep each project to 3-4 lines max
- If a project directory doesn't exist, skip silently
