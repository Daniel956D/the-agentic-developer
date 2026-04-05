---
name: file-emails
description: File all inbox emails into appropriate Outlook folders based on sender, subject, and content. Use when the user says "file my emails", "clean my inbox", "organize my emails", or "sort my inbox".
allowed-tools: mcp__ms365__list-mail-folder-messages, mcp__ms365__list-mail-folders, mcp__ms365__list-mail-child-folders, mcp__ms365__move-mail-message
---

# File Emails

Reads all emails in the user's Outlook inbox and moves each one to the appropriate subfolder based on sender, subject, and content.

## Rules

- **Always use `mailFolderId: "inbox"`** — never use `list-mail-messages` (pulls from all folders including Junk)
- Fetch emails in batches of 50 using `top: 50` and paginate with `skip` until inbox is empty
- Fetch all inbox child folders first to build the folder map
- Move all emails in parallel batches of 10 (max tool calls per message)
- After all moves, verify inbox is empty with a final check
- If new emails arrive during filing, file those too

## Folder Mapping

Match emails to folders using sender domain, sender name, and subject keywords. Customize this table to match your Outlook folder structure:

| Signal                                     | Folder          |
| ------------------------------------------ | --------------- |
| [VIP_NAME] — directive/policy emails       | Leadership      |
| [VIP_NAME] — forwarded info, general       | Team            |
| Internal @[company].com — general team     | Internal Team   |
| Internal — safety, procedures              | Internal Team   |
| Internal — engineering, design review      | Engineering     |
| Meeting accepts/cancels/invites            | Meeting Invites |
| AI meeting summaries (Read, Otter, etc.)   | Meetings        |
| [PM tool] notifications                    | Notifications   |
| IT/help desk emails                        | IT & Security   |
| Tech newsletters (Google, Microsoft, etc.) | IT Related      |
| Status page alerts (Claude, AWS, etc.)     | Notifications   |
| Recruiting/interview/job related           | Recruiting      |
| Travel/hotel bookings                      | Travel          |
| Expense management tool                    | Expenses        |
| Food/catering orders                       | Catering        |
| Restaurant reservations                    | Reservations    |
| Gift orders, office supplies               | Receipts        |
| Amazon, vendor orders                      | Receipts        |
| Accounts Payable, invoices                 | Expenses        |
| Donations, sponsorship                     | Donations       |
| ERP notifications                          | ERP             |
| Newsletters, promotional                   | Newsletters     |
| Events (company events, town halls)        | Events          |
| Event planning (coordination, volunteers)  | Event Planning  |
| Vendors (external business)                | Vendors         |
| SharePoint, OneDrive admin                 | IT & Security   |
| Calendar alerts (from self)                | Notifications   |

## Ambiguous Emails

If an email doesn't clearly match any folder, file to **Other**. Never leave emails in inbox.

## Process

1. Fetch all inbox child folders → build `displayName → id` map
2. Fetch all inbox emails (paginate with `top: 50`)
3. Classify each email using the mapping above
4. Move in parallel batches of 10
5. Final verification: re-fetch inbox, repeat if not empty
6. Report summary: count per folder + total filed
