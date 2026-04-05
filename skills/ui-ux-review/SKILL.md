---
name: ui-ux-review
description: Audit a page or component for UI/UX quality — hierarchy, spacing, responsive design, accessibility, and design tokens. Use when reviewing UI or auditing page design.
allowed-tools: Read, Glob, Grep, Agent
argument-hint: [page-name-or-file-path]
---

# UI/UX Review

Audit a page or component for design quality against the project's design system and modern UI/UX best practices.

## Process

### Step 1: Identify the Target

If an argument was provided, find that file. Otherwise, ask which page or component to review.

### Step 2: Read the Component

Read the target file and any child components it imports. Understand the full render tree.

### Step 3: Detect the Design System

Before auditing, understand what design system this project uses. Check in this order:

1. Read the project's `CLAUDE.md` for design system references
2. Check for `tailwind.config.*` — look at theme extensions, custom colors, design tokens
3. Check for CSS variable definitions (`:root` or theme files)
4. Look at existing components to see what patterns are actually in use

This determines which tokens, color classes, and patterns are "correct" for this project. Don't assume any specific token names — derive them from the project.

### Step 4: Audit Checklist

Run through each category and flag issues. Adapt specific class names and tokens to whatever the project actually uses (discovered in Step 3).

**Visual Hierarchy**

- [ ] Most important content is visually prominent (size, weight, color)
- [ ] Clear section separation with consistent spacing
- [ ] Heading levels are logical (not skipping h2 → h4)
- [ ] KPIs/numbers use monospace or bold for emphasis
- [ ] Secondary info is visually de-emphasized (muted/secondary text classes)

**Design Token Compliance**

- [ ] No raw Tailwind colors where project defines custom tokens — use project tokens
- [ ] No hardcoded hex values in className strings
- [ ] Surfaces follow the project's elevation/layering hierarchy
- [ ] Brand colors used per the project's design system
- [ ] Semantic colors for status states (success, warning, error)

**Spacing & Layout**

- [ ] Consistent spacing scale (not mixing arbitrary values)
- [ ] Consistent section spacing between major sections
- [ ] Consistent card/container padding
- [ ] Grid patterns match content type
- [ ] Content max-width applied where appropriate

**Responsive Design**

- [ ] Mobile-first: base classes for mobile, breakpoints for larger
- [ ] Text scales responsively
- [ ] Padding scales responsively
- [ ] Grids collapse on mobile
- [ ] Touch targets >= 44x44px on mobile
- [ ] No horizontal overflow on small screens

**Accessibility**

- [ ] Interactive elements have `aria-label` when icon-only
- [ ] Focus rings visible on interactive elements
- [ ] Color is not the only indicator of state (add icons or text)
- [ ] Form inputs have associated labels
- [ ] Proper `role` attributes on custom interactive elements
- [ ] Motion respects `prefers-reduced-motion`

**Animations & Transitions**

- [ ] Hover states on interactive elements
- [ ] Transitions are smooth (appropriate durations)
- [ ] Loading uses skeleton screens or appropriate loading patterns
- [ ] Entrance animations use project's existing keyframes if available
- [ ] No jarring layout shifts on data load

**Empty & Error States**

- [ ] Empty state has icon + descriptive text, centered
- [ ] Error state shows meaningful message with retry option
- [ ] Loading state matches the content shape (skeleton)

### Step 5: Dispatch Specialist Agent (if needed)

If issues are found that require code changes, dispatch the `ui-ux-designer` agent for design recommendations or `frontend-specialist` for implementation.

### Step 6: Report

Output format:

```
## UI/UX Review: [Component Name]

### Score: [A/B/C/D]
(A = production-ready, B = minor issues, C = needs work, D = significant redesign needed)

### Issues Found
1. **[Category]** — [specific issue with file:line reference]
   - Current: `[what it looks like now]`
   - Recommended: `[what it should be]`

### What's Working Well
- [positive observations]

### Recommended Actions
- [ ] [prioritized fix list]
```
