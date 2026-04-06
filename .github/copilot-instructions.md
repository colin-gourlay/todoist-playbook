# Copilot Instructions

## Repository Overview

**todoist-playbook** is a curated collection of Todoist assets and automation tooling. The repository now contains three primary asset types:

- Reusable CSV-based Todoist templates
- AI prompt templates for generating enriched task content
- Bundles that group related templates into starter kits

Supporting those assets is a growing set of GitHub Actions workflows, Python scripts, reusable workflows, composite actions, prompts, and wiki documentation.

There is no application build, package manager, or unit-test framework in this repository. Correctness is enforced primarily through GitHub Actions validation and repository automation.

---

## Repository Structure

```
csv-templates/            # CSV-based Todoist templates
  {slug}/
    template.csv          # Importable Todoist task list
    meta.yml              # Machine-readable metadata
    README.md             # Human-readable explanation and import guidance

prompt-templates/         # AI prompt templates
  {slug}/
    prompt.md             # Prompt with {{placeholders}}
    meta.yml              # Prompt metadata, including inputs
    README.md             # Usage guidance and examples

bundles/                  # Curated multi-template starter kits
  {slug}/
    bundle.yml            # Bundle metadata and included template slugs
    README.md             # Human-readable explanation and usage guidance

.github/
  actions/                # Composite actions used by workflows
  copilot-spaces/         # Copilot Space configuration
  prompts/                # Reusable GitHub prompt files
  scripts/                # Python automation scripts
  workflows/              # Validation, creation, sync, deploy, and release workflows
  ISSUE_TEMPLATE/         # GitHub issue forms
  REUSABLE_WORKFLOWS.md   # Documentation for reusable workflows/actions

wiki/                     # Architecture, setup, screenshots, roadmap, and supporting docs
index.md                  # Catalogue of templates, prompt templates, bundles, and workflows
README.md                 # Primary high-level repo guide
CONTRIBUTING              # Contributor workflow and conventions
CHANGELOG.md              # Version history
```

---

## Canonical Sources

When the repository evolves, prefer these files as the source of truth:

- `README.md` for the current high-level repo model and user-facing workflows
- `CONTRIBUTING` for branch, commit, versioning, and contribution expectations
- `.github/workflows/reusable-validate-templates.yml` for validation rules
- `.github/workflows/create-todoist-project.yml` for CSV-template workflow inputs
- `.github/workflows/create-todoist-project-from-prompt.yml` for prompt-template workflow inputs
- `.github/workflows/create-todoist-project-via-mcp.yml` for MCP-based project creation
- `.github/REUSABLE_WORKFLOWS.md` for reusable workflow and composite action usage

If this file conflicts with the files above, follow the implementation and update this file.

---

## Asset Conventions

### CSV Templates

Every CSV template lives at `csv-templates/{slug}/` and must contain exactly three files:

- `template.csv`
- `meta.yml`
- `README.md`

Folder names must be kebab-case: lowercase letters, digits, and hyphens only.

Required top-level `meta.yml` keys:

```yaml
name: Human Readable Name
slug: folder-slug
description: One-line description
category: kebab-case-category
tags:
  - tag-one
version: 0.0.0
```

Common optional `meta.yml` keys:

```yaml
estimated_duration: 15m
recurrence_suggestion: weekly
author: Name
project_color: blue
```

`template.csv` rules:

- First line must be `TYPE,CONTENT,PRIORITY,INDENT,AUTHOR,RESPONSIBLE,DUE_DATE,DUE_DATE_LANG`
- `TYPE` must be `section` or `task`
- `PRIORITY` values are `1` to `4`, with the import script mapping CSV `1` to Todoist API priority `4` and CSV `4` to API priority `1`
- `INDENT` is an integer nesting level
- Do not hardcode due dates in `DUE_DATE`
- Rows with empty `CONTENT` are skipped by the importer
- `README.md` must include import instructions or clearly mention CSV import

### Prompt Templates

Every prompt template lives at `prompt-templates/{slug}/` and must contain:

- `prompt.md`
- `meta.yml`
- `README.md`

Required `meta.yml` keys:

```yaml
name: Human Readable Name
slug: folder-slug
description: One-line description
category: kebab-case-category
tags:
  - tag-one
version: 0.0.0
inputs:
  - input_name
```

Prompt template rules:

- Folder name must be kebab-case
- `slug:` must match the folder name exactly
- `prompt.md` must contain `{{placeholder}}` variables
- Use `{{placeholder}}` syntax consistently for all declared inputs
- Keep prompts provider-agnostic where practical
- Define a clear output shape in the prompt and explain usage in `README.md`
- Include at least one worked example in `README.md`

### Bundles

Bundles live at `bundles/{slug}/` and currently use:

- `bundle.yml`
- `README.md`

Typical `bundle.yml` fields:

```yaml
name: Bundle Name
slug: bundle-slug
description: One-line description
category: kebab-case-category
tags:
  - tag-one
version: 1.0.0
templates:
  - template-slug
```

Bundle `templates:` entries should reference existing template slugs.

---

## Validation Rules

The canonical validator is `.github/workflows/reusable-validate-templates.yml`. The top-level `validate-templates.yml` workflow delegates to it.

### CSV Template Validation

The validator checks:

1. Kebab-case folder name
2. Required files: `template.csv`, `meta.yml`, `README.md`
3. Required `meta.yml` keys: `name:`, `slug:`, `description:`, `category:`, `tags:`, `version:`
4. `meta.yml` slug matches the folder name
5. Optional `project_color` is valid against `.github/scripts/project_colors.txt`
6. `README.md` contains import instructions or mentions CSV import
7. `template.csv` starts with the `TYPE` header
8. `TYPE` column values are only `section` or `task`

### Prompt Template Validation

The validator checks:

1. Kebab-case folder name
2. Required files: `prompt.md`, `meta.yml`, `README.md`
3. Required `meta.yml` keys: `name:`, `slug:`, `description:`, `category:`, `tags:`, `version:`, `inputs:`
4. `meta.yml` slug matches the folder name
5. `prompt.md` contains at least one `{{placeholder}}` variable

To validate locally, copy the shell commands from the `run:` blocks in `.github/workflows/reusable-validate-templates.yml` and run them from the repo root in a bash-compatible shell.

---

## Workflow Inventory

### Validation

- `validate-templates.yml` validates templates and prompt templates via the reusable validator
- `reusable-validate-templates.yml` is the source of truth for validation rules

### Project Creation

- `create-todoist-project.yml` creates a Todoist project from a CSV template
- `create-todoist-project-from-prompt.yml` generates content from a prompt template, then creates a Todoist project
- `create-todoist-project-via-mcp.yml` creates a project from a CSV template via the Todoist MCP server

### Maintenance and Sync

- `sync-template-review-issues.yml` opens or closes review issues based on template version state
- `sync-github-trending-to-todoist.yml` fetches GitHub Trending repositories and pushes them into Todoist as `read-later` tasks
- `sync-todoist-projects.yml` refreshes the `parent_project` dropdown in `create-todoist-project.yml`
- `bump-template-versions.yml` bumps reviewed template and prompt-template patch versions on pull requests
- `triage-new-issues.yml` labels new issues and adds them to the Todoist Playbook Roadmap project backlog
- `dependabot-auto-merge.yml` approves eligible Dependabot pull requests and enables auto-merge
- `copilot-setup-steps.yml` verifies the repository Python automation scripts still compile when the workflow file changes
- `doc-sync.md` is the authoring source for the documentation-maintenance agent workflow
- `doc-sync.lock.yml` is the compiled workflow file that executes the documentation sync on schedule

### Publishing and Release

- `deploy-gallery.yml` builds and deploys the gallery to GitHub Pages
- `release.yml` publishes release assets
- Reusable workflows and the `commit-and-push` composite action are documented in `.github/REUSABLE_WORKFLOWS.md`

---

## Python Scripts

Important scripts under `.github/scripts/` include:

- `create_todoist_project.py` for direct Todoist API project creation from CSV templates
- `run_prompt_template.py` for prompt-template-driven project creation
- `create_via_mcp.py` for MCP-based project creation
- `fetch_github_trending.py` for GitHub Trending ingestion and Todoist sync
- `sync_template_review_issues.py` for issue synchronization against template versions
- `sync_project_options.py` for updating `parent_project` options in `create-todoist-project.yml`
- `bump_template_versions.py` for patch-version automation on pull requests
- `generate_gallery.py` and `generate_release_assets.py` for publishing workflows

The automation scripts use Python 3 and are intended to run in GitHub Actions without a separate dependency-management setup.

---

## Versioning and Review State

Template and prompt-template versioning follows the conventions documented in `README.md` and `CONTRIBUTING`:

- `0.0.0` means unreviewed
- `0.1.0` means reviewed and considered stable
- reviewed assets may receive automatic patch bumps when changed in pull requests

The `sync-template-review-issues.yml` workflow treats `version: 0.0.0` templates as needing review and keeps GitHub issues aligned with that state.

When creating a new template or prompt template, start at `0.0.0` unless the repository conventions change.

---

## Contribution Expectations for AI Changes

When proposing or making changes in this repository:

- Follow the conventions in `CONTRIBUTING`
- Keep branch and PR naming aligned with the documented prefixes and Conventional Commits style
- Update documentation when adding or changing templates, prompt templates, bundles, workflows, or scripts
- Do not assume every new template must appear in every workflow; update the relevant workflow option lists intentionally
- Preserve existing wording and structure unless the repo has clearly moved to a new convention
- Check `index.md`, `README.md`, and workflow input options whenever adding discoverable assets

---

## Adding a New CSV Template

1. Create `csv-templates/{slug}/` using kebab-case
2. Add `meta.yml`, `template.csv`, and `README.md`
3. Ensure `meta.yml` includes all required keys and `slug:` matches the folder
4. Use `version: 0.0.0` for new unreviewed templates
5. Keep `DUE_DATE` empty and use only `section` or `task` in the CSV `TYPE` column
6. Include import instructions in `README.md`
7. Update `index.md`
8. Update `README.md` if user-facing guidance should mention the new asset
9. Add the slug to `create-todoist-project.yml` if it should be available in the standard workflow
10. Add the slug to `create-todoist-project-via-mcp.yml` if it should also be available via MCP

## Adding a New Prompt Template

1. Create `prompt-templates/{slug}/` using kebab-case
2. Add `prompt.md`, `meta.yml`, and `README.md`
3. Ensure `meta.yml` includes `inputs:` and all other required keys
4. Ensure `prompt.md` uses `{{placeholder}}` variables that match the declared inputs
5. Document the expected output format and include at least one worked example
6. Use `version: 0.0.0` for new unreviewed prompt templates
7. Update `index.md`
8. Update `README.md` if user-facing guidance should mention the new prompt workflow
9. Add the slug to `create-todoist-project-from-prompt.yml` if it should be selectable in the workflow

## Adding a New Bundle

1. Create `bundles/{slug}/` using kebab-case
2. Add `bundle.yml` and `README.md`
3. Ensure `bundle.yml` references existing CSV template slugs in `templates:`
4. Update `index.md`
5. Update `README.md` if the bundle changes user-facing discovery or usage guidance

---

## Known Errors and Workarounds

- `meta.yml` slug mismatch: check for quotes, leading or trailing spaces, or folder-name mismatch
- Missing README import guidance: ensure template `README.md` contains import instructions or explicitly mentions CSV import
- Invalid `project_color`: use one of the values listed in `.github/scripts/project_colors.txt`
- Prompt template validation failure: ensure `inputs:` exists in `meta.yml` and `prompt.md` includes `{{placeholder}}` variables
- No local test runner: use the workflow `run:` blocks as the closest equivalent of local validation
