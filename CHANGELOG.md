# Changelog

## [Unreleased]

### Added

- Security: **OWASP gallery hardening** — gallery generator now emits a slim `index.html` with a strict `Content-Security-Policy` (`default-src 'none'; script-src 'self'; style-src 'self'`), `Referrer-Policy`, and `Permissions-Policy` meta tags; CSS and JavaScript are extracted to `docs/styles.css` and `docs/app.js` (no inline scripts or styles); `marked.js` and `DOMPurify` are vendored under `docs/vendor/` and loaded with SRI `integrity` attributes; a JSON data island (`<script type="application/json">`) replaces inline template data; `esc()` escapes `&`, `<`, `>`, `"`, and `'`; all README HTML is sanitised through `DOMPurify.sanitize(marked.parse(…))`; external links always carry `rel="noopener noreferrer"`; a new `assert_gallery_security.py` CI script asserts CSP, SRI, JSON island round-trip, absence of inline `<style>` content, and absence of inline event handlers on every build
- Wiki: **Releases** page (`wiki/Releases.md`) — documents the repository's release-and-tags strategy: CalVer release tags (`vYYYY.M.D`), per-asset SemVer in `meta.yml`, and Keep-a-Changelog conventions for `CHANGELOG.md`; linked from `wiki/Home.md` and summarised in a new `Releases and Tags` section in `CONTRIBUTING`
- CSV template format: **Extended Todoist importer header** documented as the canonical schema for new templates: `TYPE,CONTENT,DESCRIPTION,IS_COLLAPSED,PRIORITY,INDENT,AUTHOR,RESPONSIBLE,DATE,DATE_LANG,TIMEZONE,DURATION,DURATION_UNIT,DEADLINE,DEADLINE_LANG`. The legacy 8-column header remains fully supported.
- Scripts: `create_todoist_project.py`, `create_via_mcp.py` — now honour extended-format task fields (`TIMEZONE` → `due_timezone`, `DURATION` + `DURATION_UNIT`, `DEADLINE` + `DEADLINE_LANG` → `deadline_date` / `deadline_lang`). The MCP path additionally now passes `DESCRIPTION` to `create_task`.
- Repository: **Nested CSV template layout supported** — CSV templates may now live under `csv-templates/{slug}/` or `csv-templates/{group}/{slug}/`; validator, Python automation scripts, gallery, and release-asset generation all resolve templates by slug regardless of grouping
- Script: `.github/scripts/template_discovery.py` — shared helper providing canonical CSV template discovery (slug → on-disk directory) used by runtime, sync, validation, and generation scripts
- Dependabot: **Automated dependency management** — `.github/dependabot.yml` configured to monitor GitHub Actions on a weekly schedule; pull requests are grouped, labelled with `dependencies`, and auto-merged for patch, minor, and security updates via `dependabot-auto-merge.yml`
- Workflow: **GitHub Trending to Todoist** — daily automation that fetches trending GitHub repositories (today, this week, this month) and pushes them into a Todoist project as `read-later` tasks, grouped by period; supports optional language filtering and language-aware project naming
- Template: **GitHub Trending Tracker** — weekly review system for discovering, evaluating, and acting on trending GitHub repositories — using stars as signal and structured habits to convert insights into value
- Template: **Artist Interview Invite Workflow** — checklist for inviting an artist or band for a live studio interview and managing follow-through
- Prompt template: **Artist Interview Invite Email** — generate concise, high-impact studio interview invite emails for artists, bands, and representatives
- Gallery: live search bar added to the GitHub Pages template gallery — filters cards in real time as you type
- Gallery: **16 usability improvements** to the GitHub Pages gallery (`generate_gallery.py` → `docs/index.html`): deep links to templates (`#/template/<type>/<slug>`), search query in URL (`#/search/<query>`), tag filter chips with `aria-pressed` and hash persistence, sort menu (Name / Tasks / Version / Recently updated) with session-storage persistence, "Recently updated" horizontal scroll-snap rail on the home page, empty-search recovery buttons ("Clear search" / "Browse all categories"), modal "Open on GitHub" action, download caption ("Open in Todoist → Import from CSV"), simplified responsive breakpoints (1 col → 2 col → auto-fill), build provenance footer stamp (`Built YYYY-MM-DD · <sha>`), README asset rewrite for relative links/images, card GitHub deep-link icon, debounced search with loop-safe hashchange handling, tag+search intersection filter, sort persists per session via `sessionStorage`, and history-safe modal navigation (`pushState`/`back()`)
- Gallery: **Accessibility (WCAG 2.2 AA)** — 15-item a11y overhaul of `generate_gallery.py`: contrast token `--muted-light` raised to `#5a6472` (5.1:1); gradient darkened to `#9a3133`; skip link; `<main>` landmark; footer `<nav aria-label="Site">`; category cards converted to native `<a href="#/category/…">` anchors; template/spotlight cards converted to `<button type="button">`; all card titles promoted to semantic headings (`h2`/`h3`); modal title promoted to `<h2>`; modal gains `inert` background, keyboard focus trap, and a stack-based focus-return (cap 20); live region `<p role="status" aria-live="polite">` for search count; search-clear uses `hidden` attribute; `/` shortcut focuses search; `Esc` closes modal then clears search; all decorative emoji wrapped in `<span aria-hidden="true">`; differentiated `aria-label` on cards and inner action buttons; README headings down-shifted by one level in the modal; `<meta name="description">` added; contrast matrix comment in CSS

### Changed

- Agent: `SEO Accessibility Agent` - expanded guidance to review canonical links, Hugo canonical generation, and indexable-versus-non-indexable page handling during SEO and accessibility audits
- Templates (GitHub category): standardised `project_color` to `grape` for `github-repo-spin-up` and `repo-ecosystem-watch`, and refined `github-trending-repo-review` metadata (`description` tightened; tag `quality-signals` replaced with `stars`); `index.md` catalogue row was updated to match current metadata
- Template: `album-of-the-week-weekly-review` - added a new preparation task to tag copied audio files with KID3 immediately before the Lidarr re-download prevention step
- Template: `github-trending-repo-review` — moved to `csv-templates/github/github-trending-repo-review/`, display name changed to **GitHub Trending Repo Review**, and tag list aligned to `github, trending, open-source, discoverability, triage, stars, daily`; workflow inputs and the trending-sync follow-on have been updated to the renamed slug
- Template: `github-repo-spin-up` — moved to `csv-templates/github/github-repo-spin-up/`; slug is unchanged so workflow inputs and template discovery continue to work
- Workflow: `reusable-validate-templates.yml` — now discovers CSV templates one or two folder levels under `csv-templates/`, validates intermediate group folder names as kebab-case, and resolves `replacement_template` by slug regardless of nesting

- Scripts: `create_todoist_project.py`, `create_via_mcp.py` — both project creation scripts now map `DUE_DATE` / `DUE_DATE_LANG` CSV columns (and legacy `DATE` / `DATE_LANG` aliases) to Todoist task due fields, so due dates defined in template CSVs are applied on import
- Template: `github-trending-repo-review` — primary task renamed from "Evaluate Trending Repos today" to "Evaluate Trending Repos" for cleaner recurrence wording
- Script: `fetch_github_trending.py` — processed repository slugs are now persisted to `.github/data/github-trending-processed-slugs.json`, ensuring each repository is imported only once across all runs even if the original Todoist task is later edited or deleted; already-active and already-completed `read-later` tasks are also checked to prevent duplicates within a run; repositories that appear in multiple trending periods within the same run are also de-duplicated
- Workflow: `create-todoist-project.yml` — now automatically triggers after the `Sync GitHub Trending to Todoist` workflow completes successfully, creating the `github-trending-repo-review` review project as a follow-on step
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
- Template: `weekly-review` — currently at version `0.0.0` (unreviewed); duration labels and task wording were refined
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
