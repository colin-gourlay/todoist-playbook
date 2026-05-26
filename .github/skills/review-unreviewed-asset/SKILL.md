---
name: review-unreviewed-asset
description: 'Review an asset at version 0.0.0 against the repo conventions and graduate it to 0.1.0 once it passes. Use when the user wants to review a template, graduate a template, mark a template stable, bump from 0.0.0, or close a template-review issue.'
---

# Review an Unreviewed Asset

Graduate a CSV template, prompt template, or bundle from `version: 0.0.0` (unreviewed) to `0.1.0` (reviewed and stable).

## When to Use

- The user asks to review, graduate, or stabilise an asset
- A template-review issue (created by `sync-template-review-issues.yml`) needs closing
- An asset has been in `0.0.0` long enough to assess

## Procedure

### 1. Identify the asset

Confirm the slug, asset type, and current `version:` in the metadata file. If `version:` is not `0.0.0`, stop — this skill is only for first review.

### 2. Run the conventions checklist

Delegate the full review to the [template-reviewer](../../agents/template-reviewer.agent.md) custom agent (read-only, returns a single review summary). For a manual review, walk the relevant scoped instructions:

- CSV template → [csv-templates.instructions.md](../../instructions/csv-templates.instructions.md)
- Prompt template → [prompt-templates.instructions.md](../../instructions/prompt-templates.instructions.md)
- Bundle → [bundles.instructions.md](../../instructions/bundles.instructions.md)

The asset must:

- Pass `validate-templates.yml`
- Conform to its scoped instructions (folder layout, required keys, slug match)
- Have a `README.md` that is accurate, complete, and includes the right kind of guidance for the asset type
- Use the correct `category:` (re-use an existing value where one fits)
- Avoid hardcoded dates, contributor-specific identifiers, or stale references

### 3. Address findings

Fix everything the review flags. If a finding requires a behavioural change to the asset, that is in scope; if it requires a behavioural change to validation, raise it as a separate issue.

### 4. Bump to 0.1.0

Hand-edit the metadata file:

```yaml
version: 0.1.0
```

Note: this is the ONE legitimate hand-bump. After 0.1.0, `bump-template-version.yml` takes over patch bumps automatically on merged PRs — do not hand-edit `version:` again.

### 5. Open a PR

Use a `chore/` branch with a work item ID (e.g. `chore/1234-review-{slug}`) and a Conventional Commits message such as:

```
chore: graduate {slug} to version 0.1.0
```

In the PR body, link the corresponding template-review issue and summarise the review findings. `sync-template-review-issues.yml` will close the review issue once the change is merged.
