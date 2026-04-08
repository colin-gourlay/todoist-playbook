# GitHub Trending Tracker

A review template for discovering, evaluating, and acting on trending GitHub repositories. Use it as a manual weekly review project, or as the companion review project that is automatically created after the GitHub Trending sync workflow runs successfully.

---

## Objective

- Review trending repositories relevant to your focus areas each week
- Evaluate candidates systematically using clear, repeatable criteria
- Organise your GitHub Stars as a curated, actionable knowledge library
- Reverse engineer high-signal repos to extract patterns worth applying
- Convert external ecosystem signals into concrete follow-up tasks and backlog work
- Close the loop between repository discovery and deliberate action in Todoist

Estimated duration: 45 minutes.

---

## When to Use

- As a weekly recurring ritual to stay current with the GitHub ecosystem
- After the `Sync GitHub Trending to Todoist` workflow creates a fresh trending project in Todoist
- Before planning a new project or feature to validate demand and direction
- When your starred repos feel noisy or misaligned with current priorities
- Whenever you want to improve the discoverability or reach of your own repos

---

## Structure Overview

1. Evaluate Trending Repos
2. Organise Your Stars as a Knowledge System
3. Reverse Engineer High-Signal Repos
4. Extract Insights and Convert to Actions
5. Track Star Velocity and Momentum
6. Close the Review

---

## How This Fits the Repository

This template now sits alongside two automation workflows:

1. `Sync GitHub Trending to Todoist` creates a separate Todoist project containing trending repositories grouped into **Trending (Today)**, **Trending (This Week)**, and **Trending (This Month)**.
2. `Create Todoist Project from Template` is triggered after a successful trending sync run and creates this **GitHub Trending Tracker** project from `template.csv`.

In practice, the automation gathers the raw repository inputs and this template provides the structured review checklist you use to process them.

---

## The 5-Second Test

When evaluating any repo, ask: **can you immediately understand its value from the README?**

People star repositories when four conditions align:

> **Clear Value + Fast Understanding + Low Effort + Trust = ⭐**

Use this as your primary filter when scanning trending repos.

---

## Repo Action States

For each candidate, assign one of these action states:

| Action | Meaning |
| ------ | ------- |
| **Star** | Useful now or likely useful soon — add to a Stars list |
| **Watch** | High signal but no immediate use — monitor for releases and changes |
| **Reference Only** | Worth knowing about, no active tracking needed |
| **Ignore** | Not relevant — log the reason briefly to avoid revisiting |

---

## Star Velocity Signals

Trending is driven by how fast stars accumulate, not just total count. Track what triggers bursts:

- A README overhaul
- A LinkedIn or Reddit post
- Being featured on a newsletter or trending list
- A new release or major feature drop

Apply this awareness to your own repos: track when your stars increase and correlate it to what changed.

---

## Review Outputs

Each weekly cycle should produce at least three practical outputs:

1. An updated Stars list with clearly classified repos
2. One extracted pattern or insight from a high-star repo
3. One concrete follow-up task for your own backlog

If you are using the automation path, the review inputs come from the separate trending-import project. That project contains one task per repository, labelled `read-later`, with the repository URL and summary in the task description.

---

## Related Resources

- [GitHub Trending](https://github.com/trending)
- [GitHub Stars](https://github.com/stars)
- Automation workflow: [Sync GitHub Trending to Todoist](../../.github/workflows/sync-github-trending-to-todoist.yml)
- Companion workflow: [Create Todoist Project from Template](../../.github/workflows/create-todoist-project.yml)
- Companion template: [Repo Ecosystem Watch](../repo-ecosystem-watch/)
- Companion template: [Repo Profile Audit](../repo-profile-audit/)
- Companion template: [GitHub Repo Spin-Up](../github-repo-spin-up/)

---

## Import Instructions

### Manual CSV import

1. Download `template.csv`
2. Create a new project in Todoist
3. Import from CSV
4. Rename the project to: `GitHub Trending Tracker – [Week of Month Year]`
5. Set this project to recur weekly

### Automated workflow path

1. Add the `TODOIST_API_TOKEN` repository secret
2. Run `Sync GitHub Trending to Todoist` manually, or wait for its daily schedule
3. After the sync succeeds on `main`, the `Create Todoist Project from Template` workflow creates this review project automatically using the `github-trending-tracker` CSV template
