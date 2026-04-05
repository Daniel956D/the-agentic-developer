First, run `date +%u` to get the day of week (1=Mon, 7=Sun). If it's 6 or 7 (Saturday/Sunday), say nothing and stop.

Otherwise, check my inbox (mailFolderId: "inbox", filter: "isRead eq false", top 10) for new unread emails from your VIP list only.

Configure your VIP list here (replace with actual email addresses):

- [vip1@company.com]
- [vip2@company.com]

For each VIP email found, report:
**From:** [name] | **Re:** [subject] | **Urgent?** [yes/no]
**Summary:** [1 line]

If none, just say "No new VIP emails." — nothing else.
