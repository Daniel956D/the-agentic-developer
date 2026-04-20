# Eval Fixtures

Sample fixtures for `scripts/eval/agent-eval.py`. Two per category — one planted-bug and one clean — is enough to start; your real set should be 10+ per agent for stable numbers.

## Shape

```yaml
id: security-001 # unique id, used with --fixture flag
category: injection # free-form
description: one-line # also shown to the agent as context
is_clean: false # true = no bugs, test false-positive rate
planted_bugs: # empty [] when is_clean: true
  - type: sql-injection # free-form label
    expect_keywords: # case-insensitive; half-match threshold
      - "sql injection"
      - "parameteriz"
code: | # literal block — indented Python/JS/etc.
  ...
```

## How it grades

- **Planted**: CAUGHT if the agent's response hits ≥ `ceil(len(keywords)/2)` of the `expect_keywords`. Otherwise MISSED.
- **Clean**: TRUE NEGATIVE if the agent reports no CRITICAL or HIGH findings. FALSE POSITIVE otherwise.

The "keyword match ≥ half" threshold is intentionally lenient — a stricter grader punishes agents for phrasing differences that a human reader would accept.

## Known grader limitations

- **Vocabulary gap.** An agent may describe the exact same issue with different wording than your keywords. Always run a human pass too and record BOTH a strict (keyword) and manual column in your ledger.
- **Small N is noisy.** With 5 fixtures per agent, one wrong call is a 20% swing. 10+ is the recommended floor.
- **"Clean" is the hard category.** Authoring genuinely bug-free code for a security-focused agent to inspect is harder than authoring bugs. If your agent repeatedly flags a "clean" fixture, treat that as fixture-design feedback before agent-over-zealousness.

See `docs/eval-harness.md` for the full story — including why `claude -p --system-prompt` is what makes this measurement shape correct.
