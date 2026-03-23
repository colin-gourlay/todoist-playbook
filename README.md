# Todoist Playbook

![Social Preview](.github/assets/social-preview.png)

A curated collection of structured [Todoist](https://www.todoist.com/) templates, workflows, and tooling.

This repository is not just a storage location - it is a system for:

- Reusable project templates
- Workflow patterns
- Bundled starter kits
- Automation tooling
- Documentation & playbooks

---

## 🚀 How to Use

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
2. Navigate to a template folder
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
| Set up a structured project for a single recurring workflow | **[Template](templates/)** | [Weekly Review](templates/weekly-review/) — a GTD-style end-of-week reset with sections for capture, review, and planning |
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

1. Navigate to [`templates/onboarding-checklist/`](templates/onboarding-checklist/)
2. Download `template.csv` (click the file, then **Raw**, then save)
3. Open [Todoist](https://app.todoist.com) and create a new project named `Onboarding – [Company Name]`
4. Open the project → click **⋯ More actions** → **Import from CSV**
5. Select the downloaded `template.csv`

Todoist imports all five sections (Day 1, Week 1, Weeks 2–4, Month 1–3, Ongoing) with tasks nested under each. Work through them in order, adapting tasks to your specific role and organisation.

> **Tip:** Read the template [`README.md`](templates/onboarding-checklist/README.md) before importing — it explains what each section covers and suggests how to customise it.

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

- `/templates` → Individual reusable templates
- `/prompt-templates` → AI prompt templates for generating enriched Todoist task content
- `/bundles` → Multi-template starter kits
- `/cli` → Automation tooling
- `/docs` → GitHub Pages site
- `/wiki` → Project wiki (problem statement, architecture, setup, roadmap, screenshots)

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

## 🤖 Automated Documentation Sync

The **Documentation Sync** workflow runs daily to keep this repository's documentation
accurate and up to date.

### What it does

On each run, the workflow:

1. Scans for changes made in the last 24 hours to templates, prompt templates, bundles,
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
