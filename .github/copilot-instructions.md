# Copilot Instructions

## Repository Overview

**todoist-playbook** is a curated collection of structured [Todoist](https://www.todoist.com/) templates and automation tooling. The repository contains:

- Reusable project templates (CSV + metadata + docs)
- A GitHub Actions workflow for creating Todoist projects via the API
- A validation workflow that enforces template structure on every push to `main`

There is no build system, package manager, or test framework — the only "tests" are the CI validation checks in `.github/workflows/validate-templates.yml`.

---

## Repository Structure

```
templates/          # Individual reusable templates, one folder per template
  {slug}/
    template.csv    # Importable task list (Todoist CSV format)
    meta.yml        # Machine-readable metadata
    README.md       # Human-readable explanation & usage guidance

.github/
  scripts/
    create_todoist_project.py   # Python 3 script: creates a Todoist project from a template via REST API
  workflows/
    validate-templates.yml      # CI: validates all templates on push to main
    create-todoist-project.yml  # Manually triggered: creates a Todoist project from a chosen template
  ISSUE_TEMPLATE/
    template-request.yml        # GitHub issue form for requesting new templates

index.md            # Template catalogue (Markdown table)
CONTRIBUTING        # Contribution guidelines
CHANGELOG.md        # Version history
```

---

## Template Conventions

Every template lives at `templates/{slug}/` and must contain exactly three files.

### Folder Naming

- Folder name (slug) must be **kebab-case**: lowercase letters, digits, and hyphens only.
- Example: `saas-spin-up`, `daily-review`, `weekly-review`

### `meta.yml`

Required top-level keys (all must start at column 0):

```yaml
name: Human Readable Name
slug: folder-slug             # Must match the folder name exactly
description: One-line description
category: kebab-case-category
tags:
  - tag-one
  - tag-two
version: 1.0.0
```

Optional but recommended keys:
```yaml
estimated_duration: 15m
recurrence_suggestion: daily  # or weekly, as-needed, etc.
author: Name
```

### `template.csv`

- First line must be the header: `TYPE,CONTENT,PRIORITY,INDENT,AUTHOR,RESPONSIBLE,DUE_DATE,DUE_DATE_LANG`
- `TYPE` column: `section` or `task` (no other values allowed)
- `PRIORITY`: `1` (urgent/p1) → `4` (normal/p4) — the Python script maps these to Todoist API priorities
- `INDENT`: integer (1 = top-level task, 2 = subtask, etc.)
- **Never use hardcoded due dates** (`DUE_DATE` column should be empty)
- Rows with an empty `CONTENT` column are skipped by the importer

Example rows:
```csv
TYPE,CONTENT,PRIORITY,INDENT,AUTHOR,RESPONSIBLE,DUE_DATE,DUE_DATE_LANG
section,1️⃣ Section Name,,,,,,
task,Do something important,1,1,,,,,
task,A subtask of the above,2,2,,,,,
```

### `README.md`

Each template README should cover:
- What the template is for
- When to use it
- Overview of sections
- Import / usage instructions

---

## CI Validation

The `validate-templates.yml` workflow runs on every push to `main` and checks:

1. **Kebab-case folder name**
2. **Required files present**: `template.csv`, `meta.yml`, `README.md`
3. **`meta.yml` required keys**: `name:`, `slug:`, `description:`, `category:`, `tags:`, `version:`
4. **`meta.yml` slug matches folder name**
5. **`template.csv` header starts with `TYPE`**
6. **`TYPE` column values are only `section` or `task`**

To validate locally, copy the shell commands from the `run:` block of `.github/workflows/validate-templates.yml` and run them in a bash shell at the repo root. There is no standalone validation script — the YAML workflow file itself is not directly executable.

---

## GitHub Actions Workflows

### `validate-templates.yml`
- Triggered: push to `main`, `workflow_dispatch`
- Runs pure bash; no external dependencies
- Failure means a template does not meet structural requirements

### `create-todoist-project.yml`
- Triggered: `workflow_dispatch` (manual), or daily schedule at 11:00 UTC (defaults to `weekly-review`)
- Inputs: `template` (choice from available slugs), `project_name` (optional override)
- Requires repository secret: `TODOIST_API_TOKEN`
- Calls `.github/scripts/create_todoist_project.py` via `python3`
- When adding a new template, add its slug to the `options` list in this workflow

### Updating `create-todoist-project.yml` when adding a template

When a new template folder is added, add its slug to the `options` list under `inputs.template`:

```yaml
options:
  - new-template-slug
  - daily-review
  # ... existing slugs
```

---

## Python Script (`create_todoist_project.py`)

- Uses only Python 3 stdlib (`csv`, `json`, `os`, `sys`, `urllib`) — no pip dependencies
- Reads `TODOIST_API_TOKEN`, `TEMPLATE`, and optionally `PROJECT_NAME` from environment variables
- Calls Todoist REST API v1 (`https://api.todoist.com/api/v1`) to create the project, sections, and tasks
- Priority mapping: CSV `1` → API `4` (p1/urgent), CSV `4` → API `1` (p4/normal)
- Reads project name from `meta.yml` if `PROJECT_NAME` env var is not set
- Subtask nesting is resolved via an indent stack

---

## Adding a New Template — Checklist

1. Create folder `templates/{slug}/` (kebab-case)
2. Add `meta.yml` with all required keys; ensure `slug:` matches the folder name
3. Add `template.csv` with `TYPE` header; use only `section`/`task` types; no hardcoded due dates
4. Add `README.md` describing the workflow and usage
5. Add the slug to the `options` list in `.github/workflows/create-todoist-project.yml`
6. Update `index.md` to include the new template in the catalogue table
7. Push to `main` — CI will validate the template automatically

---

## Known Errors & Workarounds

- **`meta.yml` slug mismatch**: The CI check is case-sensitive and strips only single and double quotes. Ensure the `slug:` value is plain lowercase kebab-case with no surrounding quotes.
- **CSV TYPE validation caveat**: The CI uses a `while read` pipeline which runs in a subshell; a failed check inside the loop sets `failed=1` inside the subshell and does **not** propagate to the outer script. This means invalid TYPE values may not cause the CI to fail. Do not rely on CI alone to catch bad TYPE values — review CSVs manually.
- **No local test runner**: There is no `make`, `npm`, or `pytest` setup. The only automated checks are in CI. To validate locally, copy the shell commands from the `run:` block of `validate-templates.yml` and run them at the repo root.
