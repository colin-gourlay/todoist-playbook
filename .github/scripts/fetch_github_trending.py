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

    Uses two strategies in sequence so the parser degrades gracefully when
    GitHub updates its HTML structure:

    1. Article-based: look for ``<article>`` elements that contain a repo
       link inside an ``<h2>``.  GitHub historically rendered each repo as
       ``<article class="Box-row">``, but the class name is intentionally
       not hard-coded so minor redesigns don't break this.

    2. Heading-based fallback: scan every ``<h2>`` that contains an
       ``<a href="/owner/repo">`` link.  This is more permissive but still
       requires a two-segment path, which filters out navigation links.

    Note: this approach is inherently dependent on GitHub's HTML structure.
    A return value of an empty list indicates either no trending repos for
    the period or a parsing failure.
    """
    repos: list[dict] = []
    seen_slugs: set[str] = set()

    # Compiled patterns reused across both strategies.
    # Use <a\b[^>]*\bhref= so that other attributes (e.g. data-hydro-click)
    # before href are tolerated.
    h2_link_re = re.compile(
        r'<h2[^>]*>.*?<a\b[^>]*\bhref="/([^/"?#][^"?#]*/[^"?#]+)"',
        re.DOTALL,
    )
    desc_re = re.compile(
        r'<p[^>]*>(.*?)</p>',
        re.DOTALL,
    )

    def _extract_slug_and_url(fragment: str) -> tuple[str, str] | None:
        m = h2_link_re.search(fragment)
        if not m:
            return None
        raw = html_module.unescape(m.group(1).strip())
        slug = re.sub(r"\s*/\s*", "/", raw)
        # Must be exactly owner/repo (two segments, no further slashes).
        if slug.count("/") != 1:
            return None
        return slug, f"https://github.com/{slug}"

    def _extract_description(fragment: str) -> str:
        m = desc_re.search(fragment)
        if not m:
            return ""
        return _strip_tags(html_module.unescape(m.group(1)))

    def _add(slug: str, url: str, description: str) -> None:
        if slug not in seen_slugs:
            seen_slugs.add(slug)
            repos.append({"slug": slug, "url": url, "description": description})

    # Strategy 1 — article-based (matches historical and many current layouts).
    article_re = re.compile(r'<article\b[^>]*>(.*?)</article>', re.DOTALL)
    for article_match in article_re.finditer(body):
        article = article_match.group(1)
        result = _extract_slug_and_url(article)
        if result:
            slug, url = result
            _add(slug, url, _extract_description(article))

    if repos:
        return repos

    # Strategy 2 — heading-based fallback for redesigned layouts.
    # Split on <h2 tags so we can associate the nearest <p> with each heading.
    for chunk in re.split(r'(?=<h2\b)', body):
        result = _extract_slug_and_url(chunk)
        if result:
            slug, url = result
            _add(slug, url, _extract_description(chunk))

    if not repos:
        print(
            "⚠️  HTML parser found no repositories. GitHub may have changed "
            "its page structure. Raw HTML length: "
            f"{len(body)} chars. First 500 chars:\n{body[:500]}",
            file=sys.stderr,
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
