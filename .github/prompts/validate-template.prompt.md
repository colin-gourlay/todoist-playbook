---
description: "Quick conformance check of a CSV template, prompt template, or bundle against repo conventions."
argument-hint: "Path to the asset folder or file"
agent: "agent"
---

Review the asset at the path the user provides and report any deviations from the repo conventions.

For the full local validation pipeline (the same checks CI runs), prefer the `validate-templates-locally` skill. Use this prompt for a fast structured review.

## What to check

### Folder + metadata (all asset types)

- Folder name is kebab-case
- Folder name equals the `slug:` in the asset's metadata file
- `version:` is `0.0.0` (unreviewed) or `0.1.x` (reviewed) — never hand-bumped
- `category:` reuses an existing kebab-case value when one fits
- The asset is listed in [index.md](../../index.md)

### CSV templates — see [csv-templates.instructions.md](../instructions/csv-templates.instructions.md)

- Folder contains exactly `template.csv`, `meta.yml`, `README.md`
- First CSV line starts with `TYPE,` and matches one of:
  - **Extended (canonical):** `TYPE,CONTENT,DESCRIPTION,IS_COLLAPSED,PRIORITY,INDENT,AUTHOR,RESPONSIBLE,DATE,DATE_LANG,TIMEZONE,DURATION,DURATION_UNIT,DEADLINE,DEADLINE_LANG`
  - **Legacy (still accepted):** `TYPE,CONTENT,PRIORITY,INDENT,AUTHOR,RESPONSIBLE,DUE_DATE,DUE_DATE_LANG`
- `TYPE` ∈ {`section`, `task`, `meta`}
- `PRIORITY` ∈ `1`–`4`
- `INDENT` is a non-negative integer
- `DATE` / `DUE_DATE` / `DEADLINE` contain only natural-language relative strings (e.g. `today at 05:30`, `every monday`); never absolute calendar dates like `2024-12-25`
- `DURATION` (integer) and `DURATION_UNIT` (`minute` or `day`) are set together when used
- Tasks start with action verbs; no vague entries
- `project_color` (if set) matches a value in [.github/scripts/project_colors.txt](../scripts/project_colors.txt)
- `README.md` includes import instructions

### Prompt templates — see [prompt-templates.instructions.md](../instructions/prompt-templates.instructions.md)

- Every `{{placeholder}}` in `prompt.md` matches an entry in `inputs:` in `meta.yml`
- The prompt declares its expected output shape

### Bundles — see [bundles.instructions.md](../instructions/bundles.instructions.md)

- `bundle.yml` only references slugs that exist under `csv-templates/` or `prompt-templates/`
- No duplicated task content (bundles are references, not content)

## Output format

```
## <asset-slug>

**Status:** PASS | FAIL

### Issues
- <issue 1>
- <issue 2>

### Suggestions
- <suggestion 1>
```
