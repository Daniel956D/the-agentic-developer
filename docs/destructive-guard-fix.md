# `destructive-guard.sh` — two latent bugs and the fix

In April 2026 I traced into my own `destructive-guard.sh` after it blocked a legitimate `rm -rf /Users/me/projects/old-clone` deletion. I found two bugs that had been silently broken since the hook was written. The second one was safety-critical.

## Bug 1: false positives on every absolute-path delete

The original pattern was:

```bash
'rm -rf /|Recursive force-delete from root'
```

The intent was to catch `rm -rf /` (root deletion). But in regex, `rm -rf /` matches **any** command starting with `rm -rf /` — including completely safe deletions like:

```bash
rm -rf /tmp/test
rm -rf /Users/me/projects/old-clone
```

Same problem applied to `rm -rf ~/` (matched any home-relative delete) and `rm -rf .` (matched any cwd-relative delete).

**Fix:** anchor the pattern to whitespace or end-of-line so `/` only matches as a complete argument:

```bash
'rm -rf /([[:space:]]|$):::Recursive force-delete from root'
'rm -rf ~/?([[:space:]]|$):::Recursive force-delete of home directory'
'rm -rf \.([[:space:]]|$):::Recursive force-delete of current directory'
```

## Bug 2 (safety-critical): pattern definitions silently mangled by the parser

Each entry in the original `DESTRUCTIVE_PATTERNS` array used `|` as the separator between regex and description:

```bash
DESTRUCTIVE_PATTERNS=(
    'rm -rf /|Recursive force-delete from root'
    'git push --force origin (main|master)|Force push to main/master'
    ...
)
```

The script then split each entry on `|`:

```bash
pattern="${entry%%|*}"
description="${entry##*|}"
```

`%%|*` strips everything from the **first** `|` onward. So for the entry:

```
git push --force origin (main|master)|Force push to main/master
```

…the parsed pattern becomes:

```
git push --force origin (main
```

That's an unclosed regex group. `grep -E` either errors silently or never matches. **The force-push-to-main blocker was bypassable from day one.** Anyone who copy-pasted this hook from a popular template was running unprotected.

The fix above introduces `([[:space:]]|$)` into the regex itself, which has the same `|` problem — so I had to fix the parser too.

**Fix:** change the separator from `|` to `:::` so regex alternation can use `|` freely:

```bash
DESTRUCTIVE_PATTERNS=(
    'rm -rf /([[:space:]]|$):::Recursive force-delete from root'
    'git push --force origin (main|master):::Force push to main/master'
    ...
)

for entry in "${DESTRUCTIVE_PATTERNS[@]}"; do
    pattern="${entry%%:::*}"
    description="${entry##*:::}"
    ...
done
```

## Test cases (19 total)

After the fix, every dangerous case is blocked and every legitimate case is allowed:

**Must block:**

- `rm -rf /`
- `rm -rf ~`, `rm -rf ~/`
- `rm -rf .`
- `rm -rf *`
- `git push --force origin main`
- `git push -f origin master`
- `git reset --hard`
- `mkfs.ext4 /dev/sda1`
- `chmod -R 777 /var`
- `kubectl delete namespace prod`
- `docker system prune -a`

**Must allow:**

- `rm -rf /Users/me/projects/old-clone`
- `rm -rf ~/projects/old`
- `rm -rf ./build`
- `rm -rf /tmp/test`
- `rm -rf node_modules`
- `git push origin feature/foo`
- `git push --force origin feature/bar`

The fixed hook is in `hooks/destructive-guard.sh`.

## Lesson

If your safety hook has never blocked anything, that doesn't mean it's working — it might mean it's silently broken. Build adversarial test cases and run them every time you touch the hook.
