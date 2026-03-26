# Architecture

This page describes how the Todoist Playbook repository is structured, how its components interact, and how data flows from a template file to a live Todoist project.

---

## High-Level Overview

```
┌─────────────────────────────────────────────────────┐
│                  GitHub Repository                   │
│                                                     │
│  ┌───────────┐  ┌───────────┐  ┌─────────────────┐ │
│ │csv-templates/│ │  bundles/ │ │ prompt-templates/│ │
│  │  (CSV +   │  │ (grouped  │  │  (AI prompts +  │ │
│  │  meta.yml)│  │ templates)│  │   meta.yml)     │ │
│  └─────┬─────┘  └─────┬─────┘  └────────┬────────┘ │
│        │              │                  │           │
│        └──────────────┴──────────────────┘           │
│                        │                             │
│              ┌─────────▼──────────┐                 │
│              │  GitHub Actions    │                 │
│              │  Workflows         │                 │
│              └─────────┬──────────┘                 │
└────────────────────────┼────────────────────────────┘
                         │
          ┌──────────────┴───────────────┐
          │                              │
   ┌──────▼──────┐               ┌───────▼──────┐
   │  Todoist    │               │  GitHub Pages │
   │  REST API   │               │  (Gallery)   │
   │  v1         │               │              │
   └─────────────┘               └──────────────┘
```

---

## Repository Structure

```
todoist-playbook/
├── csv-templates/                # Individual reusable CSV templates
│   └── {slug}/
│       ├── template.csv          # Importable task list (Todoist CSV format)
│       ├── meta.yml              # Machine-readable metadata
│       └── README.md             # Human-readable usage guide
│
├── prompt-templates/             # AI prompt templates
│   └── {slug}/
│       ├── prompt.md             # Prompt with {{placeholders}}
│       ├── meta.yml              # Metadata
│       └── README.md             # Usage guide
│
├── bundles/                      # Multi-template starter kits
│   └── {slug}/
│       ├── meta.yml              # Bundle metadata
│       └── README.md             # Bundle description
│
├── wiki/                         # This project wiki
│
├── index.md                      # Template catalogue (Markdown table)
├── CHANGELOG.md                  # Version history
├── CONTRIBUTING                  # Contribution guidelines
│
└── .github/
    ├── scripts/                  # Python automation scripts
    │   ├── create_todoist_project.py
    │   ├── create_via_mcp.py
    │   ├── run_prompt_template.py
    │   ├── generate_gallery.py
    │   ├── bump_template_versions.py
    │   ├── sync_project_options.py
    │   ├── generate_release_assets.py
    │   └── project_colors.txt
    ├── workflows/                # GitHub Actions
    │   ├── create-todoist-project.yml
    │   ├── create-todoist-project-from-prompt.yml
    │   ├── create-todoist-project-via-mcp.yml
    │   ├── validate-templates.yml
    │   ├── bump-template-versions.yml
    │   ├── deploy-gallery.yml
    │   ├── doc-sync.md
    │   ├── sync-todoist-projects.yml
    │   └── release.yml
    ├── ISSUE_TEMPLATE/
    └── assets/
```

---

## Template Format

### `template.csv`

Todoist's native CSV import format. Every template CSV starts with the canonical header:

```
TYPE,CONTENT,PRIORITY,INDENT,AUTHOR,RESPONSIBLE,DUE_DATE,DUE_DATE_LANG
```

| Column | Values | Notes |
|--------|--------|-------|
| `TYPE` | `section`, `task` | No other values are valid |
| `CONTENT` | Any string | Rows with empty content are skipped |
| `PRIORITY` | `1`–`4` | `1` = urgent (p1), `4` = normal (p4) |
| `INDENT` | Integer ≥ 1 | `1` = top-level, `2` = subtask, etc. |
| `DUE_DATE` | Always empty | Hardcoded dates are never used |

### Priority Mapping

The Python script maps CSV priorities to the Todoist API scale (which is inverted):

| CSV value | Todoist UI label | API value |
|-----------|-----------------|-----------|
| `1` | p1 / Urgent | `4` |
| `2` | p2 / High | `3` |
| `3` | p3 / Medium | `2` |
| `4` | p4 / Normal | `1` |

### `meta.yml`

Machine-readable metadata used by the automation scripts and CI validation:

```yaml
name: Human Readable Name
slug: folder-slug             # Must match the folder name exactly
description: One-line description
category: kebab-case-category
tags:
  - tag-one
  - tag-two
version: 1.0.0
# Optional:
project_color: blue           # Must be a valid Todoist colour name
estimated_duration: 15m
recurrence_suggestion: weekly
author: Name
```

---

## Automation Workflows

### Create Todoist Project from Template

```
User triggers workflow_dispatch
         │
         ▼
  Select template slug
  (+ optional project name, colour, favourite, parent)
         │
         ▼
  create_todoist_project.py runs:
    1. Reads template.csv
    2. Reads meta.yml (project name, colour)
    3. POST /projects  → creates project
    4. POST /sections  → creates each section row
    5. POST /tasks     → creates each task row
       (with parent_id for subtasks via indent stack)
         │
         ▼
  Project appears in Todoist
```

The script uses only Python 3 standard library (`csv`, `json`, `os`, `sys`, `urllib`) — no pip dependencies required.

### Create Todoist Project from Prompt Template

```
User triggers workflow_dispatch
         │
         ▼
  Select prompt template + enter task_title + context
         │
         ▼
  run_prompt_template.py:
    1. Reads prompt.md and substitutes {{placeholders}}
    2. Calls GitHub Copilot API to generate enriched task content
    3. Writes structured output to a temp CSV
         │
         ▼
  create_todoist_project.py runs on the generated CSV
         │
         ▼
  Enriched project appears in Todoist
```

### Create Todoist Project via MCP

```
User triggers workflow_dispatch
         │
         ▼
  create_via_mcp.py:
    1. Connects to Todoist MCP server (https://ai.todoist.net/mcp)
    2. Calls tools/list to discover available MCP tools
    3. Calls create_project, create_section, create_task in sequence
         │
         ▼
  Project appears in Todoist (all API calls routed through MCP)
```

### Validate Templates (CI)

Runs on every push to `main` and every pull request:

```
For each csv-templates/{slug}/:
  1. Slug must be kebab-case
  2. template.csv, meta.yml, README.md must all exist
  3. meta.yml must have: name, slug, description, category, tags, version
  4. meta.yml slug must match folder name
  5. meta.yml project_color (if present) must be a valid Todoist colour
  6. README.md must contain import instructions
  7. template.csv must start with TYPE header
  8. TYPE column values must be section or task only

For each prompt-templates/{slug}/:
  1–4. Same as above (plus inputs: key in meta.yml)
  5. prompt.md must contain at least one {{placeholder}}
```

### Bump Template Versions

Runs on every pull request targeting `main`:

- Detects which template directories have changed (excluding `meta.yml` changes)
- For each changed template, reads the current `version` in `meta.yml`
- Skips templates at `0.0.0` (unreviewed signal preserved)
- Increments the patch component (`x.y.z → x.y.(z+1)`) and commits back to the PR branch

### Documentation Sync

Runs daily (and on demand):

- Scans for changes to CSV templates, prompt templates, bundles, and scripts in the last 24 hours
- Compares changes against `index.md`, `CHANGELOG.md`, `README.md`, and template READMEs
- Generates updates using GitHub Copilot
- Opens (or updates) a pull request on the `doc-sync/automated-updates` branch

### Deploy Template Gallery

Runs on every push to `main` affecting templates or the gallery script:

- `generate_gallery.py` builds a static HTML site from all templates and prompt templates
- Deployed to GitHub Pages via `actions/deploy-pages`

### Sync Todoist Project List

Runs daily (and on demand):

- Fetches all project names from the Todoist API
- Rewrites the `parent_project` dropdown options in `create-todoist-project.yml`
- Commits the updated workflow file back to the repository

---

## Data Flow: Template to Todoist Project

```
csv-templates/weekly-review/
  ├── template.csv  ──┐
  └── meta.yml      ──┤
                      │
                      ▼
         create_todoist_project.py
                      │
         ┌────────────┼───────────────┐
         ▼            ▼               ▼
  POST /projects  POST /sections  POST /tasks
         │            │               │
         └────────────┴───────────────┘
                      │
                      ▼
          Todoist project with sections
          and tasks, ready to use
```

---

## Security

- The Todoist API token is stored as a **GitHub repository secret** (`TODOIST_API_TOKEN`) and is never exposed in logs or committed to the repository.
- All API calls are made over HTTPS to `https://api.todoist.com/api/v1`.
- The automation scripts use only Python standard library — no third-party pip packages means no supply-chain risk from Python dependencies.
- Dependabot monitors GitHub Actions dependencies, and Dependabot PRs are auto-reviewed and auto-merged (minor/patch/security) via GitHub Actions.
- Branch protection rules require pull request reviews before merging to `main`.

---

## Template Versioning

Versions follow [Semantic Versioning](https://semver.org/):

| Version | Meaning |
|---------|---------|
| `0.0.0` | Unreviewed — generated but not yet manually verified |
| `0.1.0` | Reviewed — manually verified and considered stable |
| `0.1.x` | Iterating — reviewed template receiving incremental improvements |

The `bump-template-versions` workflow automates patch increments on every PR for reviewed templates.
