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
from pathlib import Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

TODOIST_API_BASE = "https://api.todoist.com/api/v1"
TODOIST_SYNC_API_BASE = "https://api.todoist.com/sync/v9"
GITHUB_TRENDING_URL = "https://github.com/trending"

# (github_since_param, section_label, todoist_due_string_or_None)
_PERIODS = [
    ("daily", "Trending (Today)", "today"),
    ("weekly", "Trending (This Week)", None),
    ("monthly", "Trending (This Month)", None),
]

_READ_LATER_LABEL = "read-later"

_STATE_VERSION = 1
_DEFAULT_PROCESSED_SLUGS_FILE = Path(
    ".github/data/github-trending-processed-slugs.json"
)

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


def _todoist_get(
    endpoint: str,
    token: str,
    params: dict | None = None,
    base_url: str | None = None,
) -> dict | list | None:
    """GET from the Todoist REST API (or Sync API when *base_url* is given).

    Returns the parsed JSON response, or ``None`` on error so that callers
    can treat a failed lookup as an empty result without aborting the run.
    """
    base = (base_url or TODOIST_API_BASE).rstrip("/")
    url = f"{base}/{endpoint.lstrip('/')}"
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    headers = {"Authorization": f"Bearer {token}"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        print(
            f"⚠️  Todoist GET /{endpoint} returned {exc.code} — skipping",
            file=sys.stderr,
        )
        return None
    except urllib.error.URLError as exc:
        print(
            f"⚠️  Todoist GET /{endpoint} failed: {exc} — skipping",
            file=sys.stderr,
        )
        return None


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


def _to_kebab_label(value: str) -> str:
    """Convert a language name into a lowercase kebab-case Todoist label."""
    if not value:
        return ""

    # Expand common symbol-heavy language names before cleanup.
    normalised = (
        value.replace("+", " plus ")
        .replace("#", " sharp ")
        .replace(".", " dot ")
    )
    label = re.sub(r"[^a-z0-9]+", "-", normalised.lower()).strip("-")
    return re.sub(r"-+", "-", label)


def _extract_slug_from_content(content: str) -> str | None:
    """Extract the ``owner/repo`` slug from a task content string.

    Task content is formatted as ``owner/repo — Python • ⭐ 1,234`` or,
    for tasks without metrics, simply ``owner/repo``.  The slug is the
    segment before the first `` — `` separator.  It must contain exactly
    one forward slash and no whitespace to be considered valid.
    """
    name_part = content.split(" — ")[0].strip()
    if re.match(r"^[^/\s]+/[^/\s]+$", name_part):
        return name_part
    return None


def _normalise_slug(slug: str) -> str:
    """Return canonical slug format for dedup comparisons."""
    return slug.strip().lower()


def _is_valid_slug(slug: str) -> bool:
    """Validate ``owner/repo`` structure used in persisted state."""
    return bool(re.match(r"^[^/\s]+/[^/\s]+$", slug))


def _load_processed_state(path: Path) -> dict:
    """Load persisted processed slug state from disk.

    Returns a normalised state object, falling back to an empty structure when
    the file is missing or invalid.
    """
    empty_state = {"version": _STATE_VERSION, "updated_at": None, "slugs": {}}
    if not path.exists():
        return empty_state

    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        print(
            f"⚠️  Unable to read state file at {path}: {exc} — using empty state",
            file=sys.stderr,
        )
        return empty_state

    if not isinstance(data, dict):
        print(
            f"⚠️  Invalid state file format at {path} — using empty state",
            file=sys.stderr,
        )
        return empty_state

    raw_slugs = data.get("slugs", {})
    if not isinstance(raw_slugs, dict):
        print(
            f"⚠️  Invalid slug map in state file at {path} — using empty state",
            file=sys.stderr,
        )
        return empty_state

    cleaned_slugs: dict[str, dict] = {}
    for key, value in raw_slugs.items():
        if not isinstance(key, str):
            continue
        slug = _normalise_slug(key)
        if not _is_valid_slug(slug):
            continue
        if isinstance(value, dict):
            cleaned_slugs[slug] = value
        else:
            cleaned_slugs[slug] = {}

    return {
        "version": _STATE_VERSION,
        "updated_at": data.get("updated_at"),
        "slugs": cleaned_slugs,
    }


def _processed_slugs_from_state(state: dict) -> set[str]:
    """Extract processed slug set from in-memory state object."""
    slugs = state.get("slugs", {})
    if not isinstance(slugs, dict):
        return set()
    return set(slugs.keys())


def _mark_slug_in_state(
    state: dict,
    slug: str,
    created_at: str,
    project_name: str,
    section_label: str,
    languages: list[str],
) -> None:
    """Upsert slug metadata in persisted state."""
    slug_map = state.setdefault("slugs", {})
    if not isinstance(slug_map, dict):
        slug_map = {}
        state["slugs"] = slug_map

    entry = slug_map.get(slug)
    if not isinstance(entry, dict):
        entry = {}

    if "first_seen" not in entry:
        entry["first_seen"] = created_at
        entry["first_project"] = project_name
        entry["first_section"] = section_label
        entry["first_languages"] = languages

    entry["last_seen"] = created_at
    slug_map[slug] = entry


def _save_processed_state(path: Path, state: dict) -> None:
    """Persist state atomically so cross-run dedup remains durable."""
    path.parent.mkdir(parents=True, exist_ok=True)
    state["version"] = _STATE_VERSION
    state["updated_at"] = datetime.datetime.now(datetime.UTC).isoformat()

    temp_path = path.with_suffix(f"{path.suffix}.tmp")
    with temp_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(state, handle, indent=2, sort_keys=True)
        handle.write("\n")
    temp_path.replace(path)


def _fetch_processed_slugs(token: str) -> set[str]:
    """Return the set of ``owner/repo`` slugs already present in Todoist.

    Checks both active tasks (repos queued but not yet reviewed) and
    completed tasks (repos that have been reviewed and marked done) so
    that no repository is imported more than once.

    Active tasks are fetched via the Todoist REST API v1 (which returns a
    paginated response ``{"items": [...], "next_cursor": "..."}`` or a
    plain list depending on the API version).  Completed tasks are fetched
    via the Todoist Sync API v9, which exposes
    ``GET /sync/v9/items/completed/get_all`` — that endpoint is absent from
    the v1 REST API.

    If either API call fails the function silently skips that source and
    continues — the worst-case outcome is that some repos may be imported
    again rather than the whole run being aborted.
    """
    processed: set[str] = set()

    # Active read-later tasks (already queued for review).
    # The v1 REST API may return a paginated dict {"items": [...], "next_cursor": ...}
    # or a plain list — handle both.
    cursor: str | None = None
    active_count = 0
    while True:
        params: dict = {"label": _READ_LATER_LABEL}
        if cursor:
            params["cursor"] = cursor
        active = _todoist_get("tasks", token, params)

        tasks: list = []
        next_cursor: str | None = None
        if isinstance(active, list):
            tasks = active
        elif isinstance(active, dict):
            tasks = active.get("items", [])
            next_cursor = active.get("next_cursor")
        else:
            break

        for task in tasks:
            slug = _extract_slug_from_content(task.get("content", ""))
            if slug:
                processed.add(_normalise_slug(slug))
                active_count += 1

        if not next_cursor:
            break
        cursor = next_cursor

    if active_count:
        print(f"  ↳ {active_count} slug(s) from active tasks")

    # Completed tasks (already reviewed).
    # The v1 REST API does not expose a completed-tasks endpoint; use the
    # Sync API v9 instead, which supports offset-based pagination.
    offset = 0
    completed_count = 0
    while True:
        params = {"limit": 200, "offset": offset}
        result = _todoist_get(
            "items/completed/get_all", token, params, base_url=TODOIST_SYNC_API_BASE
        )
        if not isinstance(result, dict):
            break
        items = result.get("items", [])
        for task in items:
            slug = _extract_slug_from_content(task.get("content", ""))
            if slug:
                processed.add(_normalise_slug(slug))
                completed_count += 1
        if len(items) < 200:
            break
        offset += 200

    if completed_count:
        print(f"  ↳ {completed_count} slug(s) from completed tasks")

    return processed


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
    if base_name:
        language_suffix = f" ({', '.join(languages)})" if languages else ""
        if languages:
            return f"{base_name}{language_suffix}"
        return base_name

    language_segment = "-".join(_to_kebab_label(lang) for lang in languages if lang)
    if language_segment:
        return f"github-trending-{language_segment}-{today}"
    return f"github-trending-{today}"


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
    state_file_env = os.environ.get("GITHUB_TRENDING_STATE_FILE", "").strip()
    state_file = Path(state_file_env) if state_file_env else _DEFAULT_PROCESSED_SLUGS_FILE
    run_timestamp = datetime.datetime.now(datetime.UTC).isoformat()

    print(f"📁 Project  : {project_name}")
    print(f"🧪 Languages: {language_summary}")
    print(f"🧠 State    : {state_file}")
    print()

    state = _load_processed_state(state_file)
    persisted_slugs = _processed_slugs_from_state(state)

    project = _todoist_post("projects", token, {"name": project_name})
    project_id = project["id"]
    print(f"✅ Project created (id={project_id})")

    print("\n🔍 Checking for already-processed repositories...")
    todoist_processed_slugs = _fetch_processed_slugs(token)
    processed_slugs = persisted_slugs | todoist_processed_slugs
    print(f"  ↳ {len(persisted_slugs)} slug(s) from persisted state")
    print(f"  ↳ {len(todoist_processed_slugs)} slug(s) from Todoist")
    print(f"  ⏭️  {len(processed_slugs)} repository slug(s) will be skipped")

    state_dirty = False
    tasks_created = 0

    for since, section_label, due_string in _PERIODS:
        print(f"\n🔍 Fetching {section_label}...")
        repos = _fetch_for_languages(since, languages)
        if not repos:
            print(f"  ⚠️  No repositories found for {section_label}")
            continue

        before = len(repos)
        repos = [
            r
            for r in repos
            if _normalise_slug(r.get("slug", "")) not in processed_slugs
        ]
        skipped = before - len(repos)
        if skipped:
            print(
                f"  ⏭️  Skipped {skipped} already-processed "
                f"repositor{'y' if skipped == 1 else 'ies'}"
            )
        if not repos:
            print(f"  ✅ All {before} repositories for {section_label} already processed")
            continue
        print(f"  Found {len(repos)} new repositories")

        section = _todoist_post(
            "sections",
            token,
            {"project_id": project_id, "name": section_label},
        )
        section_id = section["id"]
        print(f"  📂 {section_label}")

        for repo in repos:
            content = _build_task_content(repo)
            slug = _normalise_slug(repo.get("slug", ""))
            labels = [_READ_LATER_LABEL]
            language_label = _to_kebab_label(repo.get("language", ""))
            if language_label and language_label not in labels:
                labels.append(language_label)
            task_data: dict = {
                "content": content,
                "description": _build_task_description(repo),
                "project_id": project_id,
                "section_id": section_id,
                # Todoist REST API v1 accepts label names directly as strings.
                # If the label does not yet exist in Todoist it will be created.
                "labels": labels,
                "priority": _TASK_PRIORITY,
            }
            if due_string:
                task_data["due_string"] = due_string
            _todoist_post("tasks", token, task_data)
            tasks_created += 1
            # Track as processed so a repo appearing in multiple periods
            # (e.g. trending today AND this week) is only imported once.
            processed_slugs.add(slug)
            _mark_slug_in_state(
                state,
                slug,
                run_timestamp,
                project_name,
                section_label,
                languages,
            )
            state_dirty = True
            print(f"    ✓ {content[:100]}")

    if state_dirty:
        print(f"\n💾 Persisting {tasks_created} new slug(s) to state file...")
        try:
            _save_processed_state(state_file, state)
        except OSError as exc:
            print(
                "❌ Failed to persist processed slug state after creating tasks. "
                "Stopping to avoid dedup drift.",
                file=sys.stderr,
            )
            print(f"   Path: {state_file}", file=sys.stderr)
            print(f"   Error: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        print("\nℹ️  No new repositories were added; state file unchanged.")

    print()
    print(f"🎉 Done! Project '{project_name}' is ready in Todoist.")


if __name__ == "__main__":
    main()
