# Weekly Review

A combined single-session weekly reset for people who prefer one review block.

This template is now a fallback option. The recommended workflow is the two-part system:

- [Weekly Close](../weekly-close/) for Friday closure
- [Weekly Plan](../weekly-plan/) for Sunday planning

---

## Objective

- Close open loops
- Reset commitments
- Identify priorities
- Enter the new week with clarity

Estimated duration: 30–45 minutes.

---

## When to Use

- Once per week in a single uninterrupted session
- Friday afternoon if you prefer a close-first rhythm
- Sunday evening if you prefer a plan-first rhythm

---

## Structure Overview

1. Close the Past
2. Clear the Present
3. Review Commitments
4. Plan the Future
5. Performance Review & Alignment
6. Stop / Start / Continue

---

## Recommendation

If you run review automation from GitHub Actions, use the split templates for clearer intent and lower cognitive load:

- Friday schedule creates [Weekly Close](../weekly-close/)
- Sunday schedule creates [Weekly Plan](../weekly-plan/)

Use this combined template when you only want one weekly project to import or run.

---

## Suggested Ritual

- Block 45 minutes in calendar
- Silence notifications
- Complete sections in order
- Do not skip steps

---

## Labels Suggested

All tasks in this template are pre-tagged with the following labels:

| Label | Meaning |
| ----- | ------- |
| `@people-self` | Task is self-directed — no delegation required |
| `@place-anywhere` | Can be completed from any location (home, café, commute, etc.) |
| `@tools-todoist` | Todoist itself is the primary tool for completing this task |
| `@when-evening` | Best suited to late afternoon or evening time blocks |
| `@duration-5m` | Brief review step — used for the Close the Past section |
| `@duration-25m` | Standard review step — used for the majority of the checklist |

> **Note on `@place-anywhere`**: This label was recently added to signal that the weekly review is location-independent. Unlike deep work tasks that may require a specific environment, every step of this review can be completed wherever you have access to Todoist.

---

## Recommended Filter

Use this Todoist filter to surface all weekly review tasks that are active today:

```text
search: "Weekly Review" & today
```

Or, to see all outstanding tasks across any weekly review project regardless of due date:

```text
search: "Weekly Review"
```

These filters continue to work even if you rename each imported project to include the week.

---

## CLI Auto-Naming

To create a project automatically named for the current week, run one of the following examples with the bundled `create_todoist_project.py` script.

### Bash (Linux)

```bash
TODOIST_API_TOKEN=your_token \
TEMPLATE=weekly-review \
PROJECT_NAME="Weekly Review – Week of $(date -d 'next friday' '+%d/%m')" \
python3 .github/scripts/create_todoist_project.py
```

### Bash (macOS)

```bash
TODOIST_API_TOKEN=your_token \
TEMPLATE=weekly-review \
PROJECT_NAME="Weekly Review – Week of $(date -v+fri '+%d/%m')"
python3 .github/scripts/create_todoist_project.py
```

### PowerShell

```powershell
$env:TODOIST_API_TOKEN = "your_token"
$env:TEMPLATE = "weekly-review"
$env:PROJECT_NAME = "Weekly Review – Week of $((Get-Date).Date.AddDays(((5 - [int](Get-Date).DayOfWeek + 7) % 7)).ToString('dd/MM'))"
python .github/scripts/create_todoist_project.py
```

This produces a project name such as `Weekly Review – Week of 14/03`.

---

## Optional Recurrence Automation

To run your weekly system automatically without manually importing CSV files, use one of the following approaches:

### Option A — Todoist Recurring Task (no-code)

Create a task in Todoist with the following settings:

- **Title**: `Run Weekly Review`
- **Due date**: `every friday 17:00`
- **Description**: Link to this template or your pinned review project

When the task triggers, open your pinned Weekly Review project and work through the existing sections.

### Option B — Scheduled GitHub Actions (automated project creation)

The `create-todoist-project.yml` workflow in this repository supports both manual triggering and scheduled runs.

```yaml
on:
  workflow_dispatch:
  schedule:
    - cron: '0 15 * * 5'   # Every Friday at 15:00 UTC -> weekly-close
    - cron: '0 18 * * 0'   # Every Sunday at 18:00 UTC -> weekly-plan
```

Each scheduled run creates a fresh Todoist project using a purpose-built template for that day. You can still run the same workflow manually and choose `weekly-review` when you want a single combined session.

---

## Import Instructions

1. Download `template.csv`
2. Create a new project in Todoist
3. Import from CSV
4. Rename project to: `Weekly Review – Week of [DD/MM]`
5. Schedule completion within 2 days
