#!/usr/bin/env python3
"""Fetch Todoist projects and sync the parent_project options in create-todoist-project.yml.

Reads all projects from the Todoist REST API and rewrites the options list
between the BEGIN_TODOIST_PROJECTS / END_TODOIST_PROJECTS sentinel comments in
the workflow file.  Run the "Sync Todoist Project List" GitHub Actions workflow
to keep the dropdown current.
"""

import json
import os
import sys
import urllib.error
import urllib.request

TODOIST_API_BASE = "https://api.todoist.com/api/v1"
WORKFLOW_PATH = ".github/workflows/create-todoist-project.yml"

# These markers delimit the auto-generated options block inside the YAML file.
BEGIN_MARKER = "          # BEGIN_TODOIST_PROJECTS (auto-updated by the sync-todoist-projects workflow)"
END_MARKER = "          # END_TODOIST_PROJECTS"


def fetch_projects(token):
    """Return all projects from the Todoist REST API."""
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


def main():
    token = os.environ.get("TODOIST_API_TOKEN", "").strip()
    if not token:
        print("❌ TODOIST_API_TOKEN is not set.", file=sys.stderr)
        sys.exit(1)

    projects = fetch_projects(token)

    # Exclude the Inbox project (`is_inbox_project` is the field name in the
    # Todoist REST API v1 project resource) and sort the rest alphabetically.
    project_names = sorted(
        p["name"] for p in projects if isinstance(p, dict) and not p.get("is_inbox_project", False)
    )

    print(f"📋 Found {len(project_names)} Todoist project(s)")
    for name in project_names:
        print(f"  - {name}")

    with open(WORKFLOW_PATH, encoding="utf-8") as f:
        lines = f.readlines()

    # Locate the sentinel markers.
    begin_idx = end_idx = None
    for i, line in enumerate(lines):
        if line.rstrip("\n") == BEGIN_MARKER:
            begin_idx = i
        elif line.rstrip("\n") == END_MARKER:
            end_idx = i
            break

    if begin_idx is None or end_idx is None:
        print(
            f"❌ Could not find sentinel markers in {WORKFLOW_PATH}.\n"
            "Expected lines:\n"
            f"  {BEGIN_MARKER}\n"
            f"  {END_MARKER}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Build the replacement block (inclusive of the sentinel lines).
    new_block = [BEGIN_MARKER + "\n", "          - ''\n"]
    for name in project_names:
        new_block.append(f"          - {yaml_single_quote(name)}\n")
    new_block.append(END_MARKER + "\n")

    # Splice the new block into the file content.
    new_lines = lines[:begin_idx] + new_block + lines[end_idx + 1 :]

    with open(WORKFLOW_PATH, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print(f"✅ Updated {WORKFLOW_PATH}")


if __name__ == "__main__":
    main()
