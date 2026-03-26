# Reusable Workflows & Composite Actions

The workflows and composite action in this repository are designed to be called from **other repositories** as well as from within this repo itself. They are pinned by release tag (e.g. `@v2026.3.22`) so consuming repos can control when they adopt updates.

---

## Available reusable workflows

### 1. `reusable-validate-templates.yml` — Validate template structure

Validates that every folder under `csv-templates/` and `prompt-templates/` conforms to the required structure (kebab-case slug, required files, `meta.yml` keys, CSV format, README import instructions).

**Inputs**

| Input | Description | Default |
|---|---|---|
| `templates_path` | Path to the CSV templates directory | `csv-templates` |
| `prompt_templates_path` | Path to the prompt-templates directory | `prompt-templates` |

**Example**

```yaml
jobs:
  validate:
    uses: colin-gourlay/todoist-playbook/.github/workflows/reusable-validate-templates.yml@v2026.3.22
    with:
      templates_path: csv-templates
      prompt_templates_path: prompt-templates
```

---

### 2. `reusable-deploy-pages-gallery.yml` — Build & deploy GitHub Pages gallery

Runs a Python gallery-generation script, uploads the output directory as a Pages artifact, and deploys it via `actions/deploy-pages`.

**Permissions required in the calling workflow**

```yaml
permissions:
  contents: read
  pages: write
  id-token: write
```

**Inputs**

| Input | Description | Default |
|---|---|---|
| `build_script` | Path to the gallery-generation script | `.github/scripts/generate_gallery.py` |
| `artifact_path` | Directory to upload as the Pages artifact | `docs` |

**Example**

```yaml
jobs:
  deploy:
    uses: colin-gourlay/todoist-playbook/.github/workflows/reusable-deploy-pages-gallery.yml@v2026.3.22
    with:
      build_script: .github/scripts/generate_gallery.py
      artifact_path: docs
```

---

### 3. `reusable-release-assets.yml` — Generate & publish a GitHub Release

Runs a Python script to generate release assets, computes a unique date-based tag (`vYYYY.M.D[-N]`), and creates a GitHub Release with the specified asset files.

**Permissions required in the calling workflow**

```yaml
permissions:
  contents: write
```

**Inputs**

| Input | Description | Default |
|---|---|---|
| `assets_zip_path` | Path to the ZIP asset | `dist/csv-templates.zip` |
| `assets_index_path` | Path to the JSON index asset | `dist/index.json` |
| `tag_prefix` | Prefix for the computed date tag | `v` |

**Example**

```yaml
jobs:
  release:
    uses: colin-gourlay/todoist-playbook/.github/workflows/reusable-release-assets.yml@v2026.3.22
    with:
      assets_zip_path: dist/csv-templates.zip
      assets_index_path: dist/index.json
```

---

## Available composite actions

### `commit-and-push` — Stage, commit, and push changes

Configures git identity, stages files, checks for changes, commits, and pushes — either to the current branch or to an explicit ref (useful for PR head-branch pushes).

**Path:** `.github/actions/commit-and-push`

**Inputs**

| Input | Required | Description | Default |
|---|---|---|---|
| `commit_message` | ✅ | Commit message | — |
| `add` | ❌ | Space-separated paths/globs to stage | `.` |
| `push_to` | ❌ | Branch ref to push to (e.g. `github.head_ref`) | _(current branch)_ |
| `user_name` | ❌ | Git committer name | `github-actions[bot]` |
| `user_email` | ❌ | Git committer email | `github-actions[bot]@users.noreply.github.com` |

**Example — push to current branch**

```yaml
- name: Commit and push changes
  uses: colin-gourlay/todoist-playbook/.github/actions/commit-and-push@v2026.3.22
  with:
    commit_message: "chore: update generated files"
    add: "docs/"
```

**Example — push to PR head branch**

```yaml
- name: Commit and push to PR branch
  uses: colin-gourlay/todoist-playbook/.github/actions/commit-and-push@v2026.3.22
  with:
    commit_message: "chore: bump version(s)"
    add: "csv-templates/*/meta.yml"
    push_to: ${{ github.head_ref }}
```

---

## Pinning to a tag

All reusable workflows and composite actions should be pinned to a specific release tag for stability:

```yaml
uses: colin-gourlay/todoist-playbook/.github/workflows/reusable-validate-templates.yml@v2026.3.22
```

Browse available tags at:  
[https://github.com/colin-gourlay/todoist-playbook/tags](https://github.com/colin-gourlay/todoist-playbook/tags)

To adopt a newer release, update the `@<tag>` suffix in your caller workflow.
