# Todoist Playbook

![Social Preview](.github/assets/social-preview.png)

A curated collection of structured [Todoist](https://www.todoist.com/) templates, workflows, and tooling — designed to reduce friction, standardise recurring work, and get structured projects into Todoist in seconds.

**Who is this for?** Anyone who uses Todoist for personal productivity, team projects, or recurring workflows — and wants a repeatable, structured starting point rather than building task lists from scratch every time.

This repository is a system, not just a storage location:

- **CSV templates** → ready-made task structures for common projects and workflows
- **Bundles** → curated multi-template starter kits for larger goals
- **Automation** → GitHub Actions workflows that create Todoist projects with one click
- **AI prompt templates** → structured prompts for generating enriched task content
- **Documentation** → guides, changelogs, and a wiki

---

## ❓ Why This Exists

**The problem:** Every sprint, code review, job change, or house-admin cycle forces you to rebuild the same task structure from scratch. Best practices live in people's heads. Task managers give you containers but not content — you always start with a blank canvas, under time pressure, with gaps in what you remember.

**The solution:**

- **CSV templates** encode proven task structures and decision points, ready to import in seconds
- **Bundles** group related templates into starter kits for bigger life events
- **AI prompt templates** generate contextually enriched task content from a short description
- **GitHub Actions automation** creates fully structured Todoist projects with one click — no local downloads required
- Templates are plain-text CSV and YAML — version-controlled, portable, and not locked to any platform

---

## 🏗️ Architecture Overview

The Playbook is built in four layers:

| Layer | What it contains |
|-------|-----------------|
| **Content assets** | `csv-templates/`, `prompt-templates/`, `bundles/` — the plain-text source of truth |
| **Automation** | `.github/workflows/` — GitHub Actions for project creation, validation, sync, and publishing |
| **Execution** | `.github/scripts/` — Python entry points called by the workflows |
| **Discovery & publishing** | `index.md`, `wiki/`, `docs/` — catalogue, documentation, and the GitHub Pages gallery |

**Flow:** author a template → push to `main` → CI validates structure → workflows create Todoist projects on demand or on schedule → gallery auto-deploys to GitHub Pages.

For the full architecture diagram and component detail, see [wiki/Architecture.md](wiki/Architecture.md).

---

## ⚙️ Setup

**Minimum setup (for automation workflows):**

1. **Fork this repository** — [github.com/colin-gourlay/todoist-playbook](https://github.com/colin-gourlay/todoist-playbook)
2. **Add your Todoist API token** as a repository secret named `TODOIST_API_TOKEN`
   Retrieve it from [Todoist → Settings → Integrations → Developer](https://app.todoist.com/app/settings/integrations/developer)
3. **Enable GitHub Actions** in your fork (Actions tab → enable workflows if prompted)
4. **Run your first workflow** — Actions → Create Todoist Project from Template → Run workflow

**Optional extras:**

- **GitHub Pages gallery** — Settings → Pages → Source: GitHub Actions, then trigger the **Deploy Template Gallery** workflow
- **AI prompt templates** — require GitHub Copilot to be enabled on the repository (Team, Enterprise, or individual Copilot plan)
- **Parent project nesting** — run the **Sync Todoist Project List** workflow to populate the parent project dropdown

> For the full walkthrough and troubleshooting guide, see [wiki/Setup.md](wiki/Setup.md).

---

## 🧭 Start Here

Not sure where to begin? Pick the path that fits you:

| I want to… | Start here |
|---|---|
| **Import a template into Todoist** | [Browse the catalogue](index.md) → pick a template → download and import the CSV |
| **Create a Todoist project automatically** | Go to **Actions → Create Todoist Project from Template** → select a template → Run workflow |
| **Use AI to generate enriched task content** | Go to **Actions → Create Todoist Project from Prompt Template** → select a prompt → Run workflow |
| **Create a Todoist project via MCP** | Go to **Actions → Create Todoist Project via MCP** → select a template → Run workflow |
| **Contribute a new template** | Read [CONTRIBUTING](CONTRIBUTING) → follow the template structure → open a PR |

> **New to the repo?** Start with the [weekly-review](csv-templates/weekly-review/) template — it is the fastest way to see how the Playbook works.

---

## 🔍 Templates vs Bundles vs Prompt Templates

Not sure which type of asset to use? Here is a quick guide:

| Type | What it is | When to use it | Example |
|------|-----------|----------------|---------|
| **Template** | A single-purpose CSV task list with sections and tasks | You need a structured Todoist project for one specific workflow | [Weekly Review](csv-templates/weekly-review/) |
| **Bundle** | A curated set of templates for a broader scenario | You are starting something that spans multiple recurring workflows | [New Job Starter Kit](bundles/new-job/) |
| **Prompt Template** | An AI prompt you fill in and paste into an AI assistant | You want AI-generated, contextually enriched task content | [Task Enrichment](prompt-templates/task-enrichment/) |

---

## 🚀 How to Use

<a name="prerequisite"></a>

> **Prerequisite for automated workflows:** Add your Todoist API token as a repository secret named `TODOIST_API_TOKEN`.
> Retrieve your token from [Todoist Integrations Settings](https://app.todoist.com/app/settings/integrations/developer).

### ⚡ Automated (recommended)

Use the **Create Todoist Project from Template** GitHub Actions workflow to create a project directly from the latest hosted template — no local downloads required.

1. Go to **Actions → Create Todoist Project from Template**
2. Click **Run workflow**
3. Select a template from the dropdown
4. Optionally provide a custom project name
5. Click **Run workflow** — the project is created in Todoist automatically

![GitHub Actions Run Workflow form](.github/assets/screenshots/github-actions-run-workflow.svg)

### 🤖 Automated via AI Prompt Template

Use the **Create Todoist Project from Prompt Template** GitHub Actions workflow to generate enriched task content via GitHub Copilot and create a project automatically.

1. Go to **Actions → Create Todoist Project from Prompt Template**
2. Click **Run workflow**
3. Select a prompt template from the dropdown
4. Enter a **task title** (required) and optionally additional **context**
5. Optionally set a **priority** (`normal`, `medium`, `high`, or `urgent`) and a custom project name
6. Click **Run workflow** — Copilot generates the task content and the project is created in Todoist automatically

### 🌐 Via MCP (Todoist MCP server)

Use the **Create Todoist Project via MCP** workflow to route project creation through the Todoist MCP server.

> **Note:** This workflow supports a subset of templates. Leaving the template field blank defaults to `weekly-review`.

**Available templates:** `code-review`, `daily-review`, `ef-code-review`, `exam-certification-workflow`, `house-admin`, `iteration-0`, `onboarding-checklist`, `one-on-one`, `radio-show-system`, `saas-spin-up`, `saas-wind-down`, `socials-health-and-optimization-checklist`, `weekly-review`

1. Go to **Actions → Create Todoist Project via MCP**
2. Click **Run workflow**
3. Select a template (or leave blank for `weekly-review`)
4. Optionally provide a project name
5. Click **Run workflow**

### 📥 Manual

1. Browse the template catalogue in `index.md`
2. Navigate to a CSV template folder
3. Download `template.csv`
4. Import into Todoist:
   - Open Todoist
   - Create new project
   - Use "Import from CSV"

Each template folder includes:

- `template.csv` → importable file
- `meta.yml` → machine-readable metadata
- `README.md` → explanation & usage guidance

### 🤖 AI Prompt Templates

Use AI prompt templates to generate rich, structured task content before adding items to Todoist.

1. Browse the prompt template catalogue in `index.md`
2. Navigate to a `prompt-templates/` folder
3. Open `prompt.md` and fill in the `{{placeholders}}`
4. Paste the prompt into your AI assistant (ChatGPT, GitHub Copilot, Claude, Gemini, etc.)
5. Copy the output into the Todoist task name and description fields

Each prompt template folder includes:

- `prompt.md` → the prompt with input placeholders and expected output schema
- `meta.yml` → machine-readable metadata
- `README.md` → usage guidance and examples

---


## 💡 Usage Examples

### Example 1 — Automated: Weekly Review in 30 seconds

> **Scenario:** It's Sunday evening and you want a fresh Weekly Review project in Todoist without downloading anything.

1. Go to **Actions → Create Todoist Project from Template**
2. Click **Run workflow**
3. Select `weekly-review` from the **Template** dropdown
4. Leave **Project name** blank (defaults to `Weekly Review`)
5. Click **Run workflow**

The Actions log confirms each section and task as it is created:

```
📋 Template : weekly-review
📁 Project  : Weekly Review

  📂 1️⃣ Capture & Clarify
  ✓ Process inbox to zero
  ✓ Review flagged emails
  ✓ Review pending decisions

  📂 2️⃣ Review & Reflect
  ✓ Review last week's completed tasks
  ✓ Assess progress against goals

🎉 Done! Project 'Weekly Review' is ready in Todoist.
```

![GitHub Actions log output](.github/assets/screenshots/github-actions-log-output.svg)

The project appears in Todoist immediately, with all sections and priority flags already applied — ready to work through.

![Todoist project result — Weekly Review](.github/assets/screenshots/todoist-project-result.svg)

---

### Example 2 — Manual: Onboarding Checklist for a new job

> **Scenario:** You are starting a new role and want a 90-day onboarding plan in Todoist, imported from your own fork of the repository.

1. Navigate to [`csv-templates/onboarding-checklist/`](csv-templates/onboarding-checklist/)
2. Download `template.csv` (click the file, then **Raw**, then save)
3. Open [Todoist](https://app.todoist.com) and create a new project named `Onboarding – [Company Name]`
4. Open the project → click **⋯ More actions** → **Import from CSV**
5. Select the downloaded `template.csv`

Todoist imports all five sections (Day 1, Week 1, Weeks 2–4, Month 1–3, Ongoing) with tasks nested under each. Work through them in order, adapting tasks to your specific role and organisation.

> **Tip:** Read the template [`README.md`](csv-templates/onboarding-checklist/README.md) before importing — it explains what each section covers and suggests how to customise it.

---

## 🖼 Screenshots

Screenshots are embedded inline throughout this document alongside the relevant workflow steps. For a complete visual walkthrough — including the validation CI run, template catalogue structure, and version bump behaviour — see the [Screenshots wiki page](wiki/Screenshots.md).

---

## 📂 Structure

- `/csv-templates` → Individual reusable CSV templates
- `/prompt-templates` → AI prompt templates for generating enriched Todoist task content
- `/bundles` → Multi-template starter kits
- `/.github/scripts` → Automation scripts for creating Todoist projects and generating release assets
- `/wiki` → Project wiki (problem statement, architecture, setup, roadmap, screenshots)

### Migration note

The repository previously used `/templates` for CSV template folders. This has been renamed to `/csv-templates` to clearly distinguish CSV templates from prompt templates.

If you consume repository paths directly, update any references from:

- `templates/{slug}/...` → `csv-templates/{slug}/...`

If you consume release assets, the ZIP filename is now:

- `dist/templates.zip` → `dist/csv-templates.zip`

---

## 🧠 Philosophy

Templates are not just task lists.
They encode decisions, structure, and thinking patterns.

The goal of this repository is to:

- Reduce friction when starting projects
- Standardise recurring workflows
- Externalise mental overhead
- Improve consistency

---

## 📈 GitHub Trending to Todoist

The **GitHub Trending to Todoist** workflow runs daily at 05:30 UTC. It fetches the repositories currently trending on GitHub (today, this week, and this month) and pushes them into a dated Todoist project as `read-later` tasks, grouped by period.

### What it does

- Creates a Todoist project using either a generated dated name such as `github-trending-YYYY-MM-DD`, a generated language-specific variant such as `github-trending-python-YYYY-MM-DD`, or a custom name you supply
- Adds one task per trending repository, with the repo slug and available metrics in the task title
- Stores the repository description and source URL in the task description
- Groups tasks into three sections: **Trending (Today)**, **Trending (This Week)**, **Trending (This Month)**
- Optionally filters by one or more programming languages (e.g. `Python` or `Python,TypeScript`)
- Applies a `read-later` label to every task for easy filtering in Todoist
- Adds a kebab-case language label when GitHub exposes a primary language for the repository
- Persists imported repository slugs in `.github/data/github-trending-processed-slugs.json` so a repository is imported only once, even if the original Todoist task is later edited or deleted
- Also skips repositories that are already present as active or completed `read-later` tasks in Todoist
- Automatically triggers the **Create Todoist Project from Template** workflow after a successful run, creating a fresh **GitHub Trending Tracker Daily** review project alongside the trending tasks

### How to trigger manually

1. Go to **Actions → GitHub Trending to Todoist**
2. Click **Run workflow**
3. Optionally enter a custom project name or language filter
4. Click **Run workflow** — the project appears in Todoist immediately

> **Prerequisite:** The `TODOIST_API_TOKEN` repository secret must be set.

---

## 🤖 Automated Documentation Sync

The **Documentation Sync** workflow runs daily to keep this repository's documentation
accurate and up to date. It is compiled from
`.github/workflows/doc-sync.md` into `.github/workflows/doc-sync.lock.yml`,
which is the executable workflow file checked by GitHub Actions.

### What it does

On each run, the workflow:

1. Scans for changes made in the last 24 hours to CSV templates, prompt templates, bundles,
   and scripts.
2. Compares those changes against the relevant documentation files (`index.md`,
   `CHANGELOG.md`, `README.md`, and individual template `README.md` files).
3. Generates any necessary documentation updates using GitHub Copilot.
4. Opens a pull request (branch: `doc-sync/automated-updates`) with the changes —
   or exits silently if everything is already up to date.

The workflow is idempotent: if an open documentation-sync PR already exists on that branch,
subsequent runs will update it rather than open a duplicate.

### How to trigger manually

1. Go to **Actions → Documentation Sync**
2. Click **Run workflow**
3. Click **Run workflow** again to confirm

---

## 🔢 Template Versioning

Each template carries a `version` field in its `meta.yml` that follows [Semantic Versioning](https://semver.org/).

| Version | Meaning |
|---------|---------|
| `0.0.0` | **Unreviewed** — generated but not yet manually checked. Do not rely on it for production use. |
| `0.1.0` | **Reviewed** — manually verified and considered stable. |
| `0.1.x` | **Iterating** — reviewed template receiving incremental improvements. |

### Review queue in GitHub Issues

The **Sync Template Review Issues** workflow keeps GitHub issues aligned with unreviewed templates:

- For each template at `version: 0.0.0`, it ensures one open issue labelled `to-be-reviewed`.
- If a template moves away from `0.0.0`, the matching review issue is closed automatically.
- Issues are assigned to `colin-gourlay` by default.

Run the workflow manually from **Actions → Sync Template Review Issues** to backfill or re-sync state.

### Workflow

1. **All new templates start at `0.0.0`** to signal they have not been reviewed.
2. **After a manual review**, bump the template to `0.1.0` by editing its `meta.yml` directly.
3. **Any subsequent change** to a reviewed template (i.e. version ≥ `0.1.0`) automatically receives a **patch bump** (`x.y.z → x.y.(z+1)`) when the PR is merged.

### Auto-bump behaviour

The **Bump template versions** workflow runs on every pull request targeting `main`:

- It detects which template directories have changed (based on non-`meta.yml` file changes).
- For each changed template it reads the current `version` in `meta.yml`.
- If the version is `0.0.0` it is left untouched (preserving the "unreviewed" signal).
- Otherwise it increments the **patch** component and commits the change back to the PR branch.
- The workflow is idempotent: re-running it on a PR that has already been bumped will not produce an additional bump.

---

## 🗺️ Roadmap

**Current state:**

- ✅ 30+ curated templates across productivity, engineering, media, and personal domains
- ✅ Starter-kit bundles for common life scenarios
- ✅ GitHub Actions workflows for one-click project creation (standard, AI-powered, and MCP-based)
- ✅ Automated CI validation, template version bumping, documentation sync, and gallery deployment

**Near-term priorities:**

- [ ] Bump all unreviewed templates (`0.0.0`) to `0.1.0` after manual review
- [ ] Additional engineering templates: incident response, post-mortem, architecture decision record
- [ ] Scheduled workflow to auto-create `daily-review` project each morning
- [ ] Template preview in the GitHub Pages gallery (rendered task tree view)

→ See the full [Roadmap wiki page](wiki/Roadmap.md) for near-term, medium-term, and longer-term plans.

---

## 🔁 Reusable Workflows

The validation, gallery deployment, and release workflows in this repository can be consumed from external repositories. Pin to a release tag (e.g. `@v2026.3.22`) for a stable reference.

→ See [.github/REUSABLE_WORKFLOWS.md](.github/REUSABLE_WORKFLOWS.md) for available workflows, inputs, and usage examples.

---

## 📜 License

[Creative Commons Attribution-ShareAlike 4.0 International](LICENSE)
