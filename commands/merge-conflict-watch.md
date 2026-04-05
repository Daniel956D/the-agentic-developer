First, run `date +%u` to get the day of week (1=Mon, 7=Sun). If it's 6 or 7 (Saturday/Sunday), say nothing and stop.

Otherwise, scan project directories (~/projects/, ~/Projects/, ~/Documents/GitHub/) for git repos with active worktrees. For each repo, run `git -C <repo> worktree list`. If only one worktree exists, skip that repo.

For each repo with multiple worktrees, compare files modified in each worktree's branch (`git diff main...{branch} --name-only`) against other worktree branches to detect overlapping file changes.

If overlapping files found:
**Collision risk:** [filename] modified in both [current branch] and [worktree branch]

If no overlaps, say "No merge conflicts detected." — nothing else.
