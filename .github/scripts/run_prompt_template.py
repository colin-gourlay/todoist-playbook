#!/usr/bin/env python3
"""
Generate enriched Todoist task content via GitHub Copilot and create a project.

Environment variables
---------------------
TODOIST_API_TOKEN  – Todoist personal API token (required)
GITHUB_TOKEN       – GitHub token with models:read scope (required)
PROMPT_TEMPLATE    – Slug of the prompt template folder, e.g. task-enrichment (required)
TASK_TITLE         – Short task title supplied by the user (required)
CONTEXT            – Optional background / constraints text
PRIORITY           – urgent | high | medium | normal  (default: normal)
PROJECT_NAME       – Override the Todoist project name (default: generated TITLE)
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request

TODOIST_API_BASE = "https://api.todoist.com/api/v1"
# GitHub Models API is hosted on Azure infrastructure; authentication uses GITHUB_TOKEN.
GITHUB_MODELS_URL = "https://models.inference.ai.azure.com/chat/completions"
COPILOT_MODEL = "gpt-4o-mini"

# Map user-facing priority labels → Todoist API priority values
_PRIORITY_MAP = {"urgent": 4, "high": 3, "medium": 2, "normal": 1}

# Maximum characters to display per task/subtask line in run output
_MAX_DISPLAY_LENGTH = 80


# ---------------------------------------------------------------------------
# Prompt template helpers
# ---------------------------------------------------------------------------


def read_prompt_template(slug: str) -> str:
    """Read and return the prompt text from prompt-templates/{slug}/prompt.md.

    The prompt is extracted from the fenced code block inside the ``## Prompt``
    section of the Markdown file.
    """
    prompt_path = os.path.join("prompt-templates", slug, "prompt.md")
    if not os.path.exists(prompt_path):
        print(f"❌ Prompt template not found: {prompt_path}", file=sys.stderr)
        sys.exit(1)

    with open(prompt_path, encoding="utf-8") as fh:
        content = fh.read()

    match = re.search(r"## Prompt\s*\n+```[^\n]*\n(.*?)```", content, re.DOTALL)
    if not match:
        print(
            "❌ Could not find a fenced code block in the '## Prompt' section of "
            f"{prompt_path}",
            file=sys.stderr,
        )
        sys.exit(1)

    return match.group(1).strip()


def fill_placeholders(prompt: str, task_title: str, context: str, priority: str) -> str:
    """Replace ``{{placeholders}}`` with the supplied values."""
    prompt = prompt.replace("{{task_title}}", task_title)
    prompt = prompt.replace("{{context}}", context if context else "Not provided")
    prompt = prompt.replace("{{priority}}", priority)
    return prompt


# ---------------------------------------------------------------------------
# GitHub Copilot (Models API)
# ---------------------------------------------------------------------------


def call_copilot(github_token: str, prompt: str) -> str:
    """Send the filled prompt to GitHub Copilot and return the response text."""
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Content-Type": "application/json",
    }
    data = {
        "model": COPILOT_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
    }
    body = json.dumps(data).encode()
    req = urllib.request.Request(
        GITHUB_MODELS_URL, data=body, headers=headers, method="POST"
    )
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            return result["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as exc:
        print(
            f"❌ GitHub Copilot API error {exc.code}: {exc.read().decode()}",
            file=sys.stderr,
        )
        sys.exit(1)


# ---------------------------------------------------------------------------
# Output parser
# ---------------------------------------------------------------------------


def parse_output(output: str) -> tuple[str, str, list[str]]:
    """Parse TITLE, DESCRIPTION, and SUBTASKS from the model's response.

    The model is expected to return a response in the following structure::

        TITLE: <one-line task title>

        DESCRIPTION:
        ## Goal
        <goal sentence>

        ## Steps
        1. <step>
        ...

        ## Notes          ← optional
        <notes>

        SUBTASKS:         ← optional
        - <subtask>
        ...

    Returns
    -------
    title : str
        The parsed task title (empty string if not found).
    description : str
        The Markdown description block (empty string if not found).
    subtasks : list[str]
        Ordered list of sub-task content strings (empty list if none).
    """
    # TITLE: single line after the label
    title_match = re.search(r"^TITLE:\s*(.+)$", output, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else ""

    # DESCRIPTION: everything between the DESCRIPTION: label and SUBTASKS (or end)
    desc_match = re.search(
        r"^DESCRIPTION:\s*\n(.*?)(?=^SUBTASKS|\Z)", output, re.DOTALL | re.MULTILINE
    )
    description = desc_match.group(1).strip() if desc_match else ""

    # SUBTASKS: optional bullet list
    subtasks: list[str] = []
    subtasks_match = re.search(r"^SUBTASKS[^\n]*\n(.*)", output, re.DOTALL | re.MULTILINE)
    if subtasks_match:
        for line in subtasks_match.group(1).splitlines():
            item = line.strip().lstrip("-•* ").strip()
            if item:
                subtasks.append(item)

    return title, description, subtasks


# ---------------------------------------------------------------------------
# Todoist API helper
# ---------------------------------------------------------------------------


def todoist_post(endpoint: str, token: str, data: dict) -> dict:
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
        print(
            f"❌ Todoist API error {exc.code}: {exc.read().decode()}", file=sys.stderr
        )
        sys.exit(1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    todoist_token = os.environ.get("TODOIST_API_TOKEN", "").strip()
    if not todoist_token:
        print("❌ TODOIST_API_TOKEN is not set.", file=sys.stderr)
        sys.exit(1)

    github_token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not github_token:
        print("❌ GITHUB_TOKEN is not set.", file=sys.stderr)
        sys.exit(1)

    prompt_slug = os.environ.get("PROMPT_TEMPLATE", "").strip()
    if not prompt_slug:
        print("❌ PROMPT_TEMPLATE is not set.", file=sys.stderr)
        sys.exit(1)

    task_title = os.environ.get("TASK_TITLE", "").strip()
    if not task_title:
        print("❌ TASK_TITLE is not set.", file=sys.stderr)
        sys.exit(1)

    context = os.environ.get("CONTEXT", "").strip()
    priority_label = os.environ.get("PRIORITY", "normal").strip().lower()
    if not priority_label:
        priority_label = "normal"
    if priority_label not in _PRIORITY_MAP:
        print(
            f"❌ Invalid PRIORITY '{priority_label}'. "
            f"Must be one of: {', '.join(_PRIORITY_MAP)}",
            file=sys.stderr,
        )
        sys.exit(1)

    project_name_override = os.environ.get("PROJECT_NAME", "").strip()

    print(f"🤖 Prompt template : {prompt_slug}")
    print(f"📝 Task title      : {task_title}")
    print(f"📋 Priority        : {priority_label}")
    print()

    # Build and fill the prompt
    raw_prompt = read_prompt_template(prompt_slug)
    filled_prompt = fill_placeholders(raw_prompt, task_title, context, priority_label)

    print("🔄 Generating content via GitHub Copilot...")
    output = call_copilot(github_token, filled_prompt)
    print("✅ Content generated")
    print()

    # Parse the generated output
    title, description, subtasks = parse_output(output)
    if not title:
        print(
            "❌ Could not parse a TITLE from the model output. Raw output:\n",
            file=sys.stderr,
        )
        print(output, file=sys.stderr)
        sys.exit(1)

    project_name = project_name_override or title

    print(f"📁 Project  : {project_name}")
    print(f"📌 Title    : {title}")
    if subtasks:
        print(f"📎 Subtasks : {len(subtasks)}")
    print()

    # Create the Todoist project
    project = todoist_post("projects", todoist_token, {"name": project_name})
    project_id = project["id"]
    print(f"✅ Project created (id={project_id})")

    # Create the main task with the generated description
    todoist_priority = _PRIORITY_MAP[priority_label]
    task_data: dict = {
        "content": title,
        "project_id": project_id,
        "priority": todoist_priority,
    }
    if description:
        task_data["description"] = description

    main_task = todoist_post("tasks", todoist_token, task_data)
    main_task_id = main_task["id"]
    print(f"  ✓ {title[:_MAX_DISPLAY_LENGTH]}")

    # Create sub-tasks nested under the main task
    for subtask_content in subtasks:
        subtask_data = {
            "content": subtask_content,
            "project_id": project_id,
            "parent_id": main_task_id,
            "priority": todoist_priority,
        }
        todoist_post("tasks", todoist_token, subtask_data)
        print(f"    ✓ {subtask_content[:_MAX_DISPLAY_LENGTH]}")

    print()
    print(f"🎉 Done! Project '{project_name}' is ready in Todoist.")


if __name__ == "__main__":
    main()
