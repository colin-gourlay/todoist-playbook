#!/usr/bin/env python3
"""Create a Todoist project from a hosted template CSV via the Todoist REST API v2."""

import csv
import json
import os
import sys
import urllib.error
import urllib.request

TODOIST_API_BASE = "https://api.todoist.com/rest/v2"

# CSV priority 1 = urgent (p1) → API priority 4; CSV 4 = normal → API 1
_PRIORITY_MAP = {"1": 4, "2": 3, "3": 2, "4": 1}


def api_post(endpoint, token, data):
    """POST to the Todoist REST API and return the parsed JSON response."""
    url = f"{TODOIST_API_BASE}/{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        print(f"❌ Todoist API error {exc.code}: {exc.read().decode()}", file=sys.stderr)
        sys.exit(1)


def read_project_name_from_meta(template_dir):
    """Return the 'name' field from meta.yml, or None if unavailable.

    meta.yml must use a simple 'name: value' format on a single line
    (as enforced by the validate-templates workflow).
    """
    meta_path = os.path.join(template_dir, "meta.yml")
    if not os.path.exists(meta_path):
        return None
    with open(meta_path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("name:"):
                return line.split(":", 1)[1].strip().strip("\"'")
    return None


def main():
    token = os.environ.get("TODOIST_API_TOKEN", "").strip()
    if not token:
        print("❌ TODOIST_API_TOKEN secret is not set.", file=sys.stderr)
        sys.exit(1)

    template_slug = os.environ.get("TEMPLATE", "").strip()
    if not template_slug:
        print("❌ TEMPLATE input is not set.", file=sys.stderr)
        sys.exit(1)

    template_dir = os.path.join("templates", template_slug)
    csv_path = os.path.join(template_dir, "template.csv")

    if not os.path.exists(csv_path):
        print(f"❌ Template CSV not found: {csv_path}", file=sys.stderr)
        sys.exit(1)

    # Resolve the project name: explicit input takes priority over meta.yml
    project_name = os.environ.get("PROJECT_NAME", "").strip()
    if not project_name:
        project_name = read_project_name_from_meta(template_dir)
    if not project_name:
        project_name = template_slug.replace("-", " ").title()

    print(f"📋 Template : {template_slug}")
    print(f"📁 Project  : {project_name}")
    print()

    # Create the Todoist project
    project = api_post("projects", token, {"name": project_name})
    project_id = project["id"]
    print(f"✅ Project created (id={project_id})")

    current_section_id = None
    # Stack of (indent_level, task_id) used to resolve parent tasks for subtasks
    indent_stack = []

    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_type = row.get("TYPE", "").strip()
            content = row.get("CONTENT", "").strip()

            if not content:
                continue

            if row_type == "section":
                section = api_post(
                    "sections",
                    token,
                    {"project_id": project_id, "name": content},
                )
                current_section_id = section["id"]
                indent_stack = []
                print(f"  📂 {content}")

            elif row_type == "task":
                try:
                    indent = int(row.get("INDENT", "") or 1)
                except ValueError:
                    indent = 1
                priority = _PRIORITY_MAP.get(row.get("PRIORITY", "").strip(), 1)

                # Pop stack entries at the same or deeper indent level
                while indent_stack and indent_stack[-1][0] >= indent:
                    indent_stack.pop()

                parent_id = indent_stack[-1][1] if indent_stack else None

                task_data = {
                    "content": content,
                    "project_id": project_id,
                    "priority": priority,
                }
                if current_section_id:
                    task_data["section_id"] = current_section_id
                if parent_id:
                    task_data["parent_id"] = parent_id

                task = api_post("tasks", token, task_data)
                indent_stack.append((indent, task["id"]))
                prefix = "  " * indent
                print(f"  {prefix}✓ {content[:80]}")

    print()
    print(f"🎉 Done! Project '{project_name}' is ready in Todoist.")


if __name__ == "__main__":
    main()
