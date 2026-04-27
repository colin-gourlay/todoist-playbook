---
description: "Propose a new bundle (curated multi-template starter kit) under bundles/."
argument-hint: "Bundle name + which existing templates to include"
agent: "agent"
---

Propose a new bundle that follows [bundles.instructions.md](../instructions/bundles.instructions.md). Bundles are curated **references** to existing CSV and prompt templates — they do not contain task content themselves.

For the full guided scaffold, prefer the `add-todoist-asset` skill (bundle path). Use this prompt to brainstorm composition and a `bundle.yml` draft.

## Inputs

- **Bundle name** (required)
- **Slug** (optional) — kebab-case; MUST equal folder name
- **Theme / use case** (required) — e.g. "Radio Show Week", "New Job Onboarding"
- **Candidate templates** (optional) — slugs from `csv-templates/` and `prompt-templates/`

## Output

Draft a `bundle.yml`:

```yaml
name: <Human Readable Name>
slug: <kebab-slug>
description: <one-line>
version: 0.0.0
templates:
  - <csv-template-slug>
  - <csv-template-slug>
prompt_templates:
  - <prompt-template-slug>
```

Also outline a short `README.md` explaining:

- The real-world workflow the bundle covers
- Suggested order of use
- How the included templates fit together (no duplicated tasks; complementary scopes)

## Constraints

- Reference only slugs that exist under `csv-templates/` or `prompt-templates/`
- Do not invent new templates inside the bundle — propose them separately if needed
- Keep the set tight: prefer 2–6 templates that genuinely belong together
