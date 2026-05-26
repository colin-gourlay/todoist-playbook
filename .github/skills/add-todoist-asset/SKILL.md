---
name: add-todoist-asset
description: 'Walk through creating a new asset in todoist-playbook (CSV template, prompt template, or bundle). Use when the user wants to add a new template, add a new prompt, add a new bundle, scaffold a Todoist template, or create a starter kit. Bundles meta.yml / bundle.yml / template.csv / prompt.md stubs.'
---

# Add a Todoist Playbook Asset

## When to Use

- User asks to add or scaffold a new CSV template, prompt template, or bundle
- User asks for a starter / boilerplate / skeleton for any of the above
- User describes a workflow or process they want to capture as a Todoist project

## Procedure

### 1. Identify the asset type

Ask the user which asset type they want, then load the matching scoped instruction file:

| Asset type | Scoped instructions |
|---|---|
| CSV template | [csv-templates.instructions.md](../../instructions/csv-templates.instructions.md) |
| Prompt template | [prompt-templates.instructions.md](../../instructions/prompt-templates.instructions.md) |
| Bundle | [bundles.instructions.md](../../instructions/bundles.instructions.md) |

### 2. Pick a slug

- Kebab-case (lowercase letters, digits, hyphens only)
- Must not collide with an existing folder under the asset's root
- For CSV templates only: decide whether the slug belongs at `csv-templates/{slug}/` or under a category group (e.g. `csv-templates/github/{slug}/`)

### 3. Scaffold the folder

Copy the matching stub files from this skill's `assets/` folder, then customise:

- CSV template — [meta.yml](./assets/csv-template/meta.yml), [template.csv](./assets/csv-template/template.csv), [README.md](./assets/csv-template/README.md)
- Prompt template — [meta.yml](./assets/prompt-template/meta.yml), [prompt.md](./assets/prompt-template/prompt.md), [README.md](./assets/prompt-template/README.md)
- Bundle — [bundle.yml](./assets/bundle/bundle.yml), [README.md](./assets/bundle/README.md)

Set `version: 0.0.0` on every new asset.

### 4. Wire up discovery

- ALWAYS update `index.md` to list the new asset
- Update workflow `inputs` option lists ONLY for the workflows that should expose this asset:
  - CSV template → `create-todoist-project.yml` (and `create-todoist-project-via-mcp.yml` if MCP-enabled)
  - Prompt template → `create-todoist-project-from-prompt.yml`
  - Bundle → no workflow option list update needed
- Update `README.md` ONLY when user-facing discovery copy changes

### 5. Validate locally

Run the validation steps from the [validate-templates-locally](../validate-templates-locally/SKILL.md) skill, or push the branch and let `validate-templates.yml` run in CI.

### 6. Open a PR

Use the [open-pr](../open-pr/SKILL.md) skill or follow `CONTRIBUTING`. For new assets, use `feature/<work-item-id>-<short-description>`.
