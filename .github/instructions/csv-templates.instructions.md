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

Use `csv-templates/github/github-trending-repo-review/template.csv` as the structural exemplar when editing other extended-format CSV templates. Match its canonical structure (column order and leading `meta,view_style=list` row) unless a repo-specific requirement explicitly calls for a different format.

The first line MUST start with `TYPE,` and use one of the two supported headers below. The **extended** header is the canonical format for new templates; the **legacy** header is still accepted for back-compat.

**Extended (recommended for new templates):**

```
TYPE,CONTENT,DESCRIPTION,IS_COLLAPSED,PRIORITY,INDENT,AUTHOR,RESPONSIBLE,DATE,DATE_LANG,TIMEZONE,DURATION,DURATION_UNIT,DEADLINE,DEADLINE_LANG
```

**Legacy (still accepted):**

```
TYPE,CONTENT,PRIORITY,INDENT,AUTHOR,RESPONSIBLE,DUE_DATE,DUE_DATE_LANG
```

Common rules (both formats):

- `TYPE` MUST be `section`, `task`, or `meta`
- `PRIORITY` is `1`–`4`. The importer maps CSV `1` → API `4` (highest) and CSV `4` → API `1` (lowest)
- `INDENT` is an integer nesting level (top-level rows = `1`)
- Rows with empty `CONTENT` are skipped by the importer
- `README.md` MUST include import instructions or explicitly mention CSV import

Extended-format columns:

| Column | Notes |
|---|---|
| `DESCRIPTION` | Optional long-form description (multi-line allowed when CSV-quoted) |
| `IS_COLLAPSED` | Optional. Empty or `1` to collapse the row in the Todoist UI |
| `DATE` | Natural-language due string (e.g. `today at 05:30`, `every monday`). Absolute calendar dates (e.g. `2024-12-25`) MUST NOT be used — they go stale on import |
| `DATE_LANG` | Language code for the due string (e.g. `en`) |
| `TIMEZONE` | IANA zone (e.g. `Europe/London`) when a specific zone matters |
| `DURATION` / `DURATION_UNIT` | Integer + `minute` or `day` |
| `DEADLINE` / `DEADLINE_LANG` | Optional immovable deadline string + language |

`meta` rows use `CONTENT` for `key=value` settings (e.g. `meta,view_style=list,...`).

Legacy-format date columns (`DUE_DATE`, `DUE_DATE_LANG`) MUST be empty in legacy templates — the project-creation scripts alias `DUE_DATE` ↔ `DATE` for back-compat.

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
- Hardcoded calendar dates in `DATE` / `DEADLINE` (use natural-language relative dates instead)

## Content style

- Do not use the em dash character (`—`) in `description:` fields or any content that appears in the GitHub Pages gallery. Use a hyphen (`-`) instead.
