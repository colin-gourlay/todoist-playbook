#!/usr/bin/env python3
"""Fetch trending GitHub repositories and push them as Todoist tasks.

Environment variables
---------------------
TODOIST_API_TOKEN  – Todoist personal API token (required)
PROJECT_NAME       – Override the default project name (optional)
LANGUAGES          – Optional comma-separated GitHub Trending languages.
                     Leave blank or use "Any" for no filter.
"""

import datetime
import html as html_module
import json
import os
import re
import sys
import urllib.error
import urllib.parse
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


def fetch_trending(since: str, language: str | None = None) -> list[dict]:
    """Fetch and parse trending repos for the given period.

    Parameters
    ----------
    since:
        One of ``daily``, ``weekly``, or ``monthly`` — passed as
        the ``?since=`` query parameter.
    language:
        Optional GitHub Trending language name (for example ``Python`` or
        ``Bicep``). When ``None``, no language filter is applied.

    Returns
    -------
    list of dicts with keys ``slug``, ``url``, and ``description``.
    """
    query_params = {"since": since}
    if language:
        query_params["l"] = language
    url = f"{GITHUB_TRENDING_URL}?{urllib.parse.urlencode(query_params)}"
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
            f"❌ Failed to fetch GitHub Trending (since={since}, language={language or 'Any'}): {exc}",
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
        r'<p[^>]*class="[^"]*col-9[^"]*"[^>]*>(.*?)</p>',
        re.DOTALL,
    )
    stars_re = re.compile(
        r'([0-9][0-9,]*)\s+stars\s+(today|this week|this month)',
        re.IGNORECASE,
    )
    total_stars_re = re.compile(
        r'/stargazers"[^>]*>.*?</svg>\s*([0-9][0-9,]*)\s*</a>',
        re.IGNORECASE | re.DOTALL,
    )
    forks_re = re.compile(
        r'/forks"[^>]*>.*?</svg>\s*([0-9][0-9,]*)\s*</a>',
        re.IGNORECASE | re.DOTALL,
    )
    language_re = re.compile(
        r'<span[^>]*itemprop="programmingLanguage"[^>]*>(.*?)</span>',
        re.IGNORECASE | re.DOTALL,
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
        if m:
            return _strip_tags(html_module.unescape(m.group(1)))
        # Fallback when class names change: pick the first non-empty paragraph.
        fallback = re.search(r'<p[^>]*>(.*?)</p>', fragment, re.DOTALL)
        if fallback:
            return _strip_tags(html_module.unescape(fallback.group(1)))
        return ""

    def _extract_stars_text(fragment: str) -> str:
        plain = _strip_tags(html_module.unescape(fragment))
        m = stars_re.search(plain)
        if not m:
            return ""
        number = m.group(1)
        period = m.group(2).lower()
        return f"{number} stars {period}"

    def _extract_total_stars(fragment: str) -> str:
        # Prefer the value adjacent to GitHub's stargazer metric in card markup.
        m = total_stars_re.search(fragment)
        if m:
            return m.group(1)

        # Fallback for markup shifts: infer from plain text where "star" appears.
        plain = _strip_tags(html_module.unescape(fragment))
        fallback = re.search(r'star\s*([0-9][0-9,]*)', plain, re.IGNORECASE)
        if fallback:
            return fallback.group(1)
        return ""

    def _extract_forks(fragment: str) -> str:
        m = forks_re.search(fragment)
        if m:
            return m.group(1)
        plain = _strip_tags(html_module.unescape(fragment))
        fallback = re.search(r'fork\s*([0-9][0-9,]*)', plain, re.IGNORECASE)
        if fallback:
            return fallback.group(1)
        return ""

    def _extract_language(fragment: str) -> str:
        m = language_re.search(fragment)
        if not m:
            return ""
        return _strip_tags(html_module.unescape(m.group(1)))

    def _add(
        slug: str,
        url: str,
        description: str,
        stars_text: str,
        total_stars: str,
        forks: str,
        language: str,
    ) -> None:
        if slug not in seen_slugs:
            seen_slugs.add(slug)
            repos.append(
                {
                    "slug": slug,
                    "url": url,
                    "description": description,
                    "stars_text": stars_text,
                    "total_stars": total_stars,
                    "forks": forks,
                    "language": language,
                }
            )

    # Strategy 1 — article-based (matches historical and many current layouts).
    article_re = re.compile(r'<article\b[^>]*>(.*?)</article>', re.DOTALL)
    for article_match in article_re.finditer(body):
        article = article_match.group(1)
        result = _extract_slug_and_url(article)
        if result:
            slug, url = result
            _add(
                slug,
                url,
                _extract_description(article),
                _extract_stars_text(article),
                _extract_total_stars(article),
                _extract_forks(article),
                _extract_language(article),
            )

    if repos:
        return repos

    # Strategy 2 — heading-based fallback for redesigned layouts.
    # Split on <h2 tags so we can associate the nearest <p> with each heading.
    for chunk in re.split(r'(?=<h2\b)', body):
        result = _extract_slug_and_url(chunk)
        if result:
            slug, url = result
            _add(
                slug,
                url,
                _extract_description(chunk),
                _extract_stars_text(chunk),
                _extract_total_stars(chunk),
                _extract_forks(chunk),
                _extract_language(chunk),
            )

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
    """Build task title in a GitHub-card-like metric order."""
    metrics: list[str] = []
    if repo.get("language"):
        metrics.append(repo["language"])
    if repo.get("total_stars"):
        metrics.append(f"⭐ {repo['total_stars']}")
    if repo.get("forks"):
        metrics.append(f"🍴 {repo['forks']}")
    if repo.get("stars_text"):
        metrics.append(f"⭐ {repo['stars_text']}")

    if not metrics:
        return repo["slug"]
    return f"{repo['slug']} — {' • '.join(metrics)}"


def _build_task_description(repo: dict) -> str:
    """Build task description with blurb and source URL."""
    parts: list[str] = []
    if repo.get("description"):
        parts.append(repo["description"])
    parts.append(repo["url"])
    return "\n\n".join(parts)


def _parse_language_filters(raw: str) -> list[str]:
    """Parse comma-separated languages from workflow input.

    Returns an ordered unique list. Empty list means "Any".
    """
    if not raw.strip():
        return []

    parts = [p.strip() for p in raw.split(",") if p.strip()]
    if not parts:
        return []

    seen: set[str] = set()
    languages: list[str] = []
    for part in parts:
        if part.lower() == "any":
            continue
        key = part.casefold()
        if key in seen:
            continue
        seen.add(key)
        languages.append(part)
    return languages


def _build_project_name(base_name: str, today: str, languages: list[str]) -> str:
    """Build project name with optional language suffix."""
    language_suffix = f" ({', '.join(languages)})" if languages else ""

    if base_name:
        if languages:
            return f"{base_name}{language_suffix}"
        return base_name

    return f"GitHub Trending{language_suffix} — {today}"


def _fetch_for_languages(since: str, languages: list[str]) -> list[dict]:
    """Fetch and merge repos for one period across selected languages."""
    if not languages:
        return fetch_trending(since)

    merged: list[dict] = []
    seen_slugs: set[str] = set()

    for language in languages:
        repos = fetch_trending(since, language)
        for repo in repos:
            slug = repo.get("slug", "")
            if slug in seen_slugs:
                continue
            seen_slugs.add(slug)
            merged.append(repo)

    return merged


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    token = os.environ.get("TODOIST_API_TOKEN", "").strip()
    if not token:
        print("❌ TODOIST_API_TOKEN secret is not set.", file=sys.stderr)
        sys.exit(1)

    today = datetime.date.today().isoformat()
    project_name_input = os.environ.get("PROJECT_NAME", "").strip()
    languages = _parse_language_filters(os.environ.get("LANGUAGES", ""))
    project_name = _build_project_name(project_name_input, today, languages)

    language_summary = ", ".join(languages) if languages else "Any"

    print(f"📁 Project  : {project_name}")
    print(f"🧪 Languages: {language_summary}")
    print()

    project = _todoist_post("projects", token, {"name": project_name})
    project_id = project["id"]
    print(f"✅ Project created (id={project_id})")

    for since, section_label, due_string in _PERIODS:
        print(f"\n🔍 Fetching {section_label}...")
        repos = _fetch_for_languages(since, languages)
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
                "description": _build_task_description(repo),
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
