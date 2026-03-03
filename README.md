# Todoist Playbook

A curated collection of structured [Todoist](https://www.todoist.com/) templates, workflows, and tooling.

This repository is not just a storage location - it is a system for:

- Reusable project templates
- Workflow patterns
- Bundled starter kits
- Automation tooling
- Documentation & playbooks

---

## 🚀 How to Use

### ⚡ Automated (recommended)

Use the **Create Todoist Project from Template** GitHub Actions workflow to create a project directly from the latest hosted template — no local downloads required.

1. Go to **Actions → Create Todoist Project from Template**
2. Click **Run workflow**
3. Select a template from the dropdown
4. Optionally provide a custom project name
5. Click **Run workflow** — the project is created in Todoist automatically

> **Prerequisite:** Add your Todoist API token as a repository secret named `TODOIST_API_TOKEN`.
> Retrieve your token from [Todoist Integrations Settings](https://app.todoist.com/app/settings/integrations/developer).

### 📥 Manual

1. Browse the template catalog in `INDEX.md`
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

---

## 📂 Structure

- `/templates` → Individual reusable templates
- `/bundles` → Multi-template starter kits
- `/cli` → Automation tooling
- `/docs` → GitHub Pages site

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

## 📜 License

[Creative Commons Attribution-ShareAlike 4.0 International](LICENSE)
