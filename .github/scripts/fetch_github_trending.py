#!/usr/bin/env python3
"""Fetch trending GitHub repositories and push them as Todoist tasks.

Environment variables
---------------------
TODOIST_API_TOKEN  – Todoist personal API token (required)
PROJECT_NAME       – Override the default project name (optional)
"""

import datetime
import html as html_module
import json
import os
import re
import sys
import urllib.error
import urllib.request

TODOIST_API_BASE = "https://api.todoist.com/api/v1"
GITHUB_TRENDING_URL = "https://github.com/trending"

# (github_since_param, section_label, todoist_due_string_or_None)
_PERIODS = [
    ("daily", "Trending (Today)", "today"),
    ("weekly", "Trending (This Week)", None),
    ("monthly", "Trending (This Month)", None),
]

_READ_LATER_LABEL = "read-later"

# Todoist API priority for read-later discovery tasks: 2 = medium (p3 in Todoist UI).
# Range: 1 (no priority / p4) → 4 (urgent / p1).
_TASK_PRIORITY = 2


# ---------------------------------------------------------------------------
# GitHub Trending scraper
# ---------------------------------------------------------------------------


def fetch_trending(since: str) -> list[dict]:
    """Fetch and parse trending repos for the given period.

    Parameters
    ----------
    since:
        One of ``daily``, ``weekly``, or ``monthly`` — passed verbatim as the
        ``?since=`` query parameter on the GitHub Trending page.

    Returns
    -------
    list of dicts with keys ``slug``, ``url``, and ``description``.
    """
    url = f"{GITHUB_TRENDING_URL}?since={since}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; todoist-playbook-trending-bot/1.0; "
            "+https://github.com/colin-gourlay/todoist-playbook)"
        )
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            body = response.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        print(
            f"❌ Failed to fetch GitHub Trending (since={since}): {exc}",
            file=sys.stderr,
        )
        sys.exit(1)

    return _parse_trending_html(body)


def _strip_tags(text: str) -> str:
    """Remove HTML tags and normalise whitespace."""
    text = re.sub(r"<[^>]+>", "", text)
    return " ".join(text.split())


def _parse_trending_html(body: str) -> list[dict]:
    """Extract repo metadata from the GitHub Trending page HTML.

    The page renders each repository as an ``<article class="Box-row">``
    element. This parser uses lightweight regex extraction rather than a
    full HTML parser so there are no extra dependencies.

    Note: this approach is inherently dependent on GitHub's HTML structure.
    If the trending page layout changes, the regex patterns below may need
    updating. A return value of an empty list indicates either no trending
    repos for the period or a parsing failure.
    """
    repos: list[dict] = []

    article_re = re.compile(
        r'<article[^>]*class="[^"]*Box-row[^"]*"[^>]*>(.*?)</article>',
        re.DOTALL,
    )

    for article_match in article_re.finditer(body):
        article = article_match.group(1)

        # Repo slug and URL — look for the <a href="/owner/repo"> inside an <h2>
        name_match = re.search(
            r'<h2[^>]*>\s*<a\s+href="/([^/"?#][^"?#]*)"',
            article,
        )
        if not name_match:
            continue

        slug = html_module.unescape(name_match.group(1).strip())
        # Normalise spacing that GitHub sometimes renders as " owner / repo "
        slug = re.sub(r"\s*/\s*", "/", slug)
        repo_url = f"https://github.com/{slug}"

        # Description — the <p> element with class col-9
        desc_match = re.search(
            r'<p[^>]*class="[^"]*col-9[^"]*"[^>]*>(.*?)</p>',
            article,
            re.DOTALL,
        )
        description = ""
        if desc_match:
            description = _strip_tags(html_module.unescape(desc_match.group(1)))

        repos.append(
            {
                "slug": slug,
                "url": repo_url,
                "description": description,
            }
        )

    return repos


# ---------------------------------------------------------------------------
# Todoist API helpers
# ---------------------------------------------------------------------------


def _todoist_post(endpoint: str, token: str, data: dict) -> dict:
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
            f"❌ Todoist API error {exc.code}: {exc.read().decode()}",
            file=sys.stderr,
        )
        sys.exit(1)


# ---------------------------------------------------------------------------
# Task content builder
# ---------------------------------------------------------------------------


def _build_task_content(repo: dict) -> str:
    """Build the task content string: ``slug — url[ — description]``."""
    parts = [repo["slug"], repo["url"]]
    if repo["description"]:
        parts.append(repo["description"])
    return " — ".join(parts)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    token = os.environ.get("TODOIST_API_TOKEN", "").strip()
    if not token:
        print("❌ TODOIST_API_TOKEN secret is not set.", file=sys.stderr)
        sys.exit(1)

    today = datetime.date.today().isoformat()
    project_name = (
        os.environ.get("PROJECT_NAME", "").strip() or f"GitHub Trending — {today}"
    )

    print(f"📁 Project  : {project_name}")
    print()

    project = _todoist_post("projects", token, {"name": project_name})
    project_id = project["id"]
    print(f"✅ Project created (id={project_id})")

    for since, section_label, due_string in _PERIODS:
        print(f"\n🔍 Fetching {section_label}...")
        repos = fetch_trending(since)
        if not repos:
            print(f"  ⚠️  No repositories found for {section_label}")
            continue
        print(f"  Found {len(repos)} repositories")

        section = _todoist_post(
            "sections",
            token,
            {"project_id": project_id, "name": section_label},
        )
        section_id = section["id"]
        print(f"  📂 {section_label}")

        for repo in repos:
            content = _build_task_content(repo)
            task_data: dict = {
                "content": content,
                "project_id": project_id,
                "section_id": section_id,
                # Todoist REST API v1 accepts label names directly as strings.
                # If the label does not yet exist in Todoist it will be created.
                "labels": [_READ_LATER_LABEL],
                "priority": _TASK_PRIORITY,
            }
            if due_string:
                task_data["due_string"] = due_string
            _todoist_post("tasks", token, task_data)
            print(f"    ✓ {content[:100]}")

    print()
    print(f"🎉 Done! Project '{project_name}' is ready in Todoist.")


if __name__ == "__main__":
    main()
