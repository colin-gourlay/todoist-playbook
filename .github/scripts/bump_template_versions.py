#!/usr/bin/env python3
"""Bump patch version in meta.yml for templates that changed in a PR.

Usage (environment variables):
  BASE_SHA  – Git SHA of the PR base commit.
  HEAD_SHA  – Git SHA of the PR head commit.

Idempotency guarantee
---------------------
For every changed template the script compares the version present in meta.yml
at BASE_SHA against the version currently on disk.  If they already differ the
template was bumped by a previous run of this workflow; the template is skipped.
This means re-running the workflow on an unchanged PR never produces extra bumps.

Skip rules
----------
* Version == 0.0.0 → "unreviewed"; never bumped automatically.
* Only meta.yml changed between base and head → treat as an already-bumped or
  manual metadata edit; do not re-bump.
* Current version already differs from the base version → already bumped.
"""

import os
import re
import subprocess
import sys

TEMPLATE_DIRS = ["templates", "prompt-templates"]


def run_git(*args):
    """Run a git command and return stdout as a string, or raise on failure."""
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def get_changed_files(base_sha, head_sha):
    """Return the list of files changed between base_sha and head_sha."""
    output = run_git("diff", "--name-only", base_sha, head_sha)
    return [line.strip() for line in output.splitlines() if line.strip()]


def get_base_file(base_sha, repo_path):
    """Return the contents of a file at base_sha, or None if it did not exist."""
    try:
        return run_git("show", f"{base_sha}:{repo_path}")
    except subprocess.CalledProcessError:
        return None


def parse_version(text):
    """Extract the value of the 'version:' key from YAML-ish text, or None."""
    for line in (text or "").splitlines():
        if line.startswith("version:"):
            return line.split(":", 1)[1].strip().strip("\"'")
    return None


def bump_patch(version):
    """Return x.y.(z+1) for a version string x.y.z, or None if unparseable."""
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", version)
    if not match:
        return None
    major, minor, patch = (int(g) for g in match.groups())
    return f"{major}.{minor}.{patch + 1}"


def write_version(meta_path, old_version, new_version):
    """Replace the version line in meta_path in-place.  Returns True on success."""
    with open(meta_path, encoding="utf-8") as fh:
        content = fh.read()

    new_content = re.sub(
        r"^version:\s*[\"']?" + re.escape(old_version) + r"[\"']?\s*$",
        f"version: {new_version}",
        content,
        flags=re.MULTILINE,
    )

    if new_content == content:
        return False

    with open(meta_path, "w", encoding="utf-8") as fh:
        fh.write(new_content)
    return True


def collect_changed_templates(changed_files):
    """Map changed files to (template_dir, slug) → has_non_meta_change."""
    templates = {}
    for filepath in changed_files:
        for tdir in TEMPLATE_DIRS:
            prefix = f"{tdir}/"
            if not filepath.startswith(prefix):
                continue
            rest = filepath[len(prefix):]
            parts = rest.split("/", 1)
            if not parts:
                continue
            slug = parts[0]
            filename = parts[1] if len(parts) > 1 else parts[0]
            key = (tdir, slug)
            is_meta = filename == "meta.yml"
            if key not in templates:
                templates[key] = False
            if not is_meta:
                templates[key] = True
    return templates


def main():
    base_sha = os.environ.get("BASE_SHA", "").strip()
    head_sha = os.environ.get("HEAD_SHA", "").strip()

    if not base_sha or not head_sha:
        print(
            "❌ BASE_SHA and HEAD_SHA environment variables are required.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        changed_files = get_changed_files(base_sha, head_sha)
    except subprocess.CalledProcessError as exc:
        print(f"❌ git diff failed: {exc}", file=sys.stderr)
        sys.exit(1)

    if not changed_files:
        print("ℹ️  No files changed between base and head.")
        return

    templates = collect_changed_templates(changed_files)

    if not templates:
        print("ℹ️  No template directories affected.")
        return

    bumped = []

    for (tdir, slug), has_non_meta in templates.items():
        label = f"{tdir}/{slug}"

        if not has_non_meta:
            print(
                f"⏭️  {label}: only meta.yml changed — skipping "
                "(already bumped or manual metadata edit)"
            )
            continue

        meta_path = os.path.join(tdir, slug, "meta.yml")

        if not os.path.exists(meta_path):
            print(f"⚠️  {label}: meta.yml not found — skipping")
            continue

        with open(meta_path, encoding="utf-8") as fh:
            current_text = fh.read()

        current_version = parse_version(current_text)

        if not current_version:
            print(f"⚠️  {label}: no version field found — skipping")
            continue

        if current_version == "0.0.0":
            print(f"⏭️  {label}: version 0.0.0 (unreviewed) — skipping")
            continue

        # Idempotency: compare current version to base version
        base_text = get_base_file(base_sha, meta_path)
        base_version = parse_version(base_text)

        if base_version and current_version != base_version:
            print(
                f"⏭️  {label}: already bumped "
                f"({base_version} → {current_version}) — skipping"
            )
            continue

        new_version = bump_patch(current_version)
        if not new_version:
            print(
                f"⚠️  {label}: cannot parse version '{current_version}' — skipping"
            )
            continue

        if write_version(meta_path, current_version, new_version):
            print(f"✅ {label}: {current_version} → {new_version}")
            bumped.append(meta_path)
        else:
            print(f"⚠️  {label}: failed to update version in {meta_path}")

    if not bumped:
        print("ℹ️  No versions bumped.")
    else:
        print(f"\n📦 Bumped {len(bumped)} template(s).")


if __name__ == "__main__":
    main()
