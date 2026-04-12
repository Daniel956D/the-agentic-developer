#!/bin/bash
# Detects correction patterns in user prompts and reminds Claude to log a lesson.
# Reads UserPromptSubmit hook input from stdin (JSON), checks the prompt for
# correction signals, and emits additionalContext if matched.

input=$(cat)
prompt=$(printf '%s' "$input" | /usr/bin/python3 -c 'import json,sys; print(json.load(sys.stdin).get("prompt",""))' 2>/dev/null)

[ -z "$prompt" ] && exit 0

# Lowercase for matching
lower=$(printf '%s' "$prompt" | tr '[:upper:]' '[:lower:]')

# Correction patterns — phrases that signal Danny is correcting Claude
patterns=(
  "no that's wrong"
  "no, that's wrong"
  "that's wrong"
  "that is wrong"
  "actually,"
  "i said"
  "i didn't say"
  "you misunderstood"
  "stop doing"
  "don't do"
  "you keep"
  "wrong again"
  "not what i"
  "you broke"
  "this is broken"
  "you missed"
  "you forgot"
)

matched=""
for p in "${patterns[@]}"; do
  case "$lower" in
    *"$p"*)
      matched="$p"
      break
      ;;
  esac
done

[ -z "$matched" ] && exit 0

reminder="LESSON CAPTURE TRIGGER: Danny's prompt contains a correction signal (\"$matched\"). Per CLAUDE.md auto-capture policy, after resolving this turn, append a new entry to ~/.claude/lessons-learned.md with: what you got wrong, the correction, why it happened, and category=correction. If the same lesson already exists, increment its hit count instead."

/usr/bin/python3 -c "
import json
print(json.dumps({
  'hookSpecificOutput': {
    'hookEventName': 'UserPromptSubmit',
    'additionalContext': '''$reminder'''
  }
}))
"
