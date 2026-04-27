---
description: "Draft a new CSV-based Todoist template (template.csv + meta.yml + README.md) under csv-templates/."
argument-hint: "Template name and purpose"
agent: "agent"
---

Draft a new CSV-based Todoist template that conforms to the repo's conventions in [csv-templates.instructions.md](../instructions/csv-templates.instructions.md).

If the user wants the full guided scaffold (folder, all three files, index.md and workflow updates), prefer the `add-todoist-asset` skill. Use this prompt for a focused single-shot draft of `template.csv` content.

## Inputs

- **Template name** (required) — human-readable, e.g. "Weekly Review"
- **Slug** (optional) — kebab-case; defaults to slugified name
- **Purpose** (required) — one-line description
- **Sections** (optional) — suggested section headings

## Output

Produce `template.csv` content with this EXACT header on the first line:

```
TYPE,CONTENT,PRIORITY,INDENT,AUTHOR,RESPONSIBLE,DUE_DATE,DUE_DATE_LANG
```

Rules:

- `TYPE` is `section`, `task`, or `meta`
- `PRIORITY` is `1`–`4` (CSV `1` is highest in importer mapping)
- `INDENT` is an integer nesting level (sections at `1`, top-level tasks at `1`, sub-tasks at `2`+)
- `DUE_DATE` and `DUE_DATE_LANG` MUST be empty — never hardcode dates
- Tasks MUST start with an action verb (Review, Plan, Identify, Draft, Send, Schedule…)
- Group tasks under clear section rows
- Avoid vague tasks like "Do stuff"

Also draft a minimal `meta.yml`:

```yaml
name: <Human Readable Name>
slug: <kebab-slug>            # MUST equal the folder name
description: <one-line>
category: <kebab-case>        # reuse an existing category when one fits
tags:
  - <tag>
version: 0.0.0                # always start unreviewed
```

## Example

Input: `Weekly Review` — reflect on the past week and plan the next.

```csv
TYPE,CONTENT,PRIORITY,INDENT,AUTHOR,RESPONSIBLE,DUE_DATE,DUE_DATE_LANG
section,Reflect,4,1,,,,
task,Review last week's completed tasks,2,1,,,,
task,Identify blockers and unfinished work,2,1,,,,
section,Plan,4,1,,,,
task,Define top 3 priorities for next week,1,1,,,,
task,Schedule deep-work blocks,2,1,,,,
section,Improve,4,1,,,,
task,Capture one Stop / Start / Continue insight,3,1,,,,
```
