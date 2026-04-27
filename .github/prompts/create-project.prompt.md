---
description: "Adapt an existing CSV template into a dated, context-specific Todoist project plan."
argument-hint: "Template slug + project name + timeframe"
agent: "agent"
---

Take an existing CSV template under `csv-templates/` and produce a one-off, dated project plan suitable for pasting into Todoist or feeding to the `create-todoist-project.yml` workflow. This does NOT modify the source template — it adapts it for a specific run.

## Inputs

- **Template slug** (required) — e.g. `weekly-review`
- **Project name** (required) — e.g. "Weekly Review – Week 12"
- **Timeframe** (optional) — start date, end date, or relative window ("next week")
- **Context tweaks** (optional) — extra tasks or skipped sections specific to this run

## Steps

1. Read the source `csv-templates/<slug>/template.csv`
2. Preserve sections and structure
3. Resolve due dates relative to the timeframe (use Todoist natural-language dates like `every monday`, `next sunday`, `2026-05-04`)
4. Apply context tweaks (add/skip tasks) without renaming the underlying template

## Output

A structured plan grouped by section, e.g.:

```
Reflect
- Review last week's completed tasks (Due: Sunday)
- Identify blockers and unfinished work

Plan
- Define top 3 priorities for next week (Due: Sunday)
- Schedule deep-work blocks (Due: Monday)
```

## Constraints

- Do not edit files under `csv-templates/`
- Do not invent tasks that aren't in the source template unless explicitly asked
- Keep priorities and indentation consistent with the source
