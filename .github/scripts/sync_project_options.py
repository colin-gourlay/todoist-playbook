#!/usr/bin/env python3
"""Sync workflow dropdown options used by project-creation workflows.

This script performs two kinds of synchronization:
1) Fetch Todoist projects and update the parent_project options in
    create-todoist-project.yml.
2) Discover local CSV/prompt template slugs and update workflow_dispatch choice
    options in project-creation workflows.

The workflow files are edited only between sentinel comments, preserving all
other user-authored YAML.
"""

import json
import os
import sys
from pathlib import Path
import urllib.error
import urllib.request

TODOIST_API_BASE = "https://api.todoist.com/api/v1"
CREATE_PROJECT_WORKFLOW_PATH = ".github/workflows/create-todoist-project.yml"
CREATE_VIA_MCP_WORKFLOW_PATH = ".github/workflows/create-todoist-project-via-mcp.yml"
CREATE_FROM_PROMPT_WORKFLOW_PATH = ".github/workflows/create-todoist-project-from-prompt.yml"
CSV_TEMPLATES_DIR = "csv-templates"
PROMPT_TEMPLATES_DIR = "prompt-templates"

# These markers delimit the auto-generated options block inside the YAML file.
BEGIN_TODOIST_PROJECTS = "          # BEGIN_TODOIST_PROJECTS (auto-updated by the sync-todoist-projects workflow)"
END_TODOIST_PROJECTS = "          # END_TODOIST_PROJECTS"

BEGIN_CSV_TEMPLATES_CREATE = "          # BEGIN_CSV_TEMPLATES_CREATE (auto-updated by the sync-todoist-projects workflow)"
END_CSV_TEMPLATES_CREATE = "          # END_CSV_TEMPLATES_CREATE"

BEGIN_CSV_TEMPLATES_MCP = "          # BEGIN_CSV_TEMPLATES_MCP (auto-updated by the sync-todoist-projects workflow)"
END_CSV_TEMPLATES_MCP = "          # END_CSV_TEMPLATES_MCP"

BEGIN_PROMPT_TEMPLATES = "          # BEGIN_PROMPT_TEMPLATES (auto-updated by the sync-todoist-projects workflow)"
END_PROMPT_TEMPLATES = "          # END_PROMPT_TEMPLATES"


def fetch_projects(token):
    """Return all projects from the Todoist API."""
    url = f"{TODOIST_API_BASE}/projects"
    headers = {"Authorization": f"Bearer {token}"}
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        print(f"❌ Todoist API error {exc.code}: {exc.read().decode()}", file=sys.stderr)
        sys.exit(1)


def yaml_single_quote(value):
    """Wrap *value* in YAML single quotes, escaping any embedded single quotes."""
    return "'" + value.replace("'", "''") + "'"


def discover_template_slugs(base_dir):
    """Return sorted template slugs for directories that contain a metadata file."""
    root = Path(base_dir)
    if not root.is_dir():
        print(f"❌ Template directory not found: {base_dir}", file=sys.stderr)
        sys.exit(1)

    slugs = []
    for child in root.iterdir():
        if child.is_dir() and (child / "meta.yml").is_file():
            slugs.append(child.name)

    return sorted(slugs)


def replace_block(lines, begin_marker, end_marker, new_items, include_empty_choice):
    """Replace the lines between marker comments with an auto-generated options block."""
    begin_idx = end_idx = None
    for i, line in enumerate(lines):
        if line.rstrip("\n") == begin_marker:
            begin_idx = i
        elif line.rstrip("\n") == end_marker:
            end_idx = i
            break

    if begin_idx is None or end_idx is None:
        print(
            "❌ Could not find sentinel markers in workflow file.\n"
            "Expected lines:\n"
            f"  {begin_marker}\n"
            f"  {end_marker}",
            file=sys.stderr,
        )
        sys.exit(1)

    new_block = [begin_marker + "\n"]
    if include_empty_choice:
        new_block.append("          - ''\n")
    for item in new_items:
        new_block.append(f"          - {yaml_single_quote(item)}\n")
    new_block.append(end_marker + "\n")

    return lines[:begin_idx] + new_block + lines[end_idx + 1 :]


def update_workflow(workflow_path, block_specs):
    """Update one workflow file by replacing each marker-delimited options block."""
    with open(workflow_path, encoding="utf-8") as f:
        lines = f.readlines()

    for begin_marker, end_marker, items, include_empty_choice in block_specs:
        lines = replace_block(lines, begin_marker, end_marker, items, include_empty_choice)

    with open(workflow_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"✅ Updated {workflow_path}")


def main():
    token = os.environ.get("TODOIST_API_TOKEN", "").strip()
    if not token:
        print("❌ TODOIST_API_TOKEN is not set.", file=sys.stderr)
        sys.exit(1)

    projects = fetch_projects(token)

    if not isinstance(projects, list):
        preview = str(projects)[:200]
        print(
            f"❌ Unexpected API response (expected a list, got {type(projects).__name__}): {preview}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Exclude the Inbox project and sort the rest alphabetically.
    # Check both field names to handle differences across Todoist API versions
    # (`is_inbox_project` in REST v2, `inbox_project` in API v1).
    project_names = sorted(
        p["name"]
        for p in projects
        if isinstance(p, dict)
        and not p.get("is_inbox_project", False)
        and not p.get("inbox_project", False)
    )

    print(f"📋 Found {len(project_names)} Todoist project(s)")
    for name in project_names:
        print(f"  - {name}")

    csv_template_slugs = discover_template_slugs(CSV_TEMPLATES_DIR)
    prompt_template_slugs = discover_template_slugs(PROMPT_TEMPLATES_DIR)

    print(f"🧩 Found {len(csv_template_slugs)} CSV template slug(s)")
    print(f"🧠 Found {len(prompt_template_slugs)} prompt template slug(s)")

    update_workflow(
        CREATE_PROJECT_WORKFLOW_PATH,
        [
            (BEGIN_CSV_TEMPLATES_CREATE, END_CSV_TEMPLATES_CREATE, csv_template_slugs, True),
            (BEGIN_TODOIST_PROJECTS, END_TODOIST_PROJECTS, project_names, True),
        ],
    )

    update_workflow(
        CREATE_VIA_MCP_WORKFLOW_PATH,
        [
            (BEGIN_CSV_TEMPLATES_MCP, END_CSV_TEMPLATES_MCP, csv_template_slugs, True),
        ],
    )

    update_workflow(
        CREATE_FROM_PROMPT_WORKFLOW_PATH,
        [
            (BEGIN_PROMPT_TEMPLATES, END_PROMPT_TEMPLATES, prompt_template_slugs, False),
        ],
    )


if __name__ == "__main__":
    main()
