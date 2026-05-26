---
name: open-pr
description: 'Branch, commit, push, and open a PR using the repo conventions and gh CLI. Use when the user says open a PR, create a pull request, push a branch, ship this, or commit and push.'
---

# Open a PR

Codifies the branch → commit → push → `gh pr create` flow used in this repo.

## When to Use

- User says "open a PR", "create a PR", "ship this", "push and open a PR"
- A logical change is ready to merge into `main`

## Prerequisites

- Working tree contains the intended change and nothing else
- `gh` CLI is authenticated (see `/memories/repo/git-workflow-notes.md`)
- The change is on `main` or an existing short-lived branch that matches the branch naming policy

## Procedure

### 1. Confirm the working tree

```pwsh
git status
git diff --stat
```

If unrelated changes are present, split them into separate branches (one logical change per branch).

### 2. Create a branch

Use a GitHub Flow branch type from `CONTRIBUTING` and include the work item ID:

| Prefix | Use for |
|---|---|
| `feature/` | New asset or feature |
| `fix/` | Bug fix |
| `docs/` | Docs-only |
| `chore/` | Maintenance, workflows, scripts, and housekeeping |

```pwsh
git checkout -b <type>/<work-item-id>-<short-kebab-description>
```

Examples: `feature/1234-branch-ruleset-guardrails`, `docs/5678-update-contributing`

Branch names must match:

```text
^(feature|fix|docs|chore)/[0-9]+-[a-z0-9-]+$
```

### 3. Commit

Conventional Commits format. Imperative mood. No trailing period. Under 72 chars on the summary line.

```pwsh
git add <paths>
git commit -m "<type>: <summary>"
```

### 4. Push

```pwsh
git push -u origin <branch>
```

### 5. Open the PR with `gh`

The PR title MUST follow Conventional Commits — it becomes the squash-merge commit message on `main`.

For multi-paragraph PR bodies on Windows PowerShell, write the body to a temp file and use `--body-file` (or use a single-quoted here-string `@'...'@`). Double-quoted here-strings `@"..."@` interpolate `$variables` and break PR bodies.

```pwsh
$body = @'
Summary paragraph.

## Changes
- bullet one
- bullet two
'@
Set-Content -Path .pr-body.tmp -Value $body -NoNewline
gh pr create --base main --head <branch> --title "<type>: <summary>" --body-file .pr-body.tmp
Remove-Item .pr-body.tmp
```

### 6. Report the PR URL

Surface the PR URL `gh` prints back to the user.

## Merge strategy

This repo uses **Squash and merge**. The PR title becomes the commit on `main`. Delete the branch after merge.
