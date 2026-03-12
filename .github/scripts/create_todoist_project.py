#!/usr/bin/env python3
"""Create a Todoist project from a hosted template CSV via the Todoist API v1."""

import csv
import json
import os
import sys
import urllib.error
import urllib.request

TODOIST_API_BASE = "https://api.todoist.com/api/v1"

# CSV priority 1 = urgent (p1) → API priority 4; CSV 4 = normal → API 1
_PRIORITY_MAP = {"1": 4, "2": 3, "3": 2, "4": 1}

def _load_supported_project_colors():
    """Load supported Todoist color names from the shared project_colors.txt file."""
    colors_file = os.path.join(os.path.dirname(__file__), "project_colors.txt")
    with open(colors_file, encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


# Todoist color names loaded from the shared project_colors.txt file.
_SUPPORTED_PROJECT_COLORS = _load_supported_project_colors()


def api_get(endpoint, token):
    """GET from the Todoist REST API and return the parsed JSON response."""
    url = f"{TODOIST_API_BASE.rstrip('/')}/{endpoint.lstrip('/')}"
    headers = {"Authorization": f"Bearer {token}"}
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        print(f"❌ Todoist API error {exc.code}: {exc.read().decode()}", file=sys.stderr)
        sys.exit(1)


def api_post(endpoint, token, data):
    """POST to the Todoist REST API and return the parsed JSON response."""
    url = f"{TODOIST_API_BASE.rstrip('/')}/{endpoint.lstrip('/')}"
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


def resolve_parent_project_id(parent_name, token):
    """Look up a Todoist project by name (case-insensitive) and return its ID.

    Exits with an error if the name is not found or matches more than one project.
    """
    projects = api_get("projects", token)
    name_lower = parent_name.lower()
    matches = [p for p in projects if p.get("name", "").lower() == name_lower]
    if not matches:
        print(
            f"❌ No Todoist project found with name '{parent_name}'. "
            "Check the name and try again.",
            file=sys.stderr,
        )
        sys.exit(1)
    if len(matches) > 1:
        ids = ", ".join(p["id"] for p in matches)
        print(
            f"❌ Multiple Todoist projects match the name '{parent_name}' (ids: {ids}). "
            "Rename one of them so the name is unique, then try again.",
            file=sys.stderr,
        )
        sys.exit(1)
    return matches[0]["id"]


def read_meta_value(template_dir, key):
    """Return a top-level scalar meta.yml value for the provided key, or None."""
    meta_path = os.path.join(template_dir, "meta.yml")
    if not os.path.exists(meta_path):
        return None
    with open(meta_path, encoding="utf-8") as f:
        for line in f:
            if line.startswith(f"{key}:"):
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
        project_name = read_meta_value(template_dir, "name")
    if not project_name:
        project_name = template_slug.replace("-", " ").title()

    # Explicit workflow input takes priority over meta.yml
    project_color = os.environ.get("PROJECT_COLOR", "").strip() or read_meta_value(template_dir, "project_color")
    if project_color and project_color not in _SUPPORTED_PROJECT_COLORS:
        allowed = ", ".join(sorted(_SUPPORTED_PROJECT_COLORS))
        print(
            f"❌ Invalid project_color '{project_color}'. Allowed values: {allowed}",
            file=sys.stderr,
        )
        sys.exit(1)

    is_favorite = os.environ.get("IS_FAVORITE", "").strip().lower() == "yes"

    parent_project_name = os.environ.get("PARENT_PROJECT", "").strip()
    parent_project_id = None
    if parent_project_name:
        parent_project_id = resolve_parent_project_id(parent_project_name, token)

    print(f"📋 Template : {template_slug}")
    print(f"📁 Project  : {project_name}")
    if parent_project_name:
        print(f"🗂️  Parent   : {parent_project_name} (id={parent_project_id})")
    if project_color:
        print(f"🎨 Color    : {project_color}")
    if is_favorite:
        print(f"⭐ Favourite: yes")
    print()

    # Create the Todoist project
    project_data = {"name": project_name}
    if parent_project_id:
        project_data["parent_id"] = parent_project_id
    if project_color:
        project_data["color"] = project_color
    if is_favorite:
        project_data["is_favorite"] = True

    project = api_post("projects", token, project_data)
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
