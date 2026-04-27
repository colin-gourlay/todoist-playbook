---
applyTo: "bundles/**"
description: Conventions and procedures for template bundles.
---

# Bundle Conventions

## Folder layout

Every bundle lives at `bundles/{slug}/`. Folder name MUST be kebab-case and MUST contain:

- `bundle.yml`
- `README.md`

## `bundle.yml` fields

```yaml
name: Bundle Name
slug: bundle-slug          # MUST equal the folder name
description: One-line description
category: kebab-case-category
tags:
  - tag-one
version: 0.0.0             # new bundles start unreviewed
templates:
  - template-slug          # MUST reference an existing csv-templates/<slug>
optional_templates:
  - optional-template-slug # MUST reference an existing csv-templates/<slug>
```

## Rules

- `templates:` entries MUST reference existing CSV template slugs
- `optional_templates:` (when present) MUST reference existing CSV template slugs
- New bundles start at `version: 0.0.0`

## Adding a new bundle

1. Create `bundles/{slug}/` (kebab-case)
2. Add `bundle.yml`, `README.md`
3. Verify every slug in `templates:` / `optional_templates:` exists under `csv-templates/`
4. Update `index.md` to list the new bundle
5. Update `README.md` only if user-facing discovery copy needs changing
