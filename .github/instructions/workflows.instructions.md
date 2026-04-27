---
applyTo: ".github/workflows/**"
description: Inventory and behaviour of GitHub Actions workflows in this repo.
---

# Workflow Inventory

## Validation

- `validate-templates.yml` — entry point; delegates to the reusable validator
- `reusable-validate-templates.yml` — canonical validation rules for CSV templates and prompt templates

## Project creation

- `create-todoist-project.yml` — creates a Todoist project from a CSV template
- `create-todoist-project-from-prompt.yml` — runs a prompt template, then creates a Todoist project from the generated content
- `create-todoist-project-via-mcp.yml` — creates a Todoist project from a CSV template via the Todoist MCP server

## Maintenance and sync

- `sync-template-review-issues.yml` — opens or closes review issues based on `version: 0.0.0` state
- `sync-github-trending-to-todoist.yml` — fetches GitHub Trending repositories and pushes them into Todoist as `read-later` tasks
- `sync-todoist-projects.yml` — refreshes the `parent_project` dropdown options in `create-todoist-project.yml`
- `bump-template-version.yml` — bumps reviewed template / prompt-template patch versions when PRs into `main` are merged
- `triage-new-issues.yml` — labels new issues and adds them to the Todoist Playbook Roadmap project backlog
- `dependabot-auto-merge.yml` — approves eligible Dependabot PRs and enables auto-merge
- `copilot-setup-steps.yml` — verifies repo Python scripts still compile when the workflow file changes
- `doc-sync.md` / `doc-sync.lock.yml` — authoring source and compiled workflow for the documentation-sync agent that keeps `README.md`, `index.md`, and wiki pages aligned with the repo on a schedule

## Publishing and release

- `deploy-gallery.yml` — builds and deploys the gallery to GitHub Pages
- `release.yml` — publishes release assets

## Reusable building blocks

- `reusable-gallery-quality.yml` — generates the gallery, audits it with Lighthouse CI and pa11y-ci, uploads reports as artifacts
- `.github/REUSABLE_WORKFLOWS.md` documents reusable workflows and the `commit-and-push` composite action

## When editing workflows

- Keep workflow `inputs.template` / `inputs.prompt_template` option lists aligned with the assets that should be selectable in each workflow
- Update `.github/REUSABLE_WORKFLOWS.md` when adding or changing reusable workflows / composite actions
