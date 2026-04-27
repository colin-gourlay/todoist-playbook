---
applyTo: "csv-templates/**"
description: Conventions and procedures for CSV-based Todoist templates.
---

# CSV Template Conventions

## Folder layout

Every CSV template lives at `csv-templates/{slug}/` (or `csv-templates/{group}/{slug}/` when grouped). Folder name MUST be kebab-case (lowercase letters, digits, hyphens only) and MUST contain exactly:

- `template.csv`
- `meta.yml`
- `README.md`

## Required `meta.yml` keys

```yaml
name: Human Readable Name
slug: folder-slug          # MUST equal the folder name
description: One-line description
category: kebab-case-category
tags:
  - tag-one
version: 0.0.0             # 0.0.0 = unreviewed, 0.1.0 = reviewed
```

## Common optional `meta.yml` keys

```yaml
estimated_duration: 15m
recurrence_suggestion: weekly
author: Name
project_color: blue        # MUST be a value in .github/scripts/project_colors.txt
```

## `category:` values

Categories are free-form kebab-case strings. Re-use an existing value when one fits. Currently in use: `agile`, `brand-and-social`, `career`, `creative`, `engineering`, `github`, `personal-systems`, `professional-development`, `radio-show-systems`, `saas-management`. Source of truth is the union of `category:` values across `csv-templates/**/meta.yml` and `prompt-templates/**/meta.yml`.

## `template.csv` rules

- First line MUST be exactly: `TYPE,CONTENT,PRIORITY,INDENT,AUTHOR,RESPONSIBLE,DUE_DATE,DUE_DATE_LANG`
- `TYPE` MUST be `section`, `task`, or `meta`
- `PRIORITY` is `1`–`4`. The importer maps CSV `1` → API `4` and CSV `4` → API `1`
- `INDENT` is an integer nesting level
- `DUE_DATE` MUST be empty (no hardcoded dates)
- Rows with empty `CONTENT` are skipped by the importer
- `README.md` MUST include import instructions or explicitly mention CSV import

## Adding a new CSV template

1. Create `csv-templates/{slug}/` (kebab-case)
2. Add `meta.yml`, `template.csv`, `README.md`
3. Set `version: 0.0.0`
4. Update `index.md` to list the new template
5. Add the slug to `create-todoist-project.yml` `inputs.template` options
6. Add the slug to `create-todoist-project-via-mcp.yml` if it should be available via MCP
7. Update `README.md` only if user-facing discovery copy needs changing

## Common validation failures

- `meta.yml` slug mismatch — check for quotes, leading/trailing spaces, or folder rename
- Missing import guidance in `README.md`
- Invalid `project_color` (must match `.github/scripts/project_colors.txt`)
- Hardcoded due dates in `DUE_DATE`
