# Roadmap

This page outlines the current state of the project and where it is headed. The Roadmap reflects the project's philosophy: reduce friction, improve consistency, and keep everything version-controlled and automatable.

---

## Current State

The Playbook is a functioning system with:

- ✅ 30+ curated task templates across productivity, engineering, media, and personal domains
- ✅ Starter-kit bundles for common life scenarios
- ✅ AI prompt templates for enriched task generation
- ✅ GitHub Actions workflows for one-click Todoist project creation
- ✅ MCP-based Todoist project creation (via Todoist MCP server)
- ✅ Automated CI validation on every push and pull request
- ✅ Automated template version bumping on every PR
- ✅ Daily documentation sync powered by GitHub Copilot
- ✅ Template gallery deployed to GitHub Pages
- ✅ Dependabot monitoring for GitHub Actions dependencies
- ✅ Issue and pull request templates

---

## Near-Term (Next Quarter)

### Template library expansion

- [ ] Additional engineering templates: incident response, post-mortem, architecture decision record
- [ ] More agile ceremony templates: sprint planning, backlog refinement
- [ ] Personal productivity templates: quarterly review, goal-setting, travel checklist

### Template quality

- [ ] Bump all `0.0.0` (unreviewed) templates to `0.1.0` after manual review
- [ ] Add `estimated_duration` and `recurrence_suggestion` metadata to all reviewed templates

### Automation improvements

- [ ] Scheduled workflow to auto-create `daily-review` project each morning
- [ ] Workflow input to set the Todoist project view (`list`, `board`, `calendar`)
- [ ] Support for creating tasks with descriptions (not just titles) via the API

---

## Medium-Term

### Template authoring experience

- [ ] A CLI (`cli/`) to scaffold a new template folder with all required files and correct structure
- [ ] Linting for template CSV content (e.g. warn on suspiciously long CONTENT values)
- [ ] Template preview in the GitHub Pages gallery (rendered task tree view)

### Discoverability

- [ ] Submit to curated Awesome Lists (using the `awesome-list-submission` template itself)
- [ ] Template tags searchable in the GitHub Pages gallery
- [ ] `category` filter in the gallery

### Community

- [ ] Template contribution workflow with automated review checklist
- [ ] Showcase section for community-contributed templates
- [ ] Discussion board for template ideas and workflow tips

---

## Longer-Term

### Advanced automation

- [ ] Webhook trigger: create a Todoist project from an incoming GitHub issue label
- [ ] Two-way sync: completed Todoist tasks reflected back as GitHub issue comments
- [ ] Template parameterisation: fill in `{{placeholders}}` in `template.csv` before creating the project (analogous to prompt templates)

### Multi-tool support

- [ ] Export templates to Asana, Linear, or Notion format
- [ ] GitHub Projects integration: create a GitHub Project board alongside the Todoist project
- [ ] Obsidian integration: create a vault note for the project at the same time

### Ecosystem

- [ ] Public template registry: a curated index of community template repositories that follow the Playbook format
- [ ] Template versioning dashboard: a visual summary of which templates are reviewed and up to date

---

## Completed

| Item | Released |
|------|---------|
| Initial template library (daily review, weekly review, code review, sprint ceremonies) | Early 2024 |
| GitHub Actions workflow for one-click project creation | Early 2024 |
| CI validation workflow | Early 2024 |
| Starter-kit bundles | 2024 |
| AI prompt templates | 2024 |
| Template versioning (`0.0.0` / `0.1.0` semantics) | 2024 |
| Automated version bump on PR | 2024 |
| Dependabot for GitHub Actions | 2025 |
| MCP-based project creation workflow | 2025 |
| Documentation sync powered by GitHub Copilot | 2025 |
| Sync Todoist project list workflow (parent project dropdown) | 2025 |
| Template gallery on GitHub Pages | 2025 |
| Issue and pull request templates | 2025 |
| Scheduled weekly-close and weekly-plan project creation | 2025 |

---

## Contributing to the Roadmap

Ideas and suggestions are welcome. Please open an issue using the [template request form](https://github.com/colin-gourlay/todoist-playbook/issues/new?template=template-request.yml) or start a discussion in the GitHub Discussions tab.

If you would like to work on one of the items above, open an issue to claim it before submitting a pull request.
