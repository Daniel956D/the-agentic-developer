First, run `date +%u` to get the day of week (1=Mon, 7=Sun). If it's 6 or 7 (Saturday/Sunday), say nothing and stop.

Otherwise, check my calendar (timezone: [Your/Timezone]) for meetings starting in the next 45 minutes.

For each upcoming meeting, report:
**Meeting:** [title] at [time]
**With:** [attendees]
**Prep:**

1. Check inbox for recent emails from attendees and summarize any relevant context in 1 line.
2. Use Circleback (mcp\_\_plugin_circleback_circleback) to search for recent meeting notes involving these attendees. Summarize any open action items or recent discussion points in 1-2 lines. If Circleback is not authenticated or returns no results, skip silently.

If no meetings soon, just say "No upcoming meetings." — nothing else.
