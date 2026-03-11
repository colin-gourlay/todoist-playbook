# Weekly Review

A structured reset process designed to reduce cognitive load and increase clarity.

This template is designed to be used once per week.

---

## Objective

- Close open loops
- Reset commitments
- Identify priorities
- Enter the new week with clarity

Estimated duration: 30–45 minutes.

---

## When to Use

- Friday afternoon
- Sunday evening
- Whenever feeling overwhelmed

---

## Structure Overview

1. Close the Past
2. Clear the Present
3. Review Commitments
4. Plan the Future
5. Performance Review & Alignment
6. Stop / Start / Continue

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
|-------|---------|
| `@people-self` | Task is self-directed — no delegation required |
| `@place-anywhere` | Can be completed from any location (home, café, commute, etc.) |
| `@tools-todoist` | Todoist itself is the primary tool for completing this task |
| `@when-evening` | Best suited to late afternoon or evening time blocks |
| `@duration-25m` | Each task is estimated at ~25 minutes |

> **Note on `@place-anywhere`**: This label was recently added to signal that the weekly review is location-independent. Unlike deep work tasks that may require a specific environment, every step of this review can be completed wherever you have access to Todoist.

---

## Recommended Filter

Use this Todoist filter to surface all weekly review tasks that are active today:

```
#Weekly Review & today
```

Or, to see all outstanding tasks across any weekly review project regardless of due date:

```
search: Weekly Review
```

Pin the first filter as a favourite for quick access at the start of each review session.

---

## CLI Auto-Naming

To create a project automatically named for the current week, run the following from your terminal (requires the [Todoist CLI](https://github.com/sachaos/todoist) or the bundled `create_todoist_project.py` script):

```bash
# Using the bundled Python script
TODOIST_API_TOKEN=your_token \
TEMPLATE=weekly-review \
PROJECT_NAME="Weekly Review – Week of $(date -d 'next friday' '+%d/%m')" \
python3 .github/scripts/create_todoist_project.py
```

On macOS, replace `date -d 'next friday'` with `date -v+fri`:

```bash
PROJECT_NAME="Weekly Review – Week of $(date -v+fri '+%d/%m')"
```

This produces a project name such as `Weekly Review – Week of 14/03`.

---

## Optional Recurrence Automation

To run this review automatically each week without manually importing the CSV, use one of the following approaches:

### Option A — Todoist Recurring Task (no-code)

Create a task in Todoist with the following settings:

- **Title**: `Run Weekly Review`
- **Due date**: `every friday 17:00`
- **Description**: Link to this template or your pinned review project

When the task triggers, open your pinned Weekly Review project and work through the existing sections.

### Option B — Scheduled GitHub Actions (automated project creation)

The `create-todoist-project.yml` workflow in this repository supports manual triggering via `workflow_dispatch`. To also run it automatically each week, add a `schedule` trigger to `.github/workflows/create-todoist-project.yml`:

```yaml
on:
  workflow_dispatch:
    # ... existing inputs ...
  schedule:
    - cron: '0 16 * * 5'   # Every Friday at 16:00 UTC
```

Each run creates a fresh, pre-named project in your Todoist account using the `weekly-review` template as the default.

---

## Import Instructions

1. Download `template.csv`
2. Create a new project in Todoist
3. Import from CSV
4. Rename project to: `Weekly Review – Week of [DD/MM]`
5. Schedule completion within 2 days
