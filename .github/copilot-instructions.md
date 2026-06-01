# Copilot Instructions

This file is loaded into every Copilot turn. Keep it focused on always-relevant directives. Detailed conventions live in scoped instructions under `.github/instructions/` and load automatically when working in the matching folder.

## Repository overview

**todoist-playbook** is a curated collection of Todoist assets and the automation that validates, generates, and publishes them. There are three asset types:

- **CSV templates** under `csv-templates/` — importable Todoist task lists
- **Prompt templates** under `prompt-templates/` — AI prompts that produce task content
- **Bundles** under `bundles/` — curated multi-template starter kits

Supporting them: GitHub Actions workflows in `.github/workflows/`, Python scripts in `.github/scripts/`, reusable workflows / composite actions, issue forms, and a wiki under `wiki/`.

There is no application build, package manager, or unit-test framework. Correctness is enforced by the validation workflow.

## Canonical sources

When this file conflicts with the implementation, follow the implementation and update this file:

- [README.md](../README.md) — high-level repo model and user-facing workflows
- [CONTRIBUTING](../CONTRIBUTING) — branch, commit, versioning, and PR conventions (including Conventional Commits)
- [.github/workflows/reusable-validate-templates.yml](workflows/reusable-validate-templates.yml) — validation rules
- [.github/REUSABLE_WORKFLOWS.md](REUSABLE_WORKFLOWS.md) — reusable workflow / composite action usage

## Always-on directives

- Follow [CONTRIBUTING](../CONTRIBUTING) for GitHub Flow branching and Conventional Commits. Branch names must match `^(feature|fix|docs|chore)/[0-9]+-[a-z0-9-]+$`. PR titles use the same Conventional Commits format and become the squash-merge commit message.
- Folder names for templates, prompt templates, and bundles MUST be kebab-case and the folder name MUST equal the `slug:` in the asset's metadata file.
- New CSV templates and prompt templates start at `version: 0.0.0` (unreviewed). The `0.1.0` version means reviewed and stable. Reviewed assets receive automatic patch bumps via `bump-template-version.yml` when changed in a merged PR. Do not hand-bump versions.
- Treat `csv-templates/github/github-trending-repositories-daily-review/template.csv` as the structural exemplar for extended-format CSV templates. When editing other CSV templates, compare against this exemplar and preserve the canonical structure (column order and `meta,view_style=list` row) unless a repo-specific instruction explicitly requires a different format.
- When adding a discoverable asset, ALWAYS update `index.md`. Update workflow `inputs` option lists ONLY for the workflows that should expose the asset (see scoped workflow instructions).
- Update `README.md` only when user-facing discovery copy changes; routine asset additions go into `index.md` only.
- Preserve existing wording and structure unless the repo has clearly moved to a new convention.
- When proposing changes that touch multiple asset types or workflows, keep them in one logical PR (one branch per logical change).
- For every repository review request and every code/content change request (create, update, or delete), ALWAYS run the `SEO Accessibility Agent` as a mandatory guardrail pass before finalising recommendations or edits.
- This mandatory pass explicitly includes automation and publishing paths: `.github/scripts/**`, `.github/workflows/**`, `wiki/**`, `README.md`, `index.md`, and generated gallery outputs under `docs/**` whenever changes can affect GitHub Pages output.
- If the `SEO Accessibility Agent` flags violations, resolve them in the same change where possible; if not possible, report explicit blockers and required follow-up actions in the response.

## Scoped instructions (load automatically by path)

| Working in… | File |
|---|---|
| `csv-templates/**` | [.github/instructions/csv-templates.instructions.md](instructions/csv-templates.instructions.md) |
| `prompt-templates/**` | [.github/instructions/prompt-templates.instructions.md](instructions/prompt-templates.instructions.md) |
| `bundles/**` | [.github/instructions/bundles.instructions.md](instructions/bundles.instructions.md) |
| `.github/workflows/**` | [.github/instructions/workflows.instructions.md](instructions/workflows.instructions.md) |
| `.github/scripts/**` | [.github/instructions/scripts.instructions.md](instructions/scripts.instructions.md) |
| `wiki/**` | [.github/instructions/wiki.instructions.md](instructions/wiki.instructions.md) |

## Skills and custom agents

On-demand workflows live under `.github/skills/`; specialist personas live under `.github/agents/`. Prefer them over re-deriving procedures:

- Skills: `add-todoist-asset`, `validate-templates-locally`, `review-unreviewed-asset`, `open-pr`
- Agents: `template-reviewer` (read-only), `csv-doctor`, `prompt-template-author`, `asset-cataloguer` (read-only), `seo-accessibility`

## Local environment notes

- Primary development OS is Windows. Workflow `run:` blocks are bash; to validate locally, run them in Git Bash or WSL.
- The GitHub CLI (`gh`) is the standard tool for opening PRs from the command line.
- The repo default branch is `main`. Work follows GitHub Flow: create a short-lived branch matching `^(feature|fix|docs|chore)/[0-9]+-[a-z0-9-]+$`, open a PR to `main`, squash-merge, then delete the branch.
