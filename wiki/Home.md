# Todoist Playbook — Wiki

Welcome to the **Todoist Playbook** project wiki. This is the central reference for understanding what the project is, how it works, and how to get the most out of it.

---

## 📖 Contents

| Page | What you will find |
|------|--------------------|
| [Problem Statement](Problem-Statement) | Why this project exists and the problem it solves |
| [Architecture](Architecture) | How the repository hangs together technically |
| [Setup](Setup) | How to configure the project and start using it |
| [Screenshots](Screenshots) | Visual walkthroughs of the key workflows |
| [Roadmap](Roadmap) | Where the project is headed |

---

## 🚀 Quick Start

1. Add your Todoist API token as a repository secret named `TODOIST_API_TOKEN`
2. Go to **Actions → Create Todoist Project from Template**
3. Select a template and click **Run workflow**
4. The project appears in Todoist immediately

That is all it takes to turn a structured task template into a live Todoist project.

---

## 🗂 What Is the Todoist Playbook?

The Todoist Playbook is a curated library of structured task templates, automation workflows, and AI prompt templates that make it easy to start any recurring project in [Todoist](https://www.todoist.com/) in seconds.

Instead of rebuilding the same project structure from scratch each time you start a sprint, begin a new job, or kick off a house-admin cycle, the Playbook gives you a ready-made, proven skeleton — and a one-click GitHub Actions workflow to create it directly in your Todoist account.

---

## 🧠 Core Concepts

| Concept | Description |
|---------|-------------|
| **Template** | A folder containing a `template.csv`, `meta.yml`, and `README.md` |
| **Bundle** | A curated set of templates grouped for a common scenario (e.g. starting a new job) |
| **Prompt Template** | An AI prompt you fill in and paste into an AI assistant to enrich task content |
| **Workflow** | A GitHub Actions pipeline that creates a Todoist project or syncs documentation |

---

## 📜 Licence

[Creative Commons Attribution-ShareAlike 4.0 International](../LICENSE)
