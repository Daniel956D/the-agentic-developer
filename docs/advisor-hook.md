# Advisor Reminder Hook

A lightweight `UserPromptSubmit` hook that injects a short reminder into Claude's context at the start of every prompt, nudging it to call its `advisor()` tool at two key checkpoints on non-trivial tasks.

## Why

Claude Code's server-side `advisor()` tool forwards the full session transcript to a stronger reviewer model for a second opinion. It's most valuable at two moments:

1. **After orientation, before substantive work** — catch a bad plan before writing code or committing to an interpretation
2. **Before declaring done** — sanity check the result with the full transcript as context

Without a reminder, it's easy to forget at exactly the moments it matters most. A `Stop` hook is too late — the work is already done. A `UserPromptSubmit` hook lands the reminder before planning even starts, so it actually shapes the approach.

## Design decisions

- **Single one-line `echo` command** — no external script, no dependencies, nothing to install
- **Outputs `hookSpecificOutput.additionalContext`** — this is the one hook output channel that injects text back into Claude's context. `systemMessage` only shows to the user; `decision: "block"` is too aggressive
- **Explicitly tells Claude to skip the check for simple lookups and short reactive follow-ups** — prevents the reminder from becoming noise on trivial turns
- **No state tracking** — the reminder fires on every prompt, and Claude decides whether to act on it. A stateful version (only remind if Claude didn't call advisor in the last N turns) is possible but adds script complexity for marginal benefit

## Settings.json snippet

Add this entry to the `hooks` object in `~/.claude/settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "echo '{\"hookSpecificOutput\":{\"hookEventName\":\"UserPromptSubmit\",\"additionalContext\":\"ADVISOR REMINDER: For non-trivial tasks (multi-step, writes, decisions, debugging), call advisor() after orientation and before substantive work, and again before declaring done. Skip for simple lookups or short reactive follow-ups.\"}}'"
          }
        ]
      }
    ]
  }
}
```

If you already have other hooks configured, merge this into the existing `hooks` object — don't replace it.

## Activating after install

Claude Code's settings watcher only picks up new hook events from directories it was already watching at session start. If the hook doesn't fire immediately after you edit settings.json:

1. Open `/hooks` once to reload config, or
2. Restart your session

Existing hooks keep working without a reload; only brand-new event types (like a first-time `UserPromptSubmit` entry) need the nudge.

## Verifying it's live

When the hook fires, Claude sees a `<system-reminder>` block in the user turn containing the text `ADVISOR REMINDER: ...`. The reminder appears at the top of every prompt submission, injected before Claude processes your message.

You can also pipe-test the command directly:

```bash
echo '{}' | bash -c 'echo "{\"hookSpecificOutput\":{\"hookEventName\":\"UserPromptSubmit\",\"additionalContext\":\"ADVISOR REMINDER: ...\"}}"' | jq .
```

Valid JSON output means the command will work as a hook.

## Tuning

If the reminder feels too noisy or too quiet, options include:

- **Narrow the trigger** — wrap the echo in a shell conditional that inspects stdin (the JSON payload includes the user prompt) and only injects on prompts over a length threshold
- **Add a Stop backstop** — a second hook on the `Stop` event that outputs `decision: "block"` with a reminder to call advisor if it wasn't called yet. Risks loops on trivial tasks; only add if the primary reminder is getting ignored
- **Vary the message** — swap the static echo for a small script that picks a different reminder variant based on the day, project, or a rotating counter, so the reminder doesn't blur into the background

Keep it simple unless the simple version stops working.
