# Screenshots

This page provides a visual walkthrough of the key workflows and components in the Todoist Playbook.

---

## Social Preview

![Todoist Playbook social preview](../.github/assets/social-preview.png)

---

## GitHub Actions — Create Todoist Project from Template

The primary entry point for the automated workflow. Navigate to **Actions → Create Todoist Project from Template → Run workflow** to see the input form.

### Workflow inputs

The `workflow_dispatch` form presents the following inputs:

```
Template:        [ weekly-review ▾ ]
Project name:    [ Leave blank for default           ]
Colour:          [ (none) ▾                          ]
Mark as favourite: [ no ▾ ]
Parent project:  [ (none — top-level project) ▾      ]

                              [ Run workflow ]
```

After clicking **Run workflow**, the Actions log shows the creation progress:

```
📋 Template : weekly-review
📁 Project  : Weekly Review

  📂 1️⃣ Capture & Clarify
  ✓ Process inbox to zero
  ✓ Review flagged emails
  ...

  📂 2️⃣ Review & Reflect
  ✓ Review last week's completed tasks
  ...

🎉 Done! Project 'Weekly Review' is ready in Todoist.
```

---

## GitHub Actions — Template Validation (CI)

Every push to `main` and every pull request triggers the **Validate templates** workflow. A passing run looks like:

```
🔎 Checking awesome-list-submission
🔎 Checking azure-migration-assessment
🔎 Checking code-review
🔎 Checking code-review-checklist
...
✅ All templates validated successfully
✅ All prompt templates validated successfully
```

A failing run produces targeted error messages:

```
🔎 Checking my-new-template
❌ meta.yml missing key: description: in templates/my-new-template/
❌ README.md does not contain import instructions in templates/my-new-template/
💥 Validation failed
```

---

## Template Catalogue (`index.md`)

The `index.md` file is the human-readable catalogue of all available templates, organised by category:

```markdown
## 🔁 Daily & Weekly Systems

| Template     | Description                                              | Tags                              |
|-------------|----------------------------------------------------------|-----------------------------------|
| Daily Review | GTD-aligned daily review to capture, clarify, close out  | review, planning, productivity... |
| Weekly Review| Structured weekly reset to close loops and plan ahead    | review, planning, productivity... |

## 💻 Work Projects

| Template               | Description                                        | Tags                       |
|------------------------|----------------------------------------------------|----------------------------|
| Code Review Checklist  | Thorough code review checklist for any language    | code-review, quality...    |
| Iteration 0            | Sprint 0 checklist for new project setup           | sprint, azure-devops...    |
```

---

## Template Gallery (GitHub Pages)

The **Deploy Template Gallery** workflow builds a searchable static HTML gallery from all templates and deploys it to GitHub Pages. The gallery presents each template with:

- Name and description
- Category and tags
- A link to the template folder

---

## Template Folder Structure

Each template lives in a `templates/{slug}/` folder:

```
templates/weekly-review/
├── template.csv     ← importable task list
├── meta.yml         ← machine-readable metadata
└── README.md        ← explanation and usage guide
```

### Example `meta.yml`

```yaml
name: Weekly Review
slug: weekly-review
description: Structured weekly reset to close loops and plan the week ahead
category: productivity
tags:
  - review
  - planning
  - productivity
  - weekly
version: 0.1.0
project_color: blue
```

### Example `template.csv` (first few rows)

```
TYPE,CONTENT,PRIORITY,INDENT,AUTHOR,RESPONSIBLE,DUE_DATE,DUE_DATE_LANG
section,1️⃣ Capture & Clarify,,,,,,
task,Process inbox to zero,1,1,,,,,
task,Review flagged emails,2,1,,,,,
section,2️⃣ Review & Reflect,,,,,,
task,Review last week's completed tasks,2,1,,,,,
```

---

## Bump Template Versions

When a pull request modifies a reviewed template (version ≥ `0.1.0`), the **Bump template versions** workflow automatically increments the patch version and commits back to the PR branch:

```
Detected changes in: templates/weekly-review
Current version: 0.1.4
Bumped to: 0.1.5
Committed version bump for weekly-review
```

---

## Documentation Sync

The **Documentation Sync** workflow runs daily. When it detects that `index.md` or a template README is out of date with recent changes, it opens a pull request automatically:

```
Branch:  doc-sync/automated-updates
Title:   docs: automated documentation sync
Changes:
  - index.md      (updated catalogue entry)
  - CHANGELOG.md  (added unreleased entry)
```
