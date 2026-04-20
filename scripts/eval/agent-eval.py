#!/usr/bin/env python3
"""agent-eval.py — Synthetic-bug catch-rate eval harness for Claude Code agents.

REFERENCE ARTIFACT — adapt paths and fixtures before running.

Measures catch rate on planted-bug fixtures and false-positive rate on clean
fixtures, per specialist agent. Reads the agent's .md frontmatter + body and
invokes `claude -p --system-prompt <body>` — the body fully replaces Claude
Code's default system prompt, so the measurement shape matches a real Task
dispatch (agent prompt alone, nothing else). Billed under the Max subscription
(unsets ANTHROPIC_API_KEY in the subprocess env so OAuth is used instead of
Console API credits).

Dependencies:
  pip install pyyaml
  Claude Code CLI installed and logged in (OAuth / Max subscription)
  Python 3.13 recommended (anthropic's pydantic pin breaks on 3.14 at the time
  of writing — if you're only using the CLI you're probably fine on newer,
  but the test environment for this harness is 3.13).

Usage:
  agent-eval.py --agent security-auditor
  agent-eval.py --agent security-auditor --fixture security-001

Fixture layout expected:
  ~/.claude/eval-fixtures/<category>/*.yaml
  where <category> is the first token of the agent name (e.g. `security`
  for `security-auditor`). Each fixture has the shape shown in the sample
  files under `eval-fixtures/security/` of this repo.

Grader: keyword-matched against `planted_bugs[].expect_keywords`. Known
limitation — a miss may be a vocabulary gap, not a real miss. We recommend
tracking BOTH a strict (keyword) column and a manual-review column in your
ledger. See docs/eval-harness.md for the full story.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import yaml

HOME = Path.home()
AGENTS_DIR = HOME / ".claude" / "agents"
FIXTURES_DIR = HOME / ".claude" / "eval-fixtures"
REPORTS_DIR = HOME / ".claude" / "eval-reports"

MODEL_MAP = {
    "opus": "claude-opus-4-7",
    "sonnet": "claude-sonnet-4-6",
    "haiku": "claude-haiku-4-5-20251001",
    "inherit": "claude-sonnet-4-6",
}


def load_agent(name: str):
    """Return (body, model).

    Some agent .md frontmatter contains unescaped colons / raw \\n literals
    inside multi-line descriptions, which trips up a full yaml.safe_load.
    We only need the `model:` field, so extract it with a regex over the
    frontmatter region and treat everything after the closing `---` as body.
    """
    path = AGENTS_DIR / f"{name}.md"
    text = path.read_text()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not m:
        raise SystemExit(f"agent {name} missing frontmatter")
    frontmatter_text, body = m.group(1), m.group(2).strip()
    model_match = re.search(r"^model:\s*(\S+)\s*$", frontmatter_text, re.MULTILINE)
    model_key = model_match.group(1) if model_match else "sonnet"
    model = MODEL_MAP.get(model_key, model_key)
    return body, model


def load_fixtures(agent_name: str):
    category = agent_name.split("-")[0]
    fixture_dir = FIXTURES_DIR / category
    if not fixture_dir.exists():
        raise SystemExit(f"no fixture dir at {fixture_dir}")
    fixtures = []
    for path in sorted(fixture_dir.glob("*.yaml")):
        fixtures.append(yaml.safe_load(path.read_text()))
    if not fixtures:
        raise SystemExit(f"no fixtures in {fixture_dir}")
    return fixtures


def build_user_prompt(fixture: dict) -> str:
    return (
        f"Review the following code for security issues. This is a single code snippet "
        f"to audit — not a full project — so focus on what's visible.\n\n"
        f"```\n{fixture['code']}\n```\n\n"
        f"Context: {fixture.get('description', 'code review')}\n\n"
        f"Provide findings using your standard output format (CRITICAL / HIGH / MEDIUM / "
        f"Verified Safe). If no issues, say so plainly."
    )


def run_agent(
    system_prompt: str, user_prompt: str, model: str, budget_usd: float = 0.50
) -> str:
    """Invoke `claude -p` with the agent body as the full system prompt.

    Important:
      - `--system-prompt` REPLACES the default (verified via banana test)
      - ANTHROPIC_API_KEY is unset in the subprocess env so the CLI routes
        through the Max subscription (OAuth) instead of Console API credits
      - We intentionally do NOT use `--bare`, because `--bare` strips OAuth
        /keychain auth (CLI docs: "Anthropic auth is strictly
        ANTHROPIC_API_KEY or apiKeyHelper") and we need Max OAuth to work
    """
    env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
    proc = subprocess.run(
        [
            "claude",
            "-p",
            "--system-prompt",
            system_prompt,
            "--model",
            model,
            "--output-format",
            "json",
            "--max-budget-usd",
            str(budget_usd),
            user_prompt,
        ],
        capture_output=True,
        text=True,
        env=env,
        timeout=300,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"claude -p exited {proc.returncode}: {proc.stderr[:300]}")
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"claude -p produced non-JSON output: {e} / first 300 chars: {proc.stdout[:300]}"
        )
    if payload.get("is_error"):
        raise RuntimeError(f"claude -p error result: {payload.get('result', '')[:300]}")
    return payload.get("result", "")


def _section_has_findings(response_text: str, section: str) -> bool:
    """True if the given severity section (CRITICAL/HIGH) contains real findings,
    not just a 'None' placeholder. Splits on the section header and inspects
    the content up to the next header."""
    pattern = re.compile(
        rf"#{{1,4}}\s*{section}\b[^\n]*\n+(.*?)(?=\n#{{1,4}}\s|\Z)",
        re.IGNORECASE | re.DOTALL,
    )
    m = pattern.search(response_text)
    if not m:
        return False
    content = m.group(1).strip().lower()
    empty_markers = (
        "none.",
        "none",
        "n/a",
        "no issues",
        "no findings",
        "not applicable",
    )
    if not content or content in empty_markers:
        return False
    if content.splitlines()[0].strip().rstrip(".") in empty_markers:
        return False
    return True


def grade(fixture: dict, response_text: str):
    """Return ('caught' | 'missed' | 'false_positive' | 'true_negative', detail)."""
    rlow = response_text.lower()
    is_clean = fixture.get("is_clean", False)

    has_finding = _section_has_findings(
        response_text, "critical"
    ) or _section_has_findings(response_text, "high")

    if is_clean:
        if has_finding:
            return "false_positive", "agent flagged issues in clean code"
        return "true_negative", "no issues reported on clean code"

    for bug in fixture.get("planted_bugs", []):
        keywords = [k.lower() for k in bug.get("expect_keywords", [])]
        if not keywords:
            continue
        hits = sum(1 for kw in keywords if kw in rlow)
        threshold = max(1, (len(keywords) + 1) // 2)
        if hits >= threshold:
            return (
                "caught",
                f"{bug.get('type', 'bug')}: {hits}/{len(keywords)} keywords",
            )
    return "missed", "no planted-bug keywords matched"


def write_report(agent: str, model: str, results: list, summary: dict) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    d = REPORTS_DIR / agent
    d.mkdir(parents=True, exist_ok=True)
    report_file = d / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    report_file.write_text(
        json.dumps(
            {
                "agent": agent,
                "model": model,
                "date": datetime.now().isoformat(),
                "summary": summary,
                "results": results,
            },
            indent=2,
        )
    )
    return report_file


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", required=True)
    parser.add_argument("--fixture", help="run a single fixture id")
    args = parser.parse_args()

    system_prompt, model = load_agent(args.agent)
    fixtures = load_fixtures(args.agent)
    if args.fixture:
        fixtures = [f for f in fixtures if f["id"] == args.fixture]
        if not fixtures:
            raise SystemExit(f"fixture {args.fixture!r} not found")

    print(
        f"Agent: {args.agent} | Model: {model} | Fixtures: {len(fixtures)}",
        file=sys.stderr,
    )
    results = []
    for fixture in fixtures:
        print(f"→ {fixture['id']}", file=sys.stderr, flush=True)
        user_prompt = build_user_prompt(fixture)
        try:
            response = run_agent(system_prompt, user_prompt, model)
        except (subprocess.TimeoutExpired, RuntimeError) as e:
            print(f"  error: {e}", file=sys.stderr)
            results.append(
                {
                    "fixture": fixture["id"],
                    "verdict": "error",
                    "detail": str(e)[:200],
                    "response": "",
                }
            )
            continue
        verdict, detail = grade(fixture, response)
        print(f"  {verdict}: {detail}", file=sys.stderr)
        results.append(
            {
                "fixture": fixture["id"],
                "verdict": verdict,
                "detail": detail,
                "response": response,
            }
        )

    tp = sum(1 for r in results if r["verdict"] == "caught")
    fn = sum(1 for r in results if r["verdict"] == "missed")
    fp = sum(1 for r in results if r["verdict"] == "false_positive")
    tn = sum(1 for r in results if r["verdict"] == "true_negative")
    planted = tp + fn
    clean = fp + tn
    catch_rate = tp / planted if planted else 0.0
    fp_rate = fp / clean if clean else 0.0

    summary = {
        "catch_rate": catch_rate,
        "fp_rate": fp_rate,
        "tp": tp,
        "fn": fn,
        "fp": fp,
        "tn": tn,
        "planted_total": planted,
        "clean_total": clean,
    }

    report_file = write_report(args.agent, model, results, summary)

    print()
    print(f"Agent:      {args.agent} ({model})")
    print(
        f"Catch rate: {tp}/{planted} ({catch_rate:.0%})"
        if planted
        else "Catch rate: n/a (no planted fixtures)"
    )
    print(
        f"FP rate:    {fp}/{clean} ({fp_rate:.0%})"
        if clean
        else "FP rate:    n/a (no clean fixtures)"
    )
    print(f"Report:     {report_file}")


if __name__ == "__main__":
    main()
