---
description: "Run a weekly review session: reflect on the past week and plan the next."
argument-hint: "Time period and any focus areas"
agent: "ask"
---

Run a weekly review with the user. This is a facilitation prompt — ask short, focused questions and synthesize the answers into a structured review. The companion repo template is [csv-templates/weekly-review/template.csv](../../csv-templates/weekly-review/template.csv); use its sections as the spine.

## Inputs

- **Time period** (optional) — defaults to the past 7 days
- **Focus areas** (optional) — e.g. work, side project, health

## Sections to cover

1. **Review Last Week** — what got done, what slipped, what surprised you
2. **Assess Current State** — energy, blockers, open loops
3. **Plan Next Week** — top 3 priorities, deep-work blocks, commitments to decline
4. **Stop / Start / Continue** — see [stop-start-continue.prompt.md](./stop-start-continue.prompt.md)

## Output

A single Markdown document with one heading per section above, concise bullets under each, and an explicit "Top 3 priorities" line near the end.

## Style

- Ask one question at a time when interviewing
- Avoid filler and motivational fluff
- Keep planned items actionable (verb + object) so they could become Todoist tasks
