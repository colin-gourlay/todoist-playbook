# Awesome List Outreach Shortlist

A focused outreach playbook for getting this repository listed on curated Awesome Lists — built on top of the generic [Awesome List Submission](../awesome-list-submission/) workflow, with a pre-qualified shortlist, reusable submission message, and a lightweight tracking table.

---

## Objective

- Work from a curated shortlist of high-fit Awesome Lists rather than starting from scratch
- Verify each list's quality signals before committing to a submission
- Apply a consistent, reusable submission message that can be adapted per list
- Track submission status and follow up systematically

---

## When to Use

- When preparing to submit this repository to Awesome Lists for the first time
- After a significant improvement to the README, structure, or content
- As part of a periodic discoverability review (run the full [Awesome List Submission](../awesome-list-submission/) template first if this is your first time)

---

## Structure Overview

1. Review the Pre-Qualified Shortlist
2. Draft Your Submission Message
3. Submit to Each Shortlisted List
4. Track & Follow Up

---

## Pre-Qualified Shortlist

The table below is a starting point. Verify each list is still active and accepting submissions before opening a PR.

| # | Repository | Focus | Stars (at time of writing) | Rationale |
|---|-----------|-------|---------------------------|-----------|
| 1 | [jyguyomarch/awesome-productivity](https://github.com/jyguyomarch/awesome-productivity) | General productivity tools and resources | ~2.4k | Todoist Playbook is a productivity workflow system — a direct fit for this list's scope |
| 2 | [nicedoc/awesome-productivity-apps](https://github.com/nicedoc/awesome-productivity-apps) | Productivity applications | ~500 | Template-based Todoist workflows sit naturally alongside other productivity tools |
| 3 | [merq/awesome-gtd](https://github.com/merq/awesome-gtd) | Getting Things Done resources | ~300 | Weekly review and daily review templates align closely with GTD methodology |
| 4 | [dend/awesome-personal-branding](https://github.com/dend/awesome-personal-branding) | Personal branding and online presence | ~400 | Brand & Social templates (socials audit, awesome list submission) are directly relevant |
| 5 | [bayandin/awesome-awesomeness](https://github.com/bayandin/awesome-awesomeness) | Meta-list cataloguing all awesome lists | ~18k | As the repo grows, it could qualify as an awesome list in its own right |
| 6 | [sindresorhus/awesome](https://github.com/sindresorhus/awesome) | Canonical meta-list of all awesome lists | ~350k | Aspirational; requires the repo to first become a standalone awesome list |

> **Before submitting:** check the last commit date, open issues, and CONTRIBUTING.md for each list. Lists that have not been updated in over 12 months or whose PRs go unreviewed are lower priority.

---

## Quality Signal Checklist

Before submitting to any list, confirm the following for this repository:

- [ ] README has a clear title, one-line description, and Quick Start section
- [ ] The repo description in the GitHub About panel is accurate and keyword-rich
- [ ] Relevant topics are set on the repo (e.g. `todoist`, `productivity`, `gtd`, `workflow`)
- [ ] A LICENSE file is present
- [ ] The most recent commit is within the last 90 days
- [ ] The repo has a social preview image set

And for each target list:

- [ ] The list's CONTRIBUTING.md has been read in full
- [ ] The repo meets any minimum star-count requirement
- [ ] The entry format matches the list's existing style

---

## Submission Message Template

### Entry format (for the list README)

```
- [Todoist Playbook](https://github.com/colin-gourlay/todoist-playbook) – A curated collection of structured Todoist templates and automation workflows for productivity, career management, agile ceremonies, and more.
```

Adjust the description to match the tone and focus of each specific list.

### PR description template

```
## What this adds

[Todoist Playbook](https://github.com/colin-gourlay/todoist-playbook) is a curated collection of structured Todoist templates and GitHub Actions automation for productivity-focused workflows.

It includes templates for:
- Daily and weekly reviews (GTD-aligned)
- Career and meeting management (onboarding, 1:1s)
- Agile sprint ceremonies (retrospectives, reviews)
- SaaS and project management workflows
- Brand, social, and open-source outreach

## Why it belongs here

The repository solves a real, recurring problem — building and maintaining a consistent personal productivity system — and presents it in a structured, importable format.

## Quality signals

- Actively maintained (regular commits)
- Clear README with Quick Start, objectives, and import instructions
- MIT-compatible license (CC0)
- Organised folder structure with per-template metadata

I've read your CONTRIBUTING.md and believe this entry meets your submission criteria. Happy to adjust the description or placement based on your feedback.
```

### Follow-up note (for PRs open 14+ days with no response)

```
Hi, just a friendly follow-up on this PR. Happy to adjust the entry description or placement if that would help it fit better. No rush — I appreciate your time maintaining this list.
```

---

## Submission Tracking Table

Copy this table into a comment on your outreach tracking issue or a private note, and update it as submissions progress.

| List | PR URL | Date Submitted | Status | Notes |
|------|--------|---------------|--------|-------|
| jyguyomarch/awesome-productivity | — | — | Not started | — |
| nicedoc/awesome-productivity-apps | — | — | Not started | — |
| merq/awesome-gtd | — | — | Not started | — |
| dend/awesome-personal-branding | — | — | Not started | — |
| bayandin/awesome-awesomeness | — | — | Not started | — |
| sindresorhus/awesome | — | — | Not started | Aspirational — revisit when repo has 500+ stars |

**Status values:** `Not started` → `Submitted` → `Under review` → `Merged` / `Rejected`

---

## Import Instructions

1. Download `template.csv`
2. Create a new project in Todoist
3. Import from CSV
4. Rename the project to: `Awesome List Outreach – [Repo Name]`
5. Work through Section 1 first — do not submit until you have verified each list is active and accepting PRs
