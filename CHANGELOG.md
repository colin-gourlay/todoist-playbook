# Changelog

## [Unreleased]

### Added

- Template: **Repo Profile Audit** — baseline audit to align public references to a repository — canonical naming, link consistency, social and profile updates, directory listings, link validation, and follow-up tracking for unresolved external references. Derived from the Socials Health & Optimisation Checklist and scoped to a single repository.

- Template: **Weekly Commitment Reset** — weekly audit and reset of all active commitments; triage @waiting items, review @someday tasks, process the @review queue, and recommit only to what matters
- Wiki: added project wiki pages (`Home`, `Problem Statement`, `Architecture`, `Setup`, `Screenshots`, `Roadmap`) to the `wiki/` folder
- Script: `.github/scripts/generate_gallery.py` — added template spotlight feature to the GitHub Pages gallery
- Template: **Awesome List Outreach Shortlist** — pre-qualified shortlist of target Awesome Lists for this repository, with quality signal checklist, reusable submission message template, and submission tracking table

### Changed

- Template: `weekly-review` — refined task duration labels for the "Close the Past" section: "Review completed tasks from last week" changed to `@duration-5m`, "Celebrate wins (write 3)" changed to `@duration-10m`, and "Identify unfinished commitments" changed to `@duration-15m`
- Template: `weekly-review` — bumped version to `0.1.0` (manually reviewed and considered stable)
- Template: `weekly-review` — refined task wording for clarity, added a calendar review step to the Plan the Future section, and reordered Stop / Start / Continue tasks so Convert START item follows immediately after START
- Workflow: `create-todoist-project.yml` — added scheduled triggers to auto-create a weekly review project every Friday at 15:00 UTC and every Sunday at 05:00 UTC

- Renamed template `certification-exam` to `exam-certification-workflow`
- Sorted workflow dispatch template options alphabetically in `create-todoist-project.yml`
- `parent_project` input in `create-todoist-project.yml` is now a dropdown (`type: choice`) populated with existing Todoist project names instead of a free-text field

### Added

- Script: `.github/scripts/sync_project_options.py` — fetches all Todoist projects via the API and rewrites the `parent_project` options in `create-todoist-project.yml`
- Workflow: `sync-todoist-projects.yml` — runs daily (and on demand) to keep the `parent_project` dropdown in sync with the Todoist account

- Template: **Awesome List Submission** — end-to-end workflow for getting a GitHub repository listed on curated Awesome Lists — repo readiness, list targeting, submission, and follow-up
- Template: **Code Review Checklist** — structured checklist for performing thorough code reviews across any language or repository
- `bundles/` folder introducing multi-template starter kits
- Bundle: `new-job` — onboarding, weekly review, and 1:1 meeting templates for starting a new job
- Bundle: `radio-show-week` — full radio show production workflow
- Bundle: `house-admin` — annual household administration checklist
- Template: `onboarding-checklist` — structured first-90-days checklist for a new job
- Template: `one-on-one` — recurring 1:1 meeting preparation and follow-up
- Template: `house-admin` — household admin covering bills, renewals, MOT, and property maintenance
- Updated `index.md` with Bundles section, Career & Meetings section, and Home & Personal section
- Workflow: `create-todoist-project-via-mcp.yml` — creates a Todoist project from any CSV template by connecting to the Todoist MCP server (`https://ai.todoist.net/mcp`) using the MCP Streamable HTTP transport
- Script: `.github/scripts/create_via_mcp.py` — minimal MCP client (stdlib only) that initialises a session, discovers tools via `tools/list`, and calls `create_project`, `create_section`, and `create_task` in sequence
- Updated `index.md` with MCP Workflows section
- Workflow: `doc-sync.lock.yml` — runs daily to automatically detect documentation files that are out of sync with recent code or content changes, and opens a pull request with the necessary updates

