First, run `date +%u` to get the day of week (1=Mon, 7=Sun). If it's 6 or 7 (Saturday/Sunday), say nothing and stop.

Otherwise, read project paths from `~/.claude/projects.txt` (one path per line, ignore lines starting with `#`). For each path, run `git -C <path> worktree list`. If only one worktree exists, skip that repo. If `projects.txt` is missing, regenerate it via `bash ~/.claude/scripts/rebuild-projects-txt.sh` and then proceed.

For each repo with multiple worktrees, compare files modified in each worktree's branch (`git diff main...{branch} --name-only`) against other worktree branches to detect overlapping file changes.

If overlapping files found:
**Collision risk:** [filename] modified in both [current branch] and [worktree branch]

If no overlaps, say "No merge conflicts detected." — nothing else.
