# Problem Statement

## The Problem

Every time you start a new project — whether it is a sprint, a job change, a code review, or a quarterly house-admin cycle — you face the same invisible tax: rebuilding the same task structure from memory.

This overhead is small per instance but accumulates into thousands of minutes of lost focus every year. It also introduces inconsistency: the checklist you build under pressure is not as thorough as the one you would build with time to think.

Specifically:

- **Recurring projects are rebuilt from scratch.** Weekly reviews, sprint retrospectives, and onboarding checklists are recreated each time, often missing steps.
- **Tribal knowledge stays in people's heads.** The "right way" to do a code review or spin up a SaaS tool is undocumented and lost between team members.
- **Task management tools are blank canvases.** Todoist, Asana, and others give you the container but not the content. You always start with an empty project.
- **Automation is disconnected.** Even if you have a template, you still have to manually import it, rename sections, and tweak priorities.

---

## The Solution

The **Todoist Playbook** is a curated library of structured task templates with first-class automation baked in.

It provides:

1. **Pre-built templates** for common recurring projects — from daily reviews to Azure migration assessments.
2. **A one-click GitHub Actions workflow** that creates a fully structured Todoist project from any template in under a minute.
3. **AI prompt templates** that use GitHub Copilot or any LLM to enrich task descriptions with context-aware content.
4. **Starter-kit bundles** that group related templates for common life scenarios (starting a new job, producing a weekly radio show, running annual house admin).
5. **Documentation automation** that keeps the catalogue and changelog accurate and up to date without manual effort.

---

## Who Is It For?

| Persona | How they use it |
|---------|----------------|
| **Individual contributors** | Start personal and professional projects without rebuilding task structures each time |
| **Engineering teams** | Standardise sprint ceremonies, code reviews, and onboarding checklists |
| **Solo founders / freelancers** | Manage recurring client and business workflows with repeatable structure |
| **Content creators** | Run a consistent production pipeline for podcasts, radio shows, or YouTube channels |
| **Power Todoist users** | Explore and adapt high-quality templates for their own workflows |

---

## Design Principles

The Playbook is built on a few key principles:

- **Templates encode decisions, not just tasks.** A well-authored template captures the thinking behind a workflow, not just a list of things to do.
- **Automation removes the last mile of friction.** Even a CSV import is one step too many. The GitHub Actions workflow removes it entirely.
- **Everything is plain text and version-controlled.** Templates are stored as CSV and YAML — easy to diff, review, fork, and contribute to.
- **Structure is optional at the margins.** The tooling validates the minimum necessary structure and stays out of the way for everything else.
- **No vendor lock-in beyond Todoist.** The templates are importable manually. The automation layer is a convenience, not a requirement.
