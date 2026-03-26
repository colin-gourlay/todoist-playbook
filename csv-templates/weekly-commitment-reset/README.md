# Weekly Commitment Reset

A structured weekly audit for reviewing and resetting all active commitments — triaging waiting items, surfacing someday ideas, and re-committing only to what matters.

This template is designed to be used once per week, ideally on a Friday afternoon or Sunday evening.

---

## Objective

- Audit every active commitment for validity
- Chase or close out all waiting items
- Promote or remove items from the someday list
- Clear the review queue completely
- Recommit to a sustainable number of priorities
- Enter the new week with a clean, trusted system

Estimated duration: approximately 30 minutes.

---

## When to Use

- Friday afternoon (end-of-week reset)
- Sunday evening (week ahead preparation)
- Any time you feel overwhelmed by the volume of open loops in your system

---

## Label System

This template is built around four core labels applied to tasks across your entire Todoist system:

| Label | Purpose |
| ----- | ------- |
| `@commitment` | Explicit obligation or promise — you have agreed to deliver this |
| `@waiting` | Blocked by an external dependency — action is with someone or something else |
| `@someday` | Not an active commitment — captured for future consideration |
| `@review` | Needs reassessment — flagged for evaluation during the next reset |

Apply these labels consistently across all your Todoist projects so that the filters used in this workflow surface the right tasks.

---

## Structure Overview

1. Audit Active Commitments
2. Triage Waiting Items
3. Review Someday / Maybe
4. Process Review Queue
5. Reset & Recommit
6. Update & Align

---

## Suggested Ritual

- Block 30 minutes in your calendar
- Silence notifications
- Work through each section in order
- Do not leave any `@review` items unprocessed
- End with a clear list of your top three commitments for the week ahead

---

## Recommended Filters

Set up the following Todoist filters before your first session. These filters surface tasks across your entire Todoist account by label, regardless of which project they belong to.

### Active Commitments

```text
@commitment & !@waiting
```

All tasks you are actively committed to and are not currently blocked.

### Waiting On

```text
@waiting
```

All tasks where the next action is with someone or something else.

### Someday / Maybe

```text
@someday
```

All tasks that are captured but not actively committed to.

### Review Queue

```text
@review
```

All tasks flagged for reassessment during the next weekly reset.

### Full Commitment Overview

```text
@commitment | @waiting | @someday | @review
```

A single view of your entire commitment landscape.

### Overdue Commitments

```text
@commitment & overdue
```

Any committed task with a past due date — prioritise these first.

---

## Labels Suggested

All tasks in this template are pre-tagged with the following labels:

| Label | Meaning |
| ----- | ------- |
| `@when-weekly` | Best performed during a weekly review or reset session |
| `@duration-5m` | Short step — typically a scan or a single decision |
| `@duration-10m` | Moderate step — requires attention and some judgement |

---

## CLI Auto-Naming

To create a project automatically named for the current week, run one of the following examples with the bundled `create_todoist_project.py` script.

### Bash (Linux)

> **Note**: On Linux, `next friday` returns the next calendar occurrence of Friday. If today is Friday, it will resolve to today rather than the following Friday. Run the script earlier in the week or adjust the offset if needed.

```bash
TODOIST_API_TOKEN=your_token \
TEMPLATE=weekly-commitment-reset \
PROJECT_NAME="Commitment Reset – Week of $(date -d 'next friday' '+%d/%m')" \
python3 .github/scripts/create_todoist_project.py
```

### Bash (macOS)

```bash
TODOIST_API_TOKEN=your_token \
TEMPLATE=weekly-commitment-reset \
PROJECT_NAME="Commitment Reset – Week of $(date -v+fri '+%d/%m')" \
python3 .github/scripts/create_todoist_project.py
```

### PowerShell

```powershell
$env:TODOIST_API_TOKEN = "your_token"
$env:TEMPLATE = "weekly-commitment-reset"
$env:PROJECT_NAME = "Commitment Reset – Week of $((Get-Date).Date.AddDays(((5 - [int](Get-Date).DayOfWeek + 7) % 7)).ToString('dd/MM'))"
python .github/scripts/create_todoist_project.py
```

This produces a project name such as `Commitment Reset – Week of 14/03`.

---

## Import Instructions

1. Download `template.csv`
2. Create a new project in Todoist
3. Import from CSV
4. Rename project to: `Commitment Reset – Week of [DD/MM]`
5. Schedule completion within 2 days
