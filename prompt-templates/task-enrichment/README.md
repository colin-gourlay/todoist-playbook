# Task Enrichment

An AI prompt template that converts a brief task title and context into a fully structured Todoist task — including an action-oriented title, a Markdown description with goal and steps, and optional sub-tasks.

---

## Objective

- Transform a vague task idea into a clear, actionable Todoist entry
- Produce consistent, Markdown-formatted descriptions that Todoist renders natively
- Reduce the cognitive effort of breaking down tasks manually
- Work with any major AI model (ChatGPT, GitHub Copilot, Claude, Gemini, etc.)

---

## When to Use

- When you have a task idea but are not sure how to break it down
- Before adding high-priority or complex tasks to Todoist
- When you want consistent task descriptions across a project
- When onboarding a team to a shared task format

---

## Inputs

| Variable | Required | Description |
|----------|----------|-------------|
| `{{task_title}}` | Yes | Short, one-line task idea |
| `{{context}}` | No | Background, goal, or constraints |
| `{{priority}}` | No | `urgent`, `high`, `medium`, or `normal` — defaults to `normal` |

---

## Output Schema

The prompt produces three top-level sections:

| Section | Todoist Field | Notes |
|---------|---------------|-------|
| `TITLE:` | Task name | Action-oriented, max 120 characters |
| `DESCRIPTION:` | Task description | Markdown — includes Goal, Steps, and optional Notes |
| `SUBTASKS` | Sub-tasks | Optional flat list for task decomposition |

---

## Usage Instructions

1. Open `prompt.md` in this folder.
2. Copy the text inside the `## Prompt` section.
3. Replace all `{{placeholders}}` with your actual values.
4. Paste into your preferred AI assistant and run.
5. Copy the model's output into Todoist:
   - `TITLE:` → task name field
   - `DESCRIPTION:` block → task description field
   - `SUBTASKS:` items → individual sub-tasks (if present)
6. Set Todoist priority:
   - `urgent` → P1
   - `high` → P2
   - `medium` → P3
   - `normal` → P4

---

## Example

### Input

```
Task title:   Write onboarding email for new SaaS trial users
Context:      We are launching a B2B SaaS product next week. Trial users need guidance within the first 24 hours.
Priority:     high
```

### Output

```
TITLE: Write onboarding email sequence for new SaaS trial users

DESCRIPTION:
## Goal
Draft a 24-hour onboarding email that helps trial users reach their first activation milestone within the product.

## Steps
1. Review the activation milestone definition with the product team
2. Draft subject line and preview text variants (A/B)
3. Write body copy covering: welcome, key feature spotlight, and one clear CTA
4. Add personalisation tokens (first name, company name)
5. Review copy with a teammate for tone and clarity
6. Schedule send via email platform

## Notes
- Coordinate with marketing on brand voice guidelines before drafting
- Confirm email platform supports dynamic send-time triggers

SUBTASKS:
- Define activation milestone with product team
- Draft subject line variants
- Write body copy
- Add personalisation tokens
- Peer review copy
- Schedule and configure send trigger
```

---

## Notes

- The prompt is provider-agnostic — any instruction-following LLM will work.
- Keep `{{context}}` concise; one to three sentences is sufficient.
- If the model omits required sections, re-run with the instruction: *"Return only the sections TITLE, DESCRIPTION, and SUBTASKS (if applicable) with no additional commentary."*
- Todoist renders standard Markdown in task descriptions — headings, bold, and numbered lists all display correctly.
