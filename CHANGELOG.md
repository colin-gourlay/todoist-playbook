# Changelog

## [Unreleased]

### Added

- Workflow: **GitHub Trending to Todoist** — daily automation that fetches trending GitHub repositories (today, this week, this month) and pushes them into a Todoist project as `read-later` tasks, grouped by period; supports optional language filtering and language-aware project naming
- Template: **GitHub Trending Tracker** — weekly review system for discovering, evaluating, and acting on trending GitHub repositories — using stars as signal and structured habits to convert insights into value
- Template: **Artist Interview Invite Workflow** — checklist for inviting an artist or band for a live studio interview and managing follow-through
- Prompt template: **Artist Interview Invite Email** — generate concise, high-impact studio interview invite emails for artists, bands, and representatives
- Gallery: live search bar added to the GitHub Pages template gallery — filters cards in real time as you type

### Changed

- Script: `fetch_github_trending.py` — already-processed repositories (both active and completed `read-later` tasks in Todoist) are now excluded from each import run, preventing duplicate tasks; repositories that appear in multiple trending periods within the same run are also de-duplicated
- Workflow: `create-todoist-project.yml` — now automatically triggers after the `Sync GitHub Trending to Todoist` workflow completes successfully, creating the `github-trending-repos-daily-review` review project as a follow-on step
- Template: `github-trending-tracker` — marked as deprecated in `meta.yml` with a planned sunset date and replacement guidance
- Script: `sync_project_options.py` — now excludes CSV templates marked `deprecated: true` from workflow template dropdown auto-generation
- Workflow: `reusable-validate-templates.yml` — now enforces deprecation sunsets by failing validation when a `deprecated: true` template reaches `sunset_date`
- Script: `sync_template_review_issues.py` — now creates and maintains `deprecation-sunset` issues for deprecated templates that have reached `sunset_date`
- Bundle: `radio-show-week-kit` — `artist-interview-invite-workflow` added as an optional template
- Template: `weekly-review` — "Empty inbox to zero" task duration changed from `@duration-15m` to `@duration-10m`
- Workflow: `sync-github-trending-to-todoist.yml` — added optional multi-language filtering (`languages` input); project names are now lowercase kebab-case by default; task descriptions now include language, stars, forks, and star-velocity metrics; language-aware project naming appended when filters are active
- Workflow: `validate-templates.yml` — validation now also triggers on changes to `release.yml`, `reusable-release-assets.yml`, and `generate_release_assets.py`; release workflow is gated on passing validation and now includes prompt template assets in the release ZIP

---

### Added (Historical)

- Template: **Repo Ecosystem Watch** — recurring 4-week checklist for monitoring adjacent repositories, reviewing maintenance signals, and converting ecosystem insights into actionable follow-up tasks.
- Wiki: **Repo Ecosystem Watch** page — persisted shortlist of Todoist-native and adjacent productivity repositories with manual Watch/Star guidance and review prompts.
- Template: **Repo Profile Audit** — baseline audit to align public references to a repository — canonical naming, link consistency, social and profile updates, directory listings, link validation, and follow-up tracking for unresolved external references. Derived from the Socials Health & Optimisation Checklist and scoped to a single repository.

- Template: **Weekly Commitment Reset** — weekly audit and reset of all active commitments; triage @waiting items, review @someday tasks, process the @review queue, and recommit only to what matters
- Wiki: added project wiki pages (`Home`, `Problem Statement`, `Architecture`, `Setup`, `Screenshots`, `Roadmap`) to the `wiki/` folder
- Script: `.github/scripts/generate_gallery.py` — added template spotlight feature to the GitHub Pages gallery
- Template: **Awesome List Outreach Shortlist** — pre-qualified shortlist of target Awesome Lists for this repository, with quality signal checklist, reusable submission message template, and submission tracking table
- Template: **GitHub Repo Spin-Up** — end-to-end checklist for spinning up a new GitHub repository — covering identity, documentation, CI/CD, security, Copilot integration, and developer hygiene
- Template: **Radio Show Core Workflow** — core weekly workflow for preparing and delivering a radio show — creative prep, logistics, studio setup, and live broadcast
- Template: **Radio Show Guest Feature** — workflow for preparing and running a guest or feature segment — interviews, artist spotlights, and festival coverage
- Template: **Radio Show Post Production** — publishing and archiving workflow after a radio broadcast — site publishing, media distribution, and reflection
- Template: **Radio Show Promotion** — workflow for promoting a radio show across social channels — pre-show announcements and post-show engagement
- Bundle: **Radio Show Week Kit** — complete system for producing a weekly radio show — core workflow, promotion, post production, and optional guest features

### Changed

- Migration: renamed top-level CSV template folder from `templates/` to `csv-templates/` across workflows, scripts, and docs; release ZIP asset path updated from `dist/templates.zip` to `dist/csv-templates.zip`

- Template: `github-repo-spin-up` — added a Section 1 checklist reminder to run the Repo Ecosystem Watch exercise during repository setup, and updated supporting template documentation to match.
- Template: `weekly-review` — refined task duration labels for the "Close the Past" section: "Review completed tasks from last week" changed to `@duration-5m`, "Celebrate wins (write 3)" changed to `@duration-10m`, and "Identify unfinished commitments" changed to `@duration-15m`
- Template: `weekly-review` — bumped version to `0.1.0` (manually reviewed and considered stable)
- Template: `weekly-review` — refined task wording for clarity, added a calendar review step to the Plan the Future section, and reordered Stop / Start / Continue tasks so Convert START item follows immediately after START
- Workflow: `create-todoist-project.yml` — added scheduled triggers for automated Friday and Sunday project creation
- Renamed template `certification-exam` to `exam-certification-workflow`
- Sorted workflow dispatch template options alphabetically in `create-todoist-project.yml`
- `parent_project` input in `create-todoist-project.yml` is now a dropdown (`type: choice`) populated with existing Todoist project names instead of a free-text field

### Added

- Template: **Weekly Close** — Friday shutdown review to close loops, process commitments, and capture learnings
- Template: **Weekly Plan** — Sunday planning session to define priorities, schedule commitments, and start the week with clarity
- Workflow: `sync-template-review-issues.yml` — runs daily (and on push to main) to keep GitHub issues aligned with unreviewed templates; creates or re-opens one issue per template at `version: 0.0.0` and closes issues automatically when templates are reviewed
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
