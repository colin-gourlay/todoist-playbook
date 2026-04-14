#!/usr/bin/env python3
"""Sync GitHub review issues for templates that are still unreviewed.

Rules:
- A template with version 0.0.0 should have one open review issue.
- A template with version != 0.0.0 should not have an open review issue.
- The review label is ensured automatically.
- Matching is done via hidden issue-body markers to keep runs idempotent.
- Missing meta.yml files produce a single maintenance issue.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from dataclasses import dataclass

LABEL_NAME = "to-be-reviewed"
LABEL_COLOR = "d4c5f9"
LABEL_DESCRIPTION = "Template is pending feature-completeness review"

SUNSET_LABEL_NAME = "deprecation-sunset"
SUNSET_LABEL_COLOR = "b60205"
SUNSET_LABEL_DESCRIPTION = "Deprecated template has reached sunset date and should be removed"

TEMPLATE_ROOT = "csv-templates"
TEMPLATE_MARKER_RE = re.compile(r"template-review-slug:\s*([a-z0-9-]+)")
MISSING_META_MARKER = "template-review-maintenance: missing-meta-yml"
SUNSET_MARKER_RE = re.compile(r"template-sunset-slug:\s*([a-z0-9-]+)")


@dataclass
class TemplateState:
    slug: str
    version: str | None
    deprecated: bool
    sunset_date: str | None


class GitHubClient:
    def __init__(self, repository: str, token: str, dry_run: bool = False):
        self.repository = repository
        self.token = token
        self.base = f"https://api.github.com/repos/{repository}"
        self.dry_run = dry_run

    def request(self, method: str, path: str, data: dict | list | None = None):
        url = self.base + path
        payload = None
        if data is not None:
            payload = json.dumps(data).encode("utf-8")

        req = urllib.request.Request(url, data=payload, method=method)
        req.add_header("Authorization", f"Bearer {self.token}")
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("X-GitHub-Api-Version", "2022-11-28")
        if payload is not None:
            req.add_header("Content-Type", "application/json")

        try:
            with urllib.request.urlopen(req) as response:
                body = response.read().decode("utf-8")
                return json.loads(body) if body else None
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"GitHub API {method} {path} failed: {exc.code} {body}") from exc

    def ensure_label(self, name: str, color: str, description: str):
        label_path = f"/labels/{urllib.parse.quote(name, safe='')}"
        try:
            self.request("GET", label_path)
            print(f"✅ Label exists: {name}")
            return
        except RuntimeError as exc:
            if " 404 " not in str(exc):
                raise

        if self.dry_run:
            print(f"🧪 DRY-RUN: would create label '{name}'")
            return

        self.request(
            "POST",
            "/labels",
            {"name": name, "color": color, "description": description},
        )
        print(f"✅ Created label: {name}")

    def list_issues(self, state: str = "all"):
        issues = []
        page = 1
        while True:
            path = f"/issues?state={state}&per_page=100&page={page}"
            batch = self.request("GET", path) or []
            if not batch:
                break
            issues.extend(batch)
            if len(batch) < 100:
                break
            page += 1
        return [item for item in issues if "pull_request" not in item]

    def create_issue(self, title: str, body: str, labels: list[str], assignee: str):
        if self.dry_run:
            print(f"🧪 DRY-RUN: would create issue '{title}'")
            return None
        payload = {
            "title": title,
            "body": body,
            "labels": labels,
            "assignees": [assignee] if assignee else [],
        }
        issue = self.request("POST", "/issues", payload)
        print(f"✅ Created issue #{issue['number']}: {issue['title']}")
        return issue

    def update_issue(self, number: int, data: dict, dry_run_note: str):
        if self.dry_run:
            print(f"🧪 DRY-RUN: would update issue #{number}: {dry_run_note}")
            return None
        return self.request("PATCH", f"/issues/{number}", data)

    def ensure_label_on_issue(self, number: int, label: str):
        if self.dry_run:
            print(f"🧪 DRY-RUN: would ensure label '{label}' on issue #{number}")
            return
        self.request("POST", f"/issues/{number}/labels", {"labels": [label]})

    def ensure_assignee_on_issue(self, number: int, assignee: str):
        if not assignee:
            return
        if self.dry_run:
            print(f"🧪 DRY-RUN: would ensure assignee '{assignee}' on issue #{number}")
            return
        self.request("POST", f"/issues/{number}/assignees", {"assignees": [assignee]})


def parse_meta_value(text: str, key: str):
    prefix = key + ":"
    for line in text.splitlines():
        if line.startswith(prefix):
            return line.split(":", 1)[1].strip().strip("\"'")
    return None


def parse_meta_bool(text: str, key: str):
    value = parse_meta_value(text, key)
    if value is None:
        return False
    return value.strip().lower() in {"true", "yes", "1", "on"}


def load_template_states(root: str):
    states = []
    missing_meta = []

    if not os.path.isdir(root):
        return states, missing_meta

    for name in sorted(os.listdir(root)):
        path = os.path.join(root, name)
        if not os.path.isdir(path):
            continue

        meta_path = os.path.join(path, "meta.yml")
        if not os.path.exists(meta_path):
            missing_meta.append(name)
            continue

        with open(meta_path, encoding="utf-8") as fh:
            content = fh.read()

        version = parse_meta_value(content, "version")
        deprecated = parse_meta_bool(content, "deprecated")
        sunset_date = parse_meta_value(content, "sunset_date")
        states.append(
            TemplateState(
                slug=name,
                version=version,
                deprecated=deprecated,
                sunset_date=sunset_date,
            )
        )

    return states, missing_meta


def marker_for_slug(slug: str):
    return f"<!-- template-review-slug: {slug} -->"


def template_issue_title(slug: str):
    return f"Review template: {slug}"


def template_issue_body(slug: str):
    return "\n".join(
        [
            marker_for_slug(slug),
            "",
            f"Template {slug} is currently marked as unreviewed (version 0.0.0).",
            "",
            "Review goal:",
            "- Confirm the template is feature complete for its intended workflow.",
            "- Confirm all required tasks are present.",
            "- Confirm no out-of-scope or unnecessary tasks are included.",
            "",
            "Completion criteria:",
            "- [ ] Template content reviewed end to end.",
            "- [ ] Any required edits applied in a pull request.",
            "- [ ] meta.yml version moved away from 0.0.0 once approved.",
        ]
    )


def missing_meta_title():
    return "Fix template folders missing meta.yml"


def sunset_marker_for_slug(slug: str):
    return f"<!-- template-sunset-slug: {slug} -->"


def sunset_issue_title(slug: str):
    return f"Remove deprecated template: {slug}"


def sunset_issue_body(slug: str, sunset_date_value: str):
    return "\n".join(
        [
            sunset_marker_for_slug(slug),
            "",
            f"Template `{slug}` is marked `deprecated: true` and has reached its `sunset_date` ({sunset_date_value}).",
            "",
            "Action required:",
            "- Remove the template folder and related references.",
            "- Update index and documentation links if present.",
            "- Record the removal in CHANGELOG.",
            "",
            "Completion criteria:",
            "- [ ] Deprecated template removed from `csv-templates/`.",
            "- [ ] Any references removed or redirected.",
            "- [ ] Validation passes after cleanup.",
        ]
    )


def missing_meta_body(slugs: list[str]):
    lines = [
        f"<!-- {MISSING_META_MARKER} -->",
        "",
        "The following template folders are missing meta.yml and cannot be tracked for review status:",
        "",
    ]
    lines.extend([f"- {slug}" for slug in slugs])
    lines.extend(
        [
            "",
            "Completion criteria:",
            "- [ ] Add missing meta.yml files.",
            "- [ ] Ensure slug and version keys are present.",
        ]
    )
    return "\n".join(lines)


def index_existing_issues(issues: list[dict]):
    by_slug = {}
    sunset_by_slug = {}
    missing_meta_issue = None

    for issue in issues:
        body = issue.get("body") or ""
        match = TEMPLATE_MARKER_RE.search(body)
        if match:
            by_slug[match.group(1)] = issue
        sunset_match = SUNSET_MARKER_RE.search(body)
        if sunset_match:
            sunset_by_slug[sunset_match.group(1)] = issue
        if MISSING_META_MARKER in body:
            missing_meta_issue = issue

    return by_slug, missing_meta_issue, sunset_by_slug


def sync_template_issues(client: GitHubClient, assignee: str, states: list[TemplateState], existing_by_slug: dict):
    desired_open = {item.slug for item in states if item.version == "0.0.0"}

    for item in states:
        issue = existing_by_slug.get(item.slug)
        should_be_open = item.slug in desired_open

        if should_be_open:
            if issue is None:
                client.create_issue(
                    title=template_issue_title(item.slug),
                    body=template_issue_body(item.slug),
                    labels=[LABEL_NAME],
                    assignee=assignee,
                )
                continue

            if issue.get("state") != "open":
                client.update_issue(
                    issue["number"],
                    {"state": "open"},
                    "reopen review issue",
                )
                print(f"✅ Reopened issue #{issue['number']} for {item.slug}")

            client.ensure_label_on_issue(issue["number"], LABEL_NAME)
            client.ensure_assignee_on_issue(issue["number"], assignee)
            continue

        if issue is not None and issue.get("state") == "open":
            client.update_issue(
                issue["number"],
                {"state": "closed"},
                "close review issue because template is no longer 0.0.0",
            )
            print(f"✅ Closed issue #{issue['number']} for {item.slug}")


def sync_missing_meta_issue(
    client: GitHubClient,
    assignee: str,
    missing_meta_slugs: list[str],
    existing_issue: dict | None,
):
    if missing_meta_slugs:
        if existing_issue is None:
            client.create_issue(
                title=missing_meta_title(),
                body=missing_meta_body(missing_meta_slugs),
                labels=[LABEL_NAME],
                assignee=assignee,
            )
            return

        if existing_issue.get("state") != "open":
            client.update_issue(
                existing_issue["number"],
                {"state": "open"},
                "reopen missing meta maintenance issue",
            )
            print(f"✅ Reopened missing-meta issue #{existing_issue['number']}")

        client.ensure_label_on_issue(existing_issue["number"], LABEL_NAME)
        client.ensure_assignee_on_issue(existing_issue["number"], assignee)
        client.update_issue(
            existing_issue["number"],
            {"body": missing_meta_body(missing_meta_slugs)},
            "refresh missing meta issue body",
        )
        print(f"✅ Updated missing-meta issue #{existing_issue['number']}")
        return

    if existing_issue is not None and existing_issue.get("state") == "open":
        client.update_issue(
            existing_issue["number"],
            {"state": "closed"},
            "close missing meta issue because there are no missing files",
        )
        print(f"✅ Closed missing-meta issue #{existing_issue['number']}")


def has_reached_sunset(item: TemplateState):
    if not item.deprecated or not item.sunset_date:
        return False
    try:
        sunset = date.fromisoformat(item.sunset_date)
    except ValueError:
        print(f"⚠️ Invalid sunset_date for {item.slug}: {item.sunset_date}")
        return False
    return date.today() >= sunset


def sync_sunset_issues(client: GitHubClient, assignee: str, states: list[TemplateState], existing_by_slug: dict):
    overdue = {item.slug: item for item in states if has_reached_sunset(item)}

    for slug, item in overdue.items():
        issue = existing_by_slug.get(slug)
        if issue is None:
            client.create_issue(
                title=sunset_issue_title(slug),
                body=sunset_issue_body(slug, item.sunset_date or "unknown"),
                labels=[SUNSET_LABEL_NAME],
                assignee=assignee,
            )
            continue

        if issue.get("state") != "open":
            client.update_issue(
                issue["number"],
                {"state": "open"},
                "reopen sunset issue",
            )
            print(f"✅ Reopened sunset issue #{issue['number']} for {slug}")

        client.ensure_label_on_issue(issue["number"], SUNSET_LABEL_NAME)
        client.ensure_assignee_on_issue(issue["number"], assignee)
        client.update_issue(
            issue["number"],
            {"body": sunset_issue_body(slug, item.sunset_date or "unknown")},
            "refresh sunset issue body",
        )
        print(f"✅ Updated sunset issue #{issue['number']} for {slug}")

    for slug, issue in existing_by_slug.items():
        if slug in overdue:
            continue
        if issue.get("state") == "open":
            client.update_issue(
                issue["number"],
                {"state": "closed"},
                "close sunset issue because template is no longer overdue",
            )
            print(f"✅ Closed sunset issue #{issue['number']} for {slug}")


def main():
    repository = os.environ.get("GITHUB_REPOSITORY", "").strip()
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    assignee = os.environ.get("REVIEW_ISSUE_ASSIGNEE", "").strip()
    dry_run = os.environ.get("DRY_RUN", "").strip().lower() in {"1", "true", "yes"}

    if not repository:
        print("❌ GITHUB_REPOSITORY is required (example: owner/repo)", file=sys.stderr)
        sys.exit(1)
    if not token:
        print("❌ GITHUB_TOKEN is required", file=sys.stderr)
        sys.exit(1)

    print(f"🔎 Repository: {repository}")
    print(f"🧪 Dry-run: {'yes' if dry_run else 'no'}")

    client = GitHubClient(repository=repository, token=token, dry_run=dry_run)
    client.ensure_label(LABEL_NAME, LABEL_COLOR, LABEL_DESCRIPTION)
    client.ensure_label(SUNSET_LABEL_NAME, SUNSET_LABEL_COLOR, SUNSET_LABEL_DESCRIPTION)

    states, missing_meta = load_template_states(TEMPLATE_ROOT)
    print(f"📋 Found {len(states)} template(s) with meta.yml")
    if missing_meta:
        print(f"⚠️ Missing meta.yml in {len(missing_meta)} template folder(s): {', '.join(missing_meta)}")

    issues = client.list_issues(state="all")
    by_slug, missing_meta_issue, sunset_by_slug = index_existing_issues(issues)

    sync_template_issues(client, assignee=assignee, states=states, existing_by_slug=by_slug)
    sync_sunset_issues(client, assignee=assignee, states=states, existing_by_slug=sunset_by_slug)
    sync_missing_meta_issue(
        client,
        assignee=assignee,
        missing_meta_slugs=missing_meta,
        existing_issue=missing_meta_issue,
    )

    print("✅ Sync complete")


if __name__ == "__main__":
    main()
