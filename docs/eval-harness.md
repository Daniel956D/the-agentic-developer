# Evaluation Harness

Most Claude Code agent repos ship with zero evidence that the agents actually work. You add a `code-reviewer` agent because the README says you should, and you assume it's doing something. This repo ships with two eval instruments that measure whether each agent is actually catching what it's supposed to catch.

## Two instruments, two questions

| Instrument                | Layer      | Question                                                           | Status                                                 |
| ------------------------- | ---------- | ------------------------------------------------------------------ | ------------------------------------------------------ |
| **Skill-dispatch eval**   | Routing    | When I ask something, does Claude Code pick the right skill/agent? | ~87% strict accuracy on a 2-skill starter scenario set |
| **Agent catch-rate eval** | Capability | When the agent _does_ run, does it catch the bug it's supposed to? | Baselines below                                        |

Routing accuracy × catch rate = end-to-end system quality. You need both.

## Baselines (reference, adapt for your own setup)

From an initial run against planted-bug fixtures:

| Agent                 | Catch rate (strict) | FP rate (strict) | Catch rate (manual) | FP rate (manual) |
| --------------------- | ------------------- | ---------------- | ------------------- | ---------------- |
| security-auditor      | 8/8 (100%)          | 0/2 (0%)         | 8/8 (100%)          | 0/2 (0%)         |
| silent-failure-hunter | 3/3 (100%)          | 2/2 (100%)       | 3/3 (100%)          | 0/2 (0%)         |
| code-reviewer         | 1/3 (33%)           | 0/2 (0%)         | 3/3 (100%)          | 0/2 (0%)         |

**Read the divergences — they're the whole story.**

- **silent-failure-hunter strict FP 100% → manual FP 0%**: The agent caught real bugs in fixtures I'd mistakenly labeled "clean." The strict grader flagged these as false positives because the fixture said `is_clean: true`. Manual review said the agent was right and the fixture was wrong. Treat unexpected "false positives" as _fixture-design feedback first_, agent-over-zealousness second.

- **code-reviewer strict 33% → manual 100%**: The agent identified every planted issue but used different vocabulary than my `expect_keywords`. This is the **grader vocabulary gap** — the single biggest limitation of a keyword-matched grader.

**Non-goals locked in:** don't tune the grader post-hoc to make numbers look better, and don't "fix" clean fixtures that turned out to have real bugs. Treat the divergence as a signal about your measurement tool, not a problem to paper over.

## Harness architecture

```
~/.claude/
├── scripts/eval/agent-eval.py       # the harness
├── eval-fixtures/<category>/*.yaml  # planted + clean fixtures per agent
├── eval-reports/<agent>/*.json      # one report per run
└── evals-ledger.md                  # running tally + notes (strict + manual cols)
```

The harness loads an agent's `.md` frontmatter + body and invokes:

```bash
claude -p --system-prompt "<agent-body>" --model <model> \
         --output-format json --max-budget-usd 0.50 "<user-prompt>"
```

Three details that matter:

1. **`--system-prompt` REPLACES the Claude Code default** (verified with a "banana" sentinel — the model receives the agent body alone). This is what makes the measurement shape match a real `Task` dispatch, not an inflated "agent + all the default system prompt" setup.

2. **`ANTHROPIC_API_KEY` unset in subprocess env** forces the CLI through its OAuth/Max-subscription path. If you leave the env var set, the CLI routes through Console API credits and bills differently. Unset it and you're on your subscription.

3. **We do NOT use `--bare`.** `--bare` strips OAuth/keychain auth (CLI docs: "Anthropic auth is strictly ANTHROPIC_API_KEY or apiKeyHelper"), so `--bare` + no API key = 401. `--system-prompt` alone is enough to replace the default.

## Grading

```python
# Planted fixture
hits = sum(1 for kw in expect_keywords if kw in response.lower())
threshold = max(1, ceil(len(expect_keywords) / 2))
verdict = "caught" if hits >= threshold else "missed"

# Clean fixture
has_critical_or_high = find_severity_section(response, "CRITICAL") or \
                       find_severity_section(response, "HIGH")
verdict = "false_positive" if has_critical_or_high else "true_negative"
```

The "half-match" threshold is lenient on purpose. Agents paraphrase; a 3/5 keyword hit on a clearly-identified issue shouldn't be a miss.

## Known limitations

Be honest about what this harness doesn't do yet:

1. **Small N per agent.** 5-10 fixtures baseline means one wrong call is a 10-33% swing. Growing to 20+ is in-scope.
2. **Keyword grader has a vocabulary gap.** See the code-reviewer 33%/100% divergence above. The principled v2 fix is an LLM-as-judge grader (Haiku rates each response against the fixture's intent). Out of scope for v1; tracked for a later pass.
3. **"Clean" fixtures are harder to author than "planted" ones.** See silent-failure-hunter above. Budget time to iterate on these.
4. **Textbook-case bias.** Initial security fixtures all came from Known Risks registries (SQLi, XSS, hardcoded secrets). A second-round set should include harder cases (second-order SQLi, IDOR without decorator, mass assignment, timing attacks).
5. **No rate-limit pacing needed.** CLI-backed harness drains the Max subscription, which has different ceilings than the Console API's 30k/min. Running 20 fixtures end-to-end works without throttling.

## Wired into the weekly audit

`commands/agent-improvement.md` runs as a loop command every Friday. Phase 4.5 of that command runs both evals against every agent that has a fixture directory. Agents without fixtures are skipped (not failed). Trend data compounds month-over-month.

## Why this is worth the effort

Claude Code agents are infrastructure — you're going to dispatch them hundreds of times a month. If one silently drops in quality (a model update, a prompt change, a new pattern it hasn't seen) you want to know before the next production bug, not after. A 30-minute monthly run is cheap insurance.

The baseline numbers above are also the honest-marketing version: the strict/manual divergence is the most interesting part of the result, not the rounded "100% catch" headline. Most eval repos hide the uncertainty. This one leads with it.
