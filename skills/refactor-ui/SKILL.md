---
name: refactor-ui
description: Restructure existing UI templates and pages. Use when improving layouts, converting patterns (cards to tables), or cleaning up existing pages.
allowed-tools: Read, Edit, Write, Bash, Glob, Grep
argument-hint: [page-name-or-file-path]
---

# Refactor Existing UI

Restructure existing templates while preserving all functionality. This is NOT for building new interfaces from scratch — it's for making existing pages better.

## Why This Exists

Modifying existing UI is different from building new UI. The biggest risk isn't bad design — it's breaking existing functionality. A missing event handler, a lost API call, or a removed data attribute can silently break features. This skill prevents that.

## Before Touching Code

### 1. Read Everything First

Read the full template file AND its associated JS. Understand:

- Every API endpoint the page calls (fetch URLs, form actions)
- All event handlers (onclick, onchange, onsubmit, custom listeners)
- Dynamic content rendering (how data flows from API → DOM)
- State management (what's stored in variables, localStorage, Sets, Maps)
- Polling/intervals (setInterval, setTimeout, visibility listeners)
- Modal triggers and their relationships to list items

### 2. Inventory What Must Be Preserved

Before proposing changes, explicitly list:

- **API calls**: every fetch/XHR with method and URL
- **User interactions**: every clickable/interactive element and what it does
- **State**: variables that track UI state (expanded rows, active tabs, filters)
- **Side effects**: polling, localStorage reads/writes, event listeners on document/window

### 2.5. When to Consult `ui-ux-designer`

This skill handles **structural** refactors safely (preserving handlers, API calls, state). For **visual design decisions** that come up mid-refactor — spacing scale, hierarchy choices, color tokens, typography, responsive breakpoints, animation timing — dispatch the `ui-ux-designer` agent before committing the change. Skip the dispatch for purely mechanical refactors (e.g., cards → table with no visual rethink).

### 3. Check Project Patterns

Read CLAUDE.md for project-specific patterns. Common ones to enforce:

- XSS: `escapeHtml()` for user data in innerHTML, `tojson` filter in Jinja2
- Accessibility: `aria-label` on icon buttons, `aria-hidden` on decorative icons, `for` on labels
- Fetch: always check `response.ok`
- Polling: track interval IDs, clear on navigation, pause when tab hidden
- Redirects: validate origin before `window.location.href`

## Making Changes

### 4. Work Incrementally

Each change should be independently committable and revertable:

1. Header/layout cleanup (spacing, classes, remove unused elements)
2. Structural changes (cards → table, vertical → tabs)
3. JS updates to match new structure
4. Remove dead code (unused functions, CSS classes, localStorage keys)

### 5. Common Refactor Patterns

**Cards to Table:**

- Map card fields to columns
- Row click = card expand (use `event.stopPropagation()` on action buttons)
- Detail panel = `<tr>` with `colspan` spanning all columns
- Preserve the expand/collapse state tracking

**Vertical Sections to Tabs:**

- All tab content renders on page load (no lazy loading unless existing)
- Tab switching = show/hide, not re-fetch
- Chart.js canvases hidden in inactive tabs need `.resize()` on tab show
- Default to first tab, no persistence needed unless existing

**Header Cleanup:**

- Remove help panels/quick tips if requested
- Remove density toggles and associated JS/localStorage
- Keep navigation controls (prev/next, filters, search)
- Use consistent border radius (`rounded-2xl` or project standard)

### 6. JS Cleanup Checklist

After structural changes, verify the basics:

- [ ] All `getElementById`/`querySelector` calls still target valid IDs/selectors
- [ ] Event delegation still works (if parent elements changed)
- [ ] Removed functions/variables that were only used by removed UI elements

Then apply stack-specific rules based on what the project uses:

**Jinja2/Flask templates:** `var` not `let`/`const` (avoids redeclaration errors in Jinja2 blocks). No optional chaining (`?.`) — use `&&` chains for broader browser compatibility.

**React/TypeScript:** Use `const`/`let` per normal. Optional chaining is fine. Check that component props haven't changed shape after refactoring child components.

**Django templates:** Similar to Jinja2 for inline `<script>` blocks. For separate `.js`/`.ts` files, use modern syntax freely.

Read the project's CLAUDE.md and existing code to determine which rules apply.

## After Changes

### 7. Verify

- Every API call from step 2 still happens
- Every user interaction from step 2 still works
- No console errors on page load
- No console errors when interacting with every feature
- Responsive layout doesn't break at common widths

### 8. Commit Pattern

One commit per logical change, conventional commit format:

```
feat(page-name): convert card layout to table
feat(page-name): add tabbed sections for analysis content
fix(page-name): clean up header and remove unused help panel
refactor(page-name): remove dead density toggle code
```
