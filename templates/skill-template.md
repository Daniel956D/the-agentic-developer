---
name: your-skill-name
description: What this skill does in under 250 chars. Front-load trigger keywords.
allowed-tools: Read, Write, Bash, Glob, Grep
argument-hint: [optional-argument]
---

<!--
  SKILL DESIGN RULES:
  - Keep under 500 lines (official recommendation)
  - Description under 250 chars (Claude truncates beyond this)
  - Use disable-model-invocation: true for skills with side effects
  - Use allowed-tools to restrict what Claude can do
  - $ARGUMENTS contains whatever the user passes after /skill-name
-->

# Skill Name

Brief description of what this skill does and when to use it.

## Process

### Step 1: Gather Context

[What information to collect before acting]

### Step 2: Execute

[What to actually do]

### Step 3: Report

[What to show the user]

## Rules

- [Guard rails and constraints]
- [Error handling behavior]
- [What to skip silently vs what to report]
