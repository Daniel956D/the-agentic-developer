First, run `date +%u` to get the day of week (1=Mon, 7=Sun). If it's 6 or 7 (Saturday/Sunday), say nothing and stop.

Otherwise, check my inbox for new unread emails (mailFolderId: "inbox", filter: "isRead eq false", top 5). For each new email:

1. Read the full thread for context
2. Draft a concise, professional, friendly reply
3. Read my signature from ~/.claude/email-signature.html and append it
4. Save as a draft using create-reply-draft (NEVER send)
5. Report in this compact format:

**From:** [sender] | **Re:** [subject]
**Draft:** [1-line preview of your reply]

If no new unread emails, just say "No new emails." — nothing else.
