---
name: inbox-summary
description: Quick triage summary of unread inbox emails — who sent what, what's urgent, what can wait. Use when the user says "check my inbox", "what's in my inbox", "inbox summary", "any important emails", or "triage my inbox".
allowed-tools: mcp__ms365__list-mail-folder-messages, mcp__ms365__list-mail-folders
---

# Inbox Summary

Scan the user's Outlook inbox and produce a prioritized triage summary — no filing, no drafting, just awareness.

## Rules

- **Always use `mailFolderId: "inbox"`** — never use `list-mail-messages`
- Fetch up to 50 most recent emails with `top: 50`
- If more than 50, note the total count but only triage the newest 50

## Triage Categories

Classify each email into one of these priority tiers:

### Needs Action

- From VIPs (configure your VIP list — e.g., executives, direct manager)
- Emails where the user is in the TO field (not CC) asking for a response or decision
- Meeting changes for today or tomorrow
- Anything flagged as high importance

### Worth Reading

- Internal @[company].com with substance (not auto-notifications)
- Replies to threads the user started
- Calendar invites for this week
- Vendor/external emails requiring acknowledgment

### Low Priority

- Newsletters, promotional
- Auto-notifications ([PM tool], SharePoint, system alerts)
- CC-only emails
- AI meeting summaries (informational)

## Output Format

```
## Inbox Triage — [count] unread

### Needs Action ([count])
- **[Sender]** — [Subject] — [1-line summary of what's needed]

### Worth Reading ([count])
- **[Sender]** — [Subject] — [1-line summary]

### Low Priority ([count])
- [count] newsletters, [count] notifications, [count] CC-only
```

Keep it scannable. One line per email max. The user wants to know what matters in 15 seconds.
