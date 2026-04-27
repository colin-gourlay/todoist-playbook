---
applyTo: ".github/scripts/**"
description: Inventory and conventions for Python automation scripts.
---

# Python Script Inventory

Scripts under `.github/scripts/` run inside GitHub Actions. They use Python 3 and have no separate dependency-management setup — keep them stdlib-first and only add third-party imports when the workflow already installs them.

## Scripts

- `create_todoist_project.py` — direct Todoist API project creation from a CSV template
- `run_prompt_template.py` — prompt-template-driven project creation
- `create_via_mcp.py` — MCP-based project creation
- `fetch_github_trending.py` — GitHub Trending ingestion and Todoist sync
- `sync_template_review_issues.py` — issue sync against template `version:` state
- `sync_project_options.py` — updates `parent_project` options in `create-todoist-project.yml`
- `bump_template_versions.py` — patch-version automation on merged PRs
- `generate_gallery.py` — gallery build for GitHub Pages
- `generate_release_assets.py` — release-asset bundling

## Conventions

- Scripts are invoked from workflows; expect inputs via env vars or CLI args
- Keep scripts idempotent where possible — they may be re-run by the same workflow
- `copilot-setup-steps.yml` runs `py_compile` over scripts; new scripts MUST compile cleanly under the Python version pinned in that workflow
