#!/usr/bin/env bash
#
# destructive-guard.sh — PreToolUse hook for Bash
#
# Warns on destructive commands that are hard to reverse.
# Returns exit code 2 to block, 0 to allow.
# Complements security-gate.sh (which catches secrets).
#

set -uo pipefail

# Read hook input from stdin
INPUT=$(cat)

# Extract the command from tool input
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null) || true

# Exit early if no command
[[ -z "$COMMAND" ]] && exit 0

# Colors
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m'

# --- Destructive patterns to block ---
# Each entry: pattern:::description
# Separator is ':::' (not '|') so regex alternation can use '|' freely.
# Patterns are checked against the FIRST LINE of the command only,
# to avoid false positives from strings inside heredocs/scripts.
DESTRUCTIVE_PATTERNS=(
    'rm -rf /([[:space:]]|$):::Recursive force-delete from root'
    'rm -rf ~/?([[:space:]]|$):::Recursive force-delete of home directory'
    'rm -rf \.([[:space:]]|$):::Recursive force-delete of current directory'
    'rm -rf \*:::Recursive force-delete wildcard'
    'git push --force origin (main|master):::Force push to main/master'
    'git push -f origin (main|master):::Force push to main/master'
    'git reset --hard:::Hard reset discards all uncommitted changes'
    'git clean -f[^i]:::Force clean removes untracked files'
    'git checkout -- \.:::Discard all working directory changes'
    'git restore \.[[:space:]]*$:::Discard all working directory changes'
    'mkfs\.:::Format filesystem'
    'chmod -R 777:::Insecure recursive permission change'
    'kubectl delete namespace:::Kubernetes namespace deletion'
    'docker system prune -a:::Docker full prune'
)

# Extract just the first line for pattern matching
# This prevents false positives from heredocs, Python scripts, etc.
FIRST_LINE=$(echo "$COMMAND" | head -1)

for entry in "${DESTRUCTIVE_PATTERNS[@]}"; do
    pattern="${entry%%:::*}"
    description="${entry##*:::}"

    if echo "$FIRST_LINE" | grep -qiE "$pattern" 2>/dev/null; then
        echo -e "${RED}⚠️  BLOCKED${NC}: Destructive command detected."
        echo -e "${YELLOW}Pattern: ${description}${NC}"
        echo -e "${YELLOW}Command: ${COMMAND}${NC}"
        echo -e "${YELLOW}If this is intentional, ask Danny to confirm before proceeding.${NC}"
        echo '{"decision": "block", "reason": "'"$description"'. Confirm with user before proceeding."}'
        exit 2
    fi
done

# Allow the command
exit 0
