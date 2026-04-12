#!/bin/bash
# Rebuild ~/.claude/projects.txt by scanning known project locations and
# deduplicating clones by git remote URL (keeping the most recently-active clone).
#
# Customize ROOT_CANDIDATES below with your own repos that live in $HOME root.
# Standard ~/projects/* and ~/Documents/GitHub/* are scanned automatically.
set -e

OUT="$HOME/.claude/projects.txt"

/usr/bin/python3 - <<'PY' > /tmp/projects-body.txt
import os, subprocess, pathlib
home = pathlib.Path.home()
candidates = []

# Standard locations under ~/projects/
for d in (home / 'projects').glob('*'):
    if (d / '.git').exists():
        candidates.append(d)

# Older clones under ~/Documents/GitHub/
gh_dir = home / 'Documents' / 'GitHub'
if gh_dir.is_dir():
    for d in gh_dir.glob('*'):
        if (d / '.git').exists():
            candidates.append(d)

# Standalone clones in $HOME root.
# Replace the example list with the names of your own repos.
ROOT_CANDIDATES = [
    # 'my-side-project',
    # 'client-work-repo',
]
for name in ROOT_CANDIDATES:
    p = home / name
    if (p / '.git').exists():
        candidates.append(p)

def remote(p):
    try:
        return subprocess.check_output(
            ['git','-C',str(p),'remote','get-url','origin'],
            stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return str(p)

def last_commit_ts(p):
    try:
        return int(subprocess.check_output(
            ['git','-C',str(p),'log','-1','--format=%ct'],
            stderr=subprocess.DEVNULL, text=True).strip())
    except Exception:
        return 0

# Group by remote URL, keep most-recently-active clone
groups = {}
for p in candidates:
    groups.setdefault(remote(p), []).append(p)

picks = [max(paths, key=last_commit_ts) for paths in groups.values()]
picks.sort(key=lambda p: p.name)
for p in picks:
    print(p)
PY

today=$(date +%Y-%m-%d)
{
  echo "# Canonical project inventory for Claude Code loop commands."
  echo "#"
  echo "# Format: one absolute path per line. Lines starting with # are comments."
  echo "# Generated $today by ~/.claude/scripts/rebuild-projects-txt.sh"
  echo "# Dedup rule: when the same git remote is checked out at multiple paths,"
  echo "# the most-recently-active clone is the canonical one."
  echo "#"
  echo "# Loops/scripts that read this file: agent-improvement, weekly-review, merge-conflict-watch, grep-all."
  echo ""
  cat /tmp/projects-body.txt
} > "$OUT"

rm -f /tmp/projects-body.txt
echo "Wrote $(grep -cv '^#\|^$' "$OUT") projects to $OUT"
