---
description: "Facilitate a Stop / Start / Continue reflection for a given context."
argument-hint: "Context (work, personal, a specific project)"
agent: "ask"
---

Facilitate a Stop / Start / Continue retrospective for the context the user provides. Ask one or two clarifying questions if the context is too thin, then produce a structured reflection.

## Inputs

- **Context** (required) — work, personal, a specific project, the past week, etc.
- **Recent observations** (optional) — anything the user already wants to capture

## Output

```
## Stop
- <inefficiency, distraction, or anti-pattern> — why it's costing you

## Start
- <new behaviour or experiment> — the smallest viable first step

## Continue
- <what's working> — why to keep it and how to protect it
```

## Style

- 3–5 items per section
- Concrete and specific (not "work less" — instead "end work by 18:00 on Tuesdays")
- Each item one line, optionally followed by a short rationale
- Prefer reflection over advice; mirror the user's own language
