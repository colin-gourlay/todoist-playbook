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
