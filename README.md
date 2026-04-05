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

## 🧭 Start Here

Not sure where to begin? Pick the path that fits you:

| I want to… | Start here |
|---|---|
| **Import a template into Todoist** | [Browse the catalogue](index.md) → pick a template → download and import the CSV |
| **Create a Todoist project automatically** | Go to **Actions → Create Todoist Project from Template** → select a template → Run workflow |
| **Use AI to generate enriched task content** | Go to **Actions → Create Todoist Project from Prompt Template** → select a prompt → Run workflow |
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

### 🤖 Automated via AI Prompt Template

Use the **Create Todoist Project from Prompt Template** GitHub Actions workflow to generate enriched task content via GitHub Copilot and create a project automatically.

1. Go to **Actions → Create Todoist Project from Prompt Template**
2. Click **Run workflow**
3. Select a prompt template from the dropdown
4. Enter a task title and optional context
5. Optionally select a priority and provide a custom project name
6. Click **Run workflow** — Copilot generates the task content and the project is created in Todoist automatically

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

## 🧭 Which type should I use?

| I want to… | Use this | Example |
|------------|----------|---------|
| Set up a structured project for a single recurring workflow | **[Template](csv-templates/)** | [Weekly Review](csv-templates/weekly-review/) — a GTD-style end-of-week reset with sections for capture, review, and planning |
| Hit the ground running on a big life event or scenario | **[Bundle](bundles/)** | [New Job](bundles/new-job/) — combines the Onboarding Checklist, Weekly Review, and One-on-One templates in one starter kit |
| Generate rich, AI-powered task content tailored to my input | **[Prompt Template](prompt-templates/)** | [Task Enrichment](prompt-templates/task-enrichment/) — paste a short description into your AI assistant and get a fully structured task back |

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

The project appears in Todoist immediately, with all sections and priority flags already applied — ready to work through.

See the [Screenshots wiki page](wiki/Screenshots.md) for a visual walkthrough of this workflow.

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

Visual walkthroughs of the key workflows are available in the [Screenshots wiki page](wiki/Screenshots.md):

| Screenshot | Description |
|-----------|-------------|
| [Run workflow form](wiki/Screenshots.md#workflow-inputs) | GitHub Actions input form for creating a project from a template |
| [Actions log output](wiki/Screenshots.md#actions-log-output) | Live creation progress shown in the Actions log |
| [Todoist project result](wiki/Screenshots.md#todoist--project-result) | The resulting project in Todoist with sections and tasks pre-populated |

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

The **GitHub Trending to Todoist** workflow runs daily at 08:00 UTC. It fetches the repositories currently trending on GitHub (today, this week, and this month) and pushes them into a dated Todoist project as `read-later` tasks, grouped by period.

### What it does

- Creates a Todoist project named `github-trending-YYYY-MM-DD` (or a custom name you supply)
- Adds one task per trending repository, with stars, forks, star velocity, and language in the task description
- Groups tasks into three sections: **Trending (Today)**, **Trending (This Week)**, **Trending (This Month)**
- Optionally filters by one or more programming languages (e.g. `Python` or `Python,TypeScript`)
- Applies a `read-later` label to every task for easy filtering in Todoist
- Skips repositories that are already present as active or completed `read-later` tasks in Todoist, preventing duplicates across runs
- Automatically triggers the **Create Todoist Project from Template** workflow after a successful run, creating a fresh **GitHub Trending Tracker** review project alongside the trending tasks

### How to trigger manually

1. Go to **Actions → GitHub Trending to Todoist**
2. Click **Run workflow**
3. Optionally enter a custom project name or language filter
4. Click **Run workflow** — the project appears in Todoist immediately

> **Prerequisite:** The `TODOIST_API_TOKEN` repository secret must be set.

---

## 🤖 Automated Documentation Sync

The **Documentation Sync** workflow runs daily to keep this repository's documentation
accurate and up to date.

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

## 📜 License

[Creative Commons Attribution-ShareAlike 4.0 International](LICENSE)
