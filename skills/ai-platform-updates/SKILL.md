---
name: ai-platform-updates
description: Add rows to an "AI Platform Updates" workbook with automatic color-coding by product family (Claude / ChatGPT / Gemini). Use when the user asks to log a new AI platform release, update the sheet, or refresh the weekly sweep.
---

# AI Platform Updates — Sheet Maintenance

Maintains `[your-workbook-path]/AI Platform Updates.xlsx`. The workbook has three sheets:

- **Updates** — headliner / day-to-day impact changes (newest on top)
- **Minor Updates** — polish, fixes, and edge cases (newest on top)
- **README** — column definitions, sources, and the color legend

## Color coding (enforced automatically)

| Family  | Fill            | Product values that match                 |
| ------- | --------------- | ----------------------------------------- |
| Claude  | peach `#FFF4E6` | anything containing "claude"              |
| ChatGPT | green `#E6F4EA` | anything containing "chatgpt" or "openai" |
| Gemini  | blue `#E6F0FA`  | anything containing "gemini" or "gemma"   |

Coloring is applied by the helper script on every insert — you do not need to think about it. If a new product doesn't fit these families, extend the `classify()` function in the script.

## How to insert rows

Always use the helper script. Never hand-edit the xlsx via ad-hoc openpyxl snippets — it's easy to forget the style copy, column widths, or the color fill.

```bash
echo '{
  "rows": [
    {
      "sheet": "Updates",
      "date": "2026-04-09",
      "product": "Claude Code",
      "category": "Feature",
      "summary": "v2.1.98 — Interactive Google Vertex AI setup wizard",
      "why": "Guided GCP auth, project/region config, and model pinning",
      "source": "https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md"
    }
  ]
}' | python3 [path-to-helper-script]/ai-platform-updates.py insert
```

**Input fields:**

- `sheet` (optional, default `"Updates"`) — `"Updates"` or `"Minor Updates"`
- `date` — release date from the vendor, `YYYY-MM-DD`
- `product` — e.g. `Claude Code`, `Claude API/Models`, `ChatGPT`, `Gemini App`, `Gemini API/Models`
- `category` — `Feature` / `Fix` / `Model` / `Pricing` / `Deprecation` / `Improved` / `Changed` / `Other`
- `summary` — one sentence, what changed
- `why` — plain-English impact for your workflow
- `source` — official vendor release notes URL
- `added` (optional) — defaults to today in `YYYY-MM-DD`

The script downloads the current workbook, inserts each row at the top of its target sheet, copies styling from the existing top row so formatting stays consistent, colorizes by family, and uploads back. Batch multiple rows in one call so there's only one download/upload round trip.

## Where to route updates

**Updates sheet** — anything that changes what you can do, not just polish. Examples:

- New model launches or deprecations
- New features (voice mode, interactive wizards, new integrations)
- Pricing / tier changes
- Security fixes that change permission behavior
- UI changes that affect the core workflow

**Minor Updates sheet** — smaller items grouped thematically, not one row per bullet:

- Edge-case bug fixes (wildcard matching, picker polish, etc.)
- Internal plumbing (OTEL spans, LSP identification, OAuth refresh quirks)
- Terminal / input artifacts
- Memory leaks, race conditions, obscure config flags

**Grouping rule:** on the Minor sheet, 40 bullets from a single release should become ~5–8 thematic rows, not 40 separate rows. The goal is "scannable summary", not "complete change log" — that's what the source link is for.

## Weekly sweep workflow

When running a fresh sweep across Claude / ChatGPT / Gemini:

1. **Check existing entries first** to find the last date per product family:
   ```bash
   python3 [path-to-helper-script]/ai-platform-updates.py download
   python3 -c "
   from openpyxl import load_workbook
   ws = load_workbook('/tmp/ai_platform_updates.xlsx')['Updates']
   seen = set()
   for row in ws.iter_rows(min_row=2, values_only=True):
       if row[1] and row[1] not in seen:
           print(row[1], '→ latest:', row[0])
           seen.add(row[1])
   "
   ```
2. **Fetch each vendor's changelog** only from that date forward:
   - Claude Code: `gh api repos/anthropics/claude-code/contents/CHANGELOG.md` — most reliable, no 403
   - Claude API: <https://platform.claude.com/docs/en/release-notes/api>
   - ChatGPT: <https://releasebot.io/updates/openai/chatgpt> (the official `help.openai.com` page geo/bot-blocks direct fetches with 403)
   - Gemini API: <https://ai.google.dev/gemini-api/docs/changelog>
   - Gemini App: <https://gemini.google/release-notes/>
3. **Classify each item** as headliner → Updates, or small → Minor Updates.
4. **Batch everything into one `insert` call** so the sheet is locked once.

## Other commands

```bash
python3 [path-to-helper-script]/ai-platform-updates.py download   # fetch to /tmp/ai_platform_updates.xlsx
python3 [path-to-helper-script]/ai-platform-updates.py upload     # push /tmp copy back
python3 [path-to-helper-script]/ai-platform-updates.py recolor    # re-apply fills to all rows (idempotent)
```

`recolor` is useful if someone edits the sheet manually and adds uncolored rows, or if the family classifier is extended to new products.

## Known failure mode: 423 Locked

If the upload returns `HTTPError: 423 Client Error: Locked`, the file is open somewhere holding a write lock:

- **Most common:** Excel desktop has the file open. Close it and retry.
- Cloud sync client is mid-write. Wait ~10 seconds.
- Another session already has an upload in flight.

The script retries up to 5 times with exponential backoff (1s → 16s), then fails with a helpful message. If it fails after retries, close Excel and re-run the command — don't try to force it.

## Companion script

The helper script (`ai-platform-updates.py`) is not included in this repo — it's a thin openpyxl wrapper that knows how to download/upload your workbook from your cloud storage provider. The skill shows the _pattern_: log AI platform releases into a structured spreadsheet with family-based color coding. Adapt the script to your own storage (OneDrive/Drive/S3/local) and point `[path-to-helper-script]` at it.
