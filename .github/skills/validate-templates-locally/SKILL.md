---
name: validate-templates-locally
description: 'Run the validate-templates checks locally on Windows before pushing. Use when the user wants to validate templates locally, run validation, check meta.yml, verify CSV header, or reproduce CI validation failures.'
---

# Run validate-templates Locally

## When to Use

- Before pushing a template / prompt-template change
- To reproduce a `validate-templates.yml` CI failure locally
- After hand-editing `meta.yml`, `template.csv`, `prompt.md`, or `bundle.yml`

## Prerequisites

- Windows + Git Bash (or WSL). PowerShell will not run the workflow's bash blocks correctly.
- Repo cloned and the asset to validate already on disk.

## Procedure

### 1. Open Git Bash at the repo root

```bash
cd /c/Users/<you>/path/to/todoist-playbook
```

### 2. Mirror the workflow's validation steps

Open [.github/workflows/reusable-validate-templates.yml](../../workflows/reusable-validate-templates.yml) and copy each `run:` block in turn into Git Bash. The workflow is the single source of truth for validation logic — do not maintain a parallel script.

Typical checks include:

- Folder name is kebab-case
- Required files exist (`template.csv` + `meta.yml` + `README.md`, or `prompt.md` + `meta.yml` + `README.md`)
- `meta.yml` contains every required key
- `meta.yml` `slug:` equals the folder name
- `template.csv` first line equals the canonical TYPE header
- `template.csv` `TYPE` column values are only `section`, `task`, or `meta`
- `project_color` (when present) appears in [.github/scripts/project_colors.txt](../../scripts/project_colors.txt)
- Prompt templates: `prompt.md` contains at least one `{{placeholder}}` and `inputs:` is present in `meta.yml`

### 3. Fix and re-run

Re-run the failing block after each fix until clean. If a check seems wrong, treat the workflow as canonical — fix the asset, not the check.

### 4. Push and let CI confirm

Even after a clean local run, push the branch and let `validate-templates.yml` confirm in CI before opening / updating a PR.

## Common failure modes

- `meta.yml` slug has stray quotes or trailing whitespace
- `README.md` is missing import instructions for a CSV template
- `project_color` value is not in the allow-list
- Prompt template `inputs:` and `{{placeholder}}` names disagree
- Hardcoded date in CSV `DUE_DATE`
