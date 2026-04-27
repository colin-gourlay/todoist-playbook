# {{Prompt Template Name}}

One-paragraph description of what this prompt template generates and when to use it.

## Inputs

| Name | Description |
|---|---|
| `input_one` | What it represents |
| `input_two` | What it represents |

## Output shape

CSV matching the Todoist importer header. One or more sections, each containing tasks.

## Worked example

**Inputs**

- `input_one`: example value
- `input_two`: example value

**Output (truncated)**

```
TYPE,CONTENT,DESCRIPTION,IS_COLLAPSED,PRIORITY,INDENT,AUTHOR,RESPONSIBLE,DATE,DATE_LANG,TIMEZONE,DURATION,DURATION_UNIT,DEADLINE,DEADLINE_LANG
section,Example Section,,,,1,,,,,,,,,
task,Example task,,,4,1,,,,en,,,,,
```
