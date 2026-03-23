# Project Board

The [GitHub Project](https://github.com/users/colin-gourlay/projects/3) tracks all roadmap work for this repository. This page documents the configured views, custom fields, and working conventions.

---

## Views

Three saved views are set up on the board. Each serves a distinct purpose.

### Board by Status

A Kanban-style board grouped by the **Status** field.

| Column | Meaning |
|--------|---------|
| **No Status** | Items not yet triaged |
| **Backlog** | Identified but not actively planned |
| **Ready** | Scoped and ready to pick up |
| **In Progress** | Actively being worked on |
| **Done** | Completed |

Use this view for day-to-day triage and to see what is in flight at a glance.

### Table by Area

A spreadsheet-style table layout with the **Area** column visible. Items are grouped or filtered by Area to give a cross-cutting view of the roadmap by theme.

Use this view to review all work in a given area (e.g. Templates, Automation, Docs) and to spot imbalances or gaps.

### Public Visibility Focus

A filtered view showing only items where **Impact = Public Visibility**. This makes it easy to see what work is visible or meaningful to external contributors and users.

Use this view when deciding what to prioritise for open-source health or community growth.

---

## Custom Fields

| Field | Type | Meaning |
|-------|------|---------|
| **Status** | Single select | Where the item is in the workflow: Backlog → Ready → In Progress → Done |
| **Area** | Single select | The functional area the work belongs to: Templates, Automation, Docs, CI, Community, Meta |
| **Impact** | Single select | Who or what the work primarily benefits: Internal Workflow, Public Visibility, Developer Experience, Quality |
| **Target Month** | Date / Iteration | The calendar month by which the item is intended to be resolved — used for loose scheduling, not hard deadlines |

These fields are for orientation and prioritisation, not project-management overhead. Not every item needs every field populated.

---

## Draft Items vs Issues

Use **draft items** (cards created directly in the project) for:

- Initial ideas that have not yet been scoped or committed to
- Placeholder reminders that may never become real work
- Discussion topics or proposals that are still being evaluated

Convert a draft item to an **issue** when:

- The work is agreed and will definitely be done
- The item needs discussion, comments, or linked PRs
- You want it to appear in the repository issue tracker for visibility

The conversion rule of thumb: **if you would reference it in a PR or link to it from a commit, make it an issue.**

---

## Converting Discussion Outcomes into Tracked Work

When a discussion (in an issue, PR comment, or elsewhere) results in an agreed next step:

1. Create a draft item in the project with a short title capturing the outcome
2. Add the appropriate **Area** and **Impact** fields immediately
3. Assign a **Target Month** if there is any urgency or expectation
4. Promote the draft to an issue once it is scoped and ready to be worked on

This keeps speculative ideas out of the issue tracker while ensuring nothing agreed is lost.

---

## Classification Reference

Issue [#71](https://github.com/colin-gourlay/todoist-playbook/issues/71) and all seeded draft items are classified as follows:

- **Area**: the functional theme of the work (e.g. Templates, Automation, Docs)
- **Impact**: the primary audience or benefit (e.g. Internal Workflow, Public Visibility)
- **Status**: reflects actual progress, not aspirational placement

When in doubt, default to **Backlog** status and set Area; fill in Impact and Target Month only when the item is being actively considered.
