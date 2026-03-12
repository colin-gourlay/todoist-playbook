#!/usr/bin/env python3
"""
Create a Todoist project from a hosted template CSV via the Todoist MCP server.

Uses the Model Context Protocol (MCP) Streamable HTTP transport to connect to
https://ai.todoist.net/mcp and call tools for creating projects, sections, and
tasks — without requiring a direct Todoist REST API connection.

Required environment variables:
  TODOIST_API_TOKEN  — Todoist personal API token

  TEMPLATE           — Template slug (e.g. weekly-review)

Optional environment variables:
  PROJECT_NAME       — Override the project name from meta.yml
  PROJECT_COLOR      — Todoist colour name (e.g. red, blue)
  IS_FAVORITE        — Mark the project as a favourite (yes / no)
"""

import csv
import json
import os
import sys
import urllib.error
import urllib.request

MCP_ENDPOINT = "https://ai.todoist.net/mcp"
MCP_PROTOCOL_VERSION = "2024-11-05"

# CSV priority 1 = urgent (p1) → API priority 4; CSV 4 = normal → API 1
_PRIORITY_MAP = {"1": 4, "2": 3, "3": 2, "4": 1}


def _load_supported_project_colors():
    """Load supported Todoist color names from the shared project_colors.txt file."""
    colors_file = os.path.join(os.path.dirname(__file__), "project_colors.txt")
    with open(colors_file, encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


_SUPPORTED_PROJECT_COLORS = _load_supported_project_colors()


class MCPClient:
    """Minimal MCP Streamable HTTP client (stdlib only)."""

    def __init__(self, endpoint: str, token: str) -> None:
        self.endpoint = endpoint
        self.token = token
        self.session_id: str | None = None
        self._request_id = 0

    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id

    def _post(self, body: dict) -> dict | None:
        """POST a JSON-RPC message to the MCP endpoint and return the response."""
        data = json.dumps(body).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json, text/event-stream",
        }
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id

        req = urllib.request.Request(
            self.endpoint, data=data, headers=headers, method="POST"
        )
        try:
            with urllib.request.urlopen(req) as resp:
                session_header = resp.headers.get("Mcp-Session-Id")
                if session_header:
                    self.session_id = session_header

                content_type = resp.headers.get("Content-Type", "")
                raw = resp.read().decode("utf-8")

                if "text/event-stream" in content_type:
                    return self._parse_sse(raw)
                if raw.strip():
                    return json.loads(raw)
                return None
        except urllib.error.HTTPError as exc:
            body_text = exc.read().decode("utf-8", errors="replace")
            print(
                f"❌ MCP request failed ({exc.code}): {body_text}",
                file=sys.stderr,
            )
            sys.exit(1)

    @staticmethod
    def _parse_sse(text: str) -> dict | None:
        """Return the last non-terminal data event from an SSE stream."""
        result = None
        for line in text.splitlines():
            if line.startswith("data: "):
                payload = line[6:].strip()
                if payload and payload != "[DONE]":
                    result = json.loads(payload)
        return result

    def initialize(self) -> dict | None:
        """Perform the MCP initialization handshake."""
        response = self._post(
            {
                "jsonrpc": "2.0",
                "id": self._next_id(),
                "method": "initialize",
                "params": {
                    "protocolVersion": MCP_PROTOCOL_VERSION,
                    "capabilities": {},
                    "clientInfo": {
                        "name": "todoist-playbook",
                        "version": "1.0.0",
                    },
                },
            }
        )
        if response and "error" in response:
            print(
                f"❌ MCP initialization error: {response['error']}",
                file=sys.stderr,
            )
            sys.exit(1)

        # Send the required initialized notification (no response expected)
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized"})
        return response

    def list_tools(self) -> list[dict]:
        """Return the list of tools advertised by the server."""
        response = self._post(
            {
                "jsonrpc": "2.0",
                "id": self._next_id(),
                "method": "tools/list",
                "params": {},
            }
        )
        if response and "error" in response:
            print(
                f"❌ MCP tools/list error: {response['error']}",
                file=sys.stderr,
            )
            sys.exit(1)
        if response and "result" in response:
            return response["result"].get("tools", [])
        return []

    def call_tool(self, name: str, arguments: dict) -> dict:
        """Call an MCP tool and return its result."""
        response = self._post(
            {
                "jsonrpc": "2.0",
                "id": self._next_id(),
                "method": "tools/call",
                "params": {"name": name, "arguments": arguments},
            }
        )
        if response and "error" in response:
            print(
                f"❌ MCP tool '{name}' error: {response['error']}",
                file=sys.stderr,
            )
            sys.exit(1)
        if response and "result" in response:
            return response["result"]
        return {}


def _find_tool(tools: list[dict], *candidates: str) -> str:
    """Return the first candidate tool name that the server actually exposes."""
    available = {t["name"] for t in tools}
    for name in candidates:
        if name in available:
            return name
    all_names = ", ".join(sorted(available)) or "(none)"
    print(
        f"❌ None of the expected tool names {list(candidates)} were found.\n"
        f"   Available tools: {all_names}",
        file=sys.stderr,
    )
    sys.exit(1)


def _extract_id(result: dict, *keys: str) -> str:
    """Extract the ID field from a tool result, trying multiple key names."""
    # Result may be nested under a key matching one of the tool output fields
    for key in keys:
        value = result.get(key)
        if isinstance(value, dict):
            id_val = value.get("id")
            if id_val:
                return str(id_val)
        if isinstance(value, str) and value:
            return value
    # Flat result
    id_val = result.get("id")
    if id_val:
        return str(id_val)
    print(
        f"❌ Could not extract ID from tool result: {json.dumps(result)}",
        file=sys.stderr,
    )
    sys.exit(1)


def read_meta_value(template_dir: str, key: str) -> str | None:
    """Return a top-level scalar meta.yml value for the provided key, or None."""
    meta_path = os.path.join(template_dir, "meta.yml")
    if not os.path.exists(meta_path):
        return None
    with open(meta_path, encoding="utf-8") as f:
        for line in f:
            if line.startswith(f"{key}:"):
                return line.split(":", 1)[1].strip().strip("\"'")
    return None


def main() -> None:
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

    # Resolve project name: explicit input > meta.yml > slugified name
    project_name = os.environ.get("PROJECT_NAME", "").strip()
    if not project_name:
        project_name = read_meta_value(template_dir, "name")
    if not project_name:
        project_name = template_slug.replace("-", " ").title()

    # Resolve project color
    project_color = (
        os.environ.get("PROJECT_COLOR", "").strip()
        or read_meta_value(template_dir, "project_color")
    )
    if project_color and project_color not in _SUPPORTED_PROJECT_COLORS:
        allowed = ", ".join(sorted(_SUPPORTED_PROJECT_COLORS))
        print(
            f"❌ Invalid project_color '{project_color}'. Allowed values: {allowed}",
            file=sys.stderr,
        )
        sys.exit(1)

    is_favorite = os.environ.get("IS_FAVORITE", "").strip().lower() == "yes"

    print(f"📋 Template : {template_slug}")
    print(f"📁 Project  : {project_name}")
    if project_color:
        print(f"🎨 Color    : {project_color}")
    if is_favorite:
        print("⭐ Favourite: yes")
    print()

    # ── Initialise MCP connection ─────────────────────────────────────────────
    client = MCPClient(MCP_ENDPOINT, token)
    print(f"🔌 Connecting to MCP server: {MCP_ENDPOINT}")
    client.initialize()

    tools = client.list_tools()
    tool_names = [t["name"] for t in tools]
    print(f"🛠  Available tools: {', '.join(tool_names) or '(none)'}")
    print()

    # Discover the tool names the server actually exposes
    tool_create_project = _find_tool(
        tools,
        "create_project",
        "todoist_create_project",
        "projects_create",
    )
    tool_create_section = _find_tool(
        tools,
        "create_section",
        "todoist_create_section",
        "sections_create",
    )
    tool_create_task = _find_tool(
        tools,
        "create_task",
        "todoist_create_task",
        "tasks_create",
        "add_task",
    )

    # ── Create project ────────────────────────────────────────────────────────
    project_args: dict = {"name": project_name}
    if project_color:
        project_args["color"] = project_color
    if is_favorite:
        project_args["is_favorite"] = True

    project_result = client.call_tool(tool_create_project, project_args)
    project_id = _extract_id(project_result, "project")
    print(f"✅ Project created (id={project_id})")

    # ── Create sections and tasks from the CSV ────────────────────────────────
    current_section_id: str | None = None
    # Stack of (indent_level, task_id) for resolving parent tasks
    indent_stack: list[tuple[int, str]] = []

    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_type = row.get("TYPE", "").strip()
            content = row.get("CONTENT", "").strip()

            if not content:
                continue

            if row_type == "section":
                section_result = client.call_tool(
                    tool_create_section,
                    {"project_id": project_id, "name": content},
                )
                current_section_id = _extract_id(section_result, "section")
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

                task_args: dict = {
                    "content": content,
                    "project_id": project_id,
                    "priority": priority,
                }
                if current_section_id:
                    task_args["section_id"] = current_section_id
                if parent_id:
                    task_args["parent_id"] = parent_id

                task_result = client.call_tool(tool_create_task, task_args)
                task_id = _extract_id(task_result, "task")
                indent_stack.append((indent, task_id))
                prefix = "  " * indent
                print(f"  {prefix}✓ {content[:80]}")

    print()
    print(f"🎉 Done! Project '{project_name}' is ready in Todoist.")


if __name__ == "__main__":
    main()
