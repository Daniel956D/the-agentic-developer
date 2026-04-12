---
name: grep-all
description: Search a regex pattern across every project in ~/.claude/projects.txt, grouped by repo. Use when answering "how did I do X in another project" or "where else have I used this pattern" — collapses cross-repo archeology into one command.
allowed-tools: Bash
disable-model-invocation: true
argument-hint: [pattern] [optional: --include='*.tsx' or any other grep flag]
---

# Cross-Project grep

Runs `grep -rE` across every project in `~/.claude/projects.txt`, grouped by repo with match counts. Zero dependencies — uses system grep, no ripgrep required.

## Run

```bash
bash ~/.claude/scripts/grep-all.sh $ARGUMENTS
```

## Notes

- Output is capped at 300 lines total and 20 matches per file to stay scannable. If a hit looks promising, navigate to the repo and grep deeper there.
- Skips `node_modules`, `.git`, `dist`, `build`, `.next`, `__pycache__`, `venv`, `.venv` automatically.
- Pattern uses `grep -E` (extended regex). Pass extra `grep` flags after the pattern: `/grep-all "useState" --include='*.tsx'`, `/grep-all "GraphServiceClient" -i`.
- Reads `~/.claude/projects.txt` (canonical 16-project inventory). To refresh, run `bash ~/.claude/scripts/rebuild-projects-txt.sh`.
