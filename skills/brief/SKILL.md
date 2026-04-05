---
name: brief
description: Summarize technical work into a clear executive brief for non-technical stakeholders
disable-model-invocation: true
argument-hint: [topic-or-project]
---

Create an executive brief of $ARGUMENTS:

1. **Summary**: One sentence — what happened or what this is about
2. **Impact**: Why it matters to the business or stakeholders
3. **Status**: Where things stand right now (done, in progress, blocked)
4. **Next steps**: What's needed, from whom, and by when

## Audience Presets

Adapt tone and detail based on who will read this:

**For leadership:**

- Focus on timeline, cost, and risk
- Skip all technical details — translate to business outcomes
- Lead with decisions they need to make
- Keep under 150 words

**For vendors/external:**

- Focus on requirements, specs, and deliverables
- Include relevant technical constraints they need to know
- Be professional but direct
- Keep under 200 words

**For team/internal:**

- Can include light technical detail
- Focus on what changed and what they need to do differently
- Reference specific systems or tools by name
- Keep under 200 words

If the audience isn't specified, default to **leadership**.

## Rules

- No jargon — translate every technical term
- If a technical detail is essential, explain it in parentheses
- Use bullet points, not paragraphs
- Lead with what matters most to the reader
