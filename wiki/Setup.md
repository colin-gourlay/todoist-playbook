# Setup

This page covers everything you need to configure the Todoist Playbook and start creating Todoist projects from templates.

---

## Prerequisites

| Requirement | Details |
|-------------|---------|
| **Todoist account** | Free or paid. The API token is available on both plans. |
| **GitHub account** | Required to fork the repository and use GitHub Actions. |
| **Todoist API token** | Retrieved from [Todoist Integrations Settings](https://app.todoist.com/app/settings/integrations/developer) |

---

## 1. Fork the Repository

1. Go to [github.com/colin-gourlay/todoist-playbook](https://github.com/colin-gourlay/todoist-playbook)
2. Click **Fork** (top right)
3. Choose your GitHub account as the destination
4. Click **Create fork**

Forking gives you your own copy of the Playbook that you can customise, extend, and keep in sync with upstream improvements.

---

## 2. Add the Todoist API Token

The automation workflows communicate with Todoist via its REST API. You need to store your API token as a GitHub secret.

### Get your Todoist API token

1. Log in to Todoist
2. Go to **Settings → Integrations → Developer**
3. Copy the API token shown under **API token**

### Add the secret to your fork

1. In your forked repository, go to **Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Name: `TODOIST_API_TOKEN`
4. Value: paste your API token
5. Click **Add secret**

> ⚠️ Never commit your API token to the repository. Always use GitHub Secrets.

---

## 3. Enable GitHub Actions

GitHub Actions are enabled by default on forked repositories, but if they are disabled:

1. Go to the **Actions** tab in your fork
2. Click **I understand my workflows, go ahead and enable them**

---

## 4. (Optional) Enable GitHub Pages

The Playbook includes a template gallery that deploys to GitHub Pages automatically.

1. Go to **Settings → Pages**
2. Under **Source**, select **GitHub Actions**
3. Push any change to `main` (or manually trigger the **Deploy Template Gallery** workflow) to build and deploy the gallery

---

## 5. Create Your First Project

### Using the Automated Workflow (recommended)

1. Go to the **Actions** tab
2. Select **Create Todoist Project from Template**
3. Click **Run workflow**
4. Fill in the inputs:
   - **Template**: choose from the dropdown (e.g. `weekly-review`)
   - **Project name**: optional — leave blank to use the template's default name
   - **Colour**: optional project colour
   - **Mark as favourite**: optional
   - **Parent project**: optional — nest this project under an existing Todoist project
5. Click **Run workflow**

Within a few seconds the project will appear in Todoist.

### Using the Manual Import

1. Browse `index.md` to find a template
2. Navigate to the CSV template folder (e.g. `csv-templates/weekly-review/`)
3. Download `template.csv`
4. In Todoist:
   - Create a new project
   - Open the project menu (three dots)
   - Select **Import from CSV**
   - Upload the file

---

## 6. Sync Your Todoist Project List (optional)

The **Create Todoist Project from Template** workflow supports nesting new projects under existing Todoist projects. The parent project list is kept up to date by a sync workflow.

To refresh the parent project dropdown:

1. Go to **Actions → Sync Todoist Project List**
2. Click **Run workflow**

This fetches all your current Todoist projects and rewrites the dropdown options in the `create-todoist-project.yml` workflow file, then commits the change.

---

## 7. Use AI Prompt Templates (optional)

Prompt templates use GitHub Copilot to generate enriched task content before creating a project.

### Prerequisites

- The repository must have **GitHub Copilot** enabled (available on GitHub Team, Enterprise, or individual Copilot subscriptions)
- The `TODOIST_API_TOKEN` secret must already be configured

### Workflow

1. Go to **Actions → Create Todoist Project from Prompt Template**
2. Click **Run workflow**
3. Fill in the inputs:
   - **Prompt template**: select from the dropdown
   - **Task title**: a short description of the task
   - **Context**: optional additional context for the AI
   - **Priority**: optional priority
   - **Project name**: optional custom project name
4. Click **Run workflow**

Copilot generates structured task content from the prompt template and the project is created in Todoist automatically.

---

## 8. Use the MCP Workflow (optional)

The MCP workflow routes all Todoist API calls through the [Todoist MCP server](https://ai.todoist.net/mcp).

1. Go to **Actions → Create Todoist Project via MCP**
2. Click **Run workflow**
3. Select a template and optional project name
4. Click **Run workflow**

---

## Workflow Schedules

Some workflows run on a schedule in addition to on-demand:

| Workflow | Schedule | Default behaviour |
|----------|----------|-------------------|
| **Create Todoist Project from Template** | Fridays at 15:00 UTC, Sundays at 18:00 UTC | Creates `weekly-close` on Fridays and `weekly-plan` on Sundays; also runs after successful trending sync and creates `github-trending-tracker-daily` |
| **GitHub Trending to Todoist** | Daily at 05:30 UTC | Creates a dated project with trending repos as `read-later` tasks |
| **Sync Todoist Project List** | Daily at 06:00 UTC | Updates the parent project dropdown |
| **Documentation Sync** | Daily at 08:22 UTC | Runs the compiled docs-maintenance workflow generated from `doc-sync.md` |

---

## Adding Your Own Templates

See [CONTRIBUTING](../CONTRIBUTING) for the full guide. In brief:

1. Create a folder `csv-templates/{slug}/` using kebab-case naming
2. Add `meta.yml` with the required keys (`name`, `slug`, `description`, `category`, `tags`, `version`)
3. Add `template.csv` starting with the `TYPE` header
4. Add `README.md` with usage guidance and import instructions
5. Add the slug to the `options` list in `.github/workflows/create-todoist-project.yml`
6. Update `index.md` to add the template to the catalogue
7. Push to `main` — CI validates the template automatically

---

## Troubleshooting

| Problem | Solution |
|---------|---------|
| Workflow fails with `TODOIST_API_TOKEN secret is not set` | Add the `TODOIST_API_TOKEN` secret under **Settings → Secrets and variables → Actions** |
| Project is created but has no tasks | Check that `template.csv` starts with the `TYPE` header and uses only `section`/`task` row types |
| `meta.yml` slug mismatch error in CI | Ensure the `slug:` value in `meta.yml` exactly matches the folder name (case-sensitive, no quotes) |
| Parent project dropdown is empty or stale | Run the **Sync Todoist Project List** workflow to refresh it |
| Gallery is not updating on GitHub Pages | Ensure GitHub Pages is configured to use **GitHub Actions** as the source |
