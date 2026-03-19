## Summary

<!-- Briefly describe what this PR adds or changes. -->

## Type of Change

<!-- Check the one that applies: -->

- [ ] `feat` — new template, prompt template, bundle, or feature
- [ ] `fix` — bug fix or correction to existing content
- [ ] `docs` — documentation only (README, CONTRIBUTING, index.md, etc.)
- [ ] `ci` — GitHub Actions workflow or script change
- [ ] `chore` — maintenance, renaming, or housekeeping

## Checklist

<!-- For new or updated templates: -->

- [ ] Folder name is kebab-case and matches `slug:` in `meta.yml`
- [ ] All three required files are present: `template.csv`, `meta.yml`, `README.md`
- [ ] `meta.yml` includes all required keys (`name`, `slug`, `description`, `category`, `tags`, `version`)
- [ ] `template.csv` header starts with `TYPE`; only `section` and `task` values used in TYPE column
- [ ] No hardcoded due dates in `template.csv`
- [ ] Slug added to `options` list in `.github/workflows/create-todoist-project.yml`
- [ ] Row added to the catalogue table in `index.md`

<!-- For all PRs: -->

- [ ] PR title follows Conventional Commits format (e.g. `feat: add sprint-review template`)
- [ ] CI validation passes (`validate-templates` workflow)
