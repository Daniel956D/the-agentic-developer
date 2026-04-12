#!/bin/bash
# Cross-project grep using system grep -rE. Reads project paths from
# ~/.claude/projects.txt and prints matches grouped by repo.
set -u

if [ $# -eq 0 ]; then
  echo "Usage: grep-all.sh <pattern> [extra grep flags]"
  exit 1
fi

PATTERN="$1"; shift
PROJECTS_FILE="$HOME/.claude/projects.txt"

if [ ! -f "$PROJECTS_FILE" ]; then
  bash "$HOME/.claude/scripts/rebuild-projects-txt.sh" >/dev/null
fi

EXCLUDES=(
  --exclude-dir=node_modules
  --exclude-dir=.git
  --exclude-dir=dist
  --exclude-dir=build
  --exclude-dir=.next
  --exclude-dir=__pycache__
  --exclude-dir=venv
  --exclude-dir=.venv
  --exclude-dir=.turbo
  --exclude-dir=coverage
  --exclude=*.tsbuildinfo
  --exclude=*.min.js
  --exclude=*.min.css
  --exclude=*.map
  --exclude=*.lock
  --exclude=package-lock.json
  --exclude=yarn.lock
  --exclude=pnpm-lock.yaml
  --exclude=*.log
)

TOTAL_LINES=0
MAX_TOTAL=300
MAX_PER_FILE=20

while IFS= read -r repo; do
  [ -z "$repo" ] && continue
  case "$repo" in '#'*) continue ;; esac
  [ -d "$repo" ] || continue

  name=$(basename "$repo")
  # Run grep, cap matches per file, count results
  matches=$(grep -rEn "${EXCLUDES[@]}" "$@" -- "$PATTERN" "$repo" 2>/dev/null \
    | awk -v max="$MAX_PER_FILE" -F: '
        { count[$1]++; if (count[$1] <= max) print }
      ' \
    | sed "s|^$repo/||")

  if [ -n "$matches" ]; then
    count=$(printf '%s\n' "$matches" | wc -l | tr -d ' ')
    printf '\n=== %s (%s matches) ===\n%s\n' "$name" "$count" "$matches"
    TOTAL_LINES=$((TOTAL_LINES + count + 2))
    if [ "$TOTAL_LINES" -ge "$MAX_TOTAL" ]; then
      printf '\n[output capped at %s lines — narrow your pattern for more]\n' "$MAX_TOTAL"
      break
    fi
  fi
done < "$PROJECTS_FILE"

if [ "$TOTAL_LINES" -eq 0 ]; then
  echo "No matches for: $PATTERN"
fi
