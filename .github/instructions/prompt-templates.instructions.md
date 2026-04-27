---
applyTo: "prompt-templates/**"
description: Conventions and procedures for AI prompt templates.
---

# Prompt Template Conventions

## Folder layout

Every prompt template lives at `prompt-templates/{slug}/`. Folder name MUST be kebab-case and MUST contain exactly:

- `prompt.md`
- `meta.yml`
- `README.md`

## Required `meta.yml` keys

```yaml
name: Human Readable Name
slug: folder-slug          # MUST equal the folder name
description: One-line description
category: kebab-case-category
tags:
  - tag-one
version: 0.0.0             # 0.0.0 = unreviewed, 0.1.0 = reviewed
inputs:
  - input_name             # one entry per {{placeholder}} used in prompt.md
```

## `prompt.md` rules

- MUST contain at least one `{{placeholder}}` variable
- `{{placeholder}}` names MUST match the `inputs:` list in `meta.yml`
- Keep prompts provider-agnostic where practical
- Define a clear output shape inside the prompt (e.g. CSV matching the importer header, JSON schema, markdown checklist)
- `README.md` MUST document the expected output and include at least one worked example

## Adding a new prompt template

1. Create `prompt-templates/{slug}/` (kebab-case)
2. Add `prompt.md`, `meta.yml`, `README.md`
3. Set `version: 0.0.0`
4. Ensure `inputs:` matches every `{{placeholder}}` used
5. Update `index.md` to list the new prompt template
6. Add the slug to `create-todoist-project-from-prompt.yml` `inputs.prompt_template` options
7. Update `README.md` only if user-facing discovery copy needs changing

## Common validation failures

- `inputs:` missing from `meta.yml`
- `prompt.md` contains no `{{placeholder}}` variable
- `inputs:` and `{{placeholder}}` names disagree
- `slug:` does not match the folder name
