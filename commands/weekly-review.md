First, run `date +%u` to get the day of week (1=Mon, 7=Sun). If it's 6 or 7 (Saturday/Sunday), say nothing and stop.

Generate a weekly status summary covering the last 7 days. Gather from these sources:

1. **Git activity**: For each project in ~/projects/, ~/Projects/, and ~/Documents/GitHub/ that has a .git directory, run `git log --oneline --after="7 days ago" --all` to get the week's commits. Skip repos with no activity.

2. **Agent dispatches**: Check if any agent-expertise files in ~/.claude/agent-expertise/ were modified in the last 7 days. If so, list which agents were used and what they learned. Otherwise omit this section.

3. **Calendar recap**: Query calendar for the past 7 days (timezone: [Your/Timezone]) to list meetings attended.

Output format:

**Week of [date range]**

**Completed**

- [Project]: [what was done, plain language]
- ...

**Agent Activity**

- [agent]: [what it reviewed/produced]
- ...

**Meetings Attended**

- [count] meetings ([list key ones])

**Carry Forward**

- [any incomplete handoffs or in-progress branches]

Keep it under 200 words. Write for a non-technical audience. Lead with impact, not implementation details.

## Friday Agent Improvement

If today is Friday (`date +%u` = 5), after generating the weekly review, automatically run the agent improvement cycle by invoking `/agent-improvement --force`. This audits all agents and skills for drift, staleness, and improvement opportunities. Present the improvement report after the weekly review.
