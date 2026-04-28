#!/usr/bin/env python3
"""Generate a browsable Template Gallery as static files for GitHub Pages.

Usage:
    python3 generate_gallery.py

Output files (written into OUTPUT_DIR, default: docs/):
    index.html          Slim HTML with CSP/referrer/permissions-policy meta tags,
                        a JSON data island, and SRI-integrity script tags.
    styles.css          Extracted gallery stylesheet (no inline styles in HTML).
    app.js              Extracted gallery JavaScript (no inline scripts in HTML).
    vendor/marked.min.js   Vendored Markdown parser (verified against manifest).
    vendor/purify.min.js   Vendored DOMPurify sanitizer (verified against manifest).

Environment variables:
    TEMPLATES_DIR         Path to the CSV templates folder (default: csv-templates)
    PROMPT_TEMPLATES_DIR  Path to the prompt-templates folder (default: prompt-templates)
    OUTPUT_DIR            Path to the output folder (default: docs)
    TP_ALLOW_VENDOR_TOFU  Set to "1" to allow first-time vendoring when the
                          vendor-manifest.json has empty sha384 fields. The manifest
                          is updated in-place with the computed hashes. Without this
                          flag an empty sha384 is a hard build error.
"""

import base64
import csv
import datetime
import hashlib
import json
import os
import re
import shutil
import sys
import urllib.request

from template_discovery import iter_template_locations

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
VENDOR_MANIFEST_PATH = os.path.join(SCRIPTS_DIR, "vendor-manifest.json")

TEMPLATES_DIR = os.environ.get("TEMPLATES_DIR", "csv-templates")
PROMPT_TEMPLATES_DIR = os.environ.get("PROMPT_TEMPLATES_DIR", "prompt-templates")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "docs")

# Category display metadata: slug -> (emoji, human-readable label)
CATEGORY_META = {
    "personal-systems":         ("🔁", "Personal Systems"),
    "engineering":              ("💻", "Engineering"),
    "agile":                    ("🔄", "Agile"),
    "career":                   ("🧑\u200d💼", "Career"),
    "creative":                 ("🎙", "Creative"),
    "saas-management":          ("☁️", "SaaS Management"),
    "professional-development": ("🎓", "Professional Development"),
    "brand-and-social":         ("🌐", "Brand & Social"),
    "radio-show-systems":       ("📻", "Radio Show Systems"),
    "content-generation":       ("🤖", "Content Generation"),
}


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def parse_meta(path):
    """Parse a simple meta.yml file without a YAML library."""
    meta = {"tags": [], "inputs": []}
    in_list = None  # name of the current list key being parsed
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            # Detect start of a list block (e.g. "tags:" or "inputs:" with no value)
            m_list = re.match(r"^(tags|inputs):\s*$", line)
            if m_list:
                in_list = m_list.group(1)
                continue
            if in_list:
                m = re.match(r"^\s+-\s+(.+)$", line)
                if m:
                    meta[in_list].append(m.group(1).strip())
                    continue
                # Any non-indented line ends the list block
                if line and not line[0].isspace():
                    in_list = None
            m = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*):\s*(.*)$", line)
            if m:
                key = m.group(1)
                value = m.group(2).strip().strip("\"'")
                if key not in ("tags", "inputs"):
                    in_list = None
                    meta[key] = value
    return meta


def parse_csv_rows(path):
    """Return all valid (section/task) rows from a template CSV."""
    rows = []
    try:
        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row_type = row.get("TYPE", "").strip()
                content = row.get("CONTENT", "").strip()
                if row_type in ("section", "task") and content:
                    rows.append({
                        "type": row_type,
                        "content": content,
                        "priority": row.get("PRIORITY", "").strip(),
                        "indent": row.get("INDENT", "1").strip(),
                    })
    except Exception as exc:
        print(f"Warning: could not parse {path}: {exc}", file=sys.stderr)
    return rows


# ---------------------------------------------------------------------------
# Template loading
# ---------------------------------------------------------------------------

def read_readme(path):
    """Return README markdown contents, or empty string if missing/unreadable."""
    if not path or not os.path.exists(path):
        return ""
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except Exception as exc:
        print(f"Warning: could not read {path}: {exc}", file=sys.stderr)
        return ""


def load_templates():
    templates = []

    # Load CSV templates (supports nested csv-templates/{group}/{slug}/ layout)
    if os.path.isdir(TEMPLATES_DIR):
        for location in iter_template_locations(TEMPLATES_DIR):
            template_dir = location.template_dir
            meta_path = location.meta_path
            csv_path = location.csv_path
            if not os.path.exists(meta_path):
                continue
            meta = parse_meta(meta_path)
            rows = parse_csv_rows(csv_path) if os.path.exists(csv_path) else []
            task_count = sum(1 for r in rows if r["type"] == "task")
            section_count = sum(1 for r in rows if r["type"] == "section")
            templates.append({
                "slug": location.slug,
                "name": meta.get("name", location.slug),
                "description": meta.get("description", ""),
                "category": meta.get("category", ""),
                "tags": meta.get("tags", []),
                "estimated_duration": meta.get("estimated_duration", ""),
                "recurrence_suggestion": meta.get("recurrence_suggestion", ""),
                "author": meta.get("author", ""),
                "version": meta.get("version", ""),
                "deprecated": meta.get("deprecated", ""),
                "task_count": task_count,
                "section_count": section_count,
                "rows": rows,
                "csv_url": f"csv-templates/{location.relative_path}/template.csv",
                "prompt_url": "",
                "inputs": [],
                "type": "template",
                "readme": read_readme(location.readme_path),
            })

    # Load prompt templates
    if os.path.isdir(PROMPT_TEMPLATES_DIR):
        for slug in sorted(os.listdir(PROMPT_TEMPLATES_DIR)):
            template_dir = os.path.join(PROMPT_TEMPLATES_DIR, slug)
            if not os.path.isdir(template_dir):
                continue
            meta_path = os.path.join(template_dir, "meta.yml")
            if not os.path.exists(meta_path):
                continue
            meta = parse_meta(meta_path)
            readme_path = os.path.join(template_dir, "README.md")
            templates.append({
                "slug": slug,
                "name": meta.get("name", slug),
                "description": meta.get("description", ""),
                "category": meta.get("category", ""),
                "tags": meta.get("tags", []),
                "estimated_duration": "",
                "recurrence_suggestion": "",
                "author": meta.get("author", ""),
                "version": meta.get("version", ""),
                "task_count": 0,
                "section_count": 0,
                "rows": [],
                "csv_url": "",
                "prompt_url": f"prompt-templates/{slug}/prompt.md",
                "inputs": meta.get("inputs", []),
                "type": "prompt",
                "readme": read_readme(readme_path),
            })

    return templates


# ---------------------------------------------------------------------------
# Spotlight selection
# ---------------------------------------------------------------------------

def _semver_key(template):
    """Return a tuple (major, minor, patch) for semver comparison."""
    version = template.get("version", "0.0.0") or "0.0.0"
    parts = version.split(".")
    try:
        return tuple(int(p) for p in (parts + ["0", "0"])[:3])
    except ValueError:
        return (0, 0, 0)


def _is_truthy(value):
    """Return True when a metadata value represents boolean true."""
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"true", "yes", "1", "on"}


def get_spotlight_template(templates):
    """Return the template with the highest semantic version, excluding 0.0.0.

    Returns None if all templates are at version 0.0.0 (unreviewed).
    Only regular templates (type == 'template') are considered.
    """
    candidates = [
        t for t in templates
        if t.get("type") == "template"
        and _semver_key(t) > (0, 0, 0)
        and not _is_truthy(t.get("deprecated"))
    ]
    if not candidates:
        return None
    return max(candidates, key=_semver_key)




# ---------------------------------------------------------------------------
# JSON island helpers
# ---------------------------------------------------------------------------

def _escape_json_for_html(s):
    """Escape a JSON string so it is safe inside a <script type="application/json"> island.

    Prevents the sequence </script from closing the enclosing tag and removes
    HTML comment delimiters and Unicode line/paragraph separators that would
    otherwise confuse parsers or JavaScript engines.
    """
    s = s.replace("</", "<\\/")
    s = s.replace("<!--", "<\\u0021--")
    s = s.replace("-->", "--\\u003e")
    s = s.replace("\u2028", "\\u2028")
    s = s.replace("\u2029", "\\u2029")
    return s


# ---------------------------------------------------------------------------
# Vendor asset management
# ---------------------------------------------------------------------------

def vendor_assets():
    """Download and verify vendored JS libraries; return SRI integrity map.

    Reads .github/scripts/vendor-manifest.json.  For each entry:
    - If the file already exists in docs/vendor/ and its SHA-384 matches, skip.
    - Otherwise download and verify (or, when TP_ALLOW_VENDOR_TOFU=1 and the
      manifest sha384 is empty, compute the hash and self-populate the manifest).

    Returns a dict: {filename: "sha384-{base64}"} for use in <script integrity>.
    """
    allow_tofu = os.environ.get("TP_ALLOW_VENDOR_TOFU", "").strip() == "1"
    vendor_dir = os.path.join(OUTPUT_DIR, "vendor")
    os.makedirs(vendor_dir, exist_ok=True)

    with open(VENDOR_MANIFEST_PATH, encoding="utf-8") as f:
        manifest = json.load(f)

    manifest_updated = False
    integrity = {}

    for filename, entry in manifest.items():
        url = entry["url"]
        expected_hash = entry.get("sha384", "").strip()
        dest = os.path.join(vendor_dir, filename)

        if not expected_hash:
            if not allow_tofu:
                print(
                    f"❌ vendor-manifest.json: sha384 for {filename!r} is empty.\n"
                    "   Run with TP_ALLOW_VENDOR_TOFU=1 to download and auto-populate "
                    "the hash on first use, then commit the updated manifest.",
                    file=sys.stderr,
                )
                sys.exit(1)
            # TOFU mode: download, compute, populate manifest
            print(f"  [TOFU] Downloading {url} …")
            with urllib.request.urlopen(url) as resp:  # noqa: S310
                data = resp.read()
            computed = base64.b64encode(hashlib.sha384(data).digest()).decode()
            print(f"  [TOFU] {filename}: sha384-{computed}")
            entry["sha384"] = computed
            expected_hash = computed
            manifest_updated = True
            with open(dest, "wb") as f:
                f.write(data)
            integrity[filename] = f"sha384-{computed}"
            continue

        # Hash is known — verify (re-download only if file is missing or stale)
        if os.path.exists(dest):
            with open(dest, "rb") as f:
                actual = base64.b64encode(hashlib.sha384(f.read()).digest()).decode()
            if actual == expected_hash:
                integrity[filename] = f"sha384-{expected_hash}"
                continue
            print(f"  ⚠ {filename} hash mismatch — re-downloading…")

        print(f"  Downloading {url} …")
        with urllib.request.urlopen(url) as resp:  # noqa: S310
            data = resp.read()
        actual = base64.b64encode(hashlib.sha384(data).digest()).decode()
        if actual != expected_hash:
            print(
                f"❌ Hash mismatch for {filename}:\n"
                f"   expected: {expected_hash}\n"
                f"   got:      {actual}\n"
                "   Update vendor-manifest.json or re-run with TP_ALLOW_VENDOR_TOFU=1.",
                file=sys.stderr,
            )
            sys.exit(1)
        with open(dest, "wb") as f:
            f.write(data)
        integrity[filename] = f"sha384-{expected_hash}"

    if manifest_updated:
        with open(VENDOR_MANIFEST_PATH, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
            f.write("\n")
        print(f"  ✅ vendor-manifest.json updated with computed hashes.")

    return integrity


# ---------------------------------------------------------------------------
# HTML generation (slim shell — CSS/JS are external files)
# ---------------------------------------------------------------------------

def generate_html(templates, spotlight=None, integrity=None):
    if integrity is None:
        integrity = {}

    combined = {
        "templates": templates,
        "category_meta": CATEGORY_META,
        "spotlight": spotlight,
    }
    combined_json = _escape_json_for_html(json.dumps(combined, ensure_ascii=False))

    marked_sri  = integrity.get("marked.min.js", "")
    purify_sri  = integrity.get("purify.min.js", "")

    marked_integrity  = f' integrity="{marked_sri}" crossorigin="anonymous"' if marked_sri else ""
    purify_integrity  = f' integrity="{purify_sri}" crossorigin="anonymous"' if purify_sri else ""

    # NOTE: style-src is 'self' only. Any future inline style="" attributes
    # require a separate 'style-src-attr "unsafe-inline"' directive — do NOT
    # broaden style-src itself.
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <!-- Content-Security-Policy: style-src is 'self' only.
       If inline style="" attributes are ever required, add style-src-attr 'unsafe-inline'
       as a narrowly scoped allowance — do NOT broaden style-src. -->
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; manifest-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'; upgrade-insecure-requests">
  <meta name="referrer" content="strict-origin-when-cross-origin">
  <meta name="permissions-policy" content="camera=(), microphone=(), geolocation=(), payment=()">
  <title>Todoist Playbook \u2014 Template Gallery</title>
  <link rel="stylesheet" href="styles.css">
</head>
<body>

<header class="site-header">
  <h1>📋 Todoist Playbook</h1>
  <p>Curated templates for getting things done</p>
  <div class="search-bar" role="search">
    <input type="search" id="search-input" placeholder="🔍 Search templates\u2026"
           aria-label="Search templates" autocomplete="off" spellcheck="false">
    <button class="search-clear" id="search-clear" aria-label="Clear search">✕</button>
  </div>
</header>

<nav class="breadcrumb" id="breadcrumb" aria-label="Breadcrumb">
  <button id="btn-back" aria-label="Back to all categories">← All Categories</button>
  <span class="crumb-sep" aria-hidden="true">/</span>
  <span class="crumb-current" id="crumb-label"></span>
</nav>

<div class="container" id="container">
  <!-- Populated by JavaScript -->
</div>

<div class="modal-backdrop" id="modal-backdrop" role="dialog" aria-modal="true"
     aria-labelledby="modal-title" aria-hidden="true">
  <div class="modal-dialog" role="document">
    <div class="modal-header">
      <div class="modal-title-block">
        <div class="modal-title" id="modal-title"></div>
        <div class="modal-subtitle" id="modal-subtitle"></div>
      </div>
      <div class="modal-actions" id="modal-actions"></div>
      <button type="button" class="modal-close" id="modal-close" aria-label="Close">✕</button>
    </div>
    <div class="modal-body" id="modal-body"></div>
  </div>
</div>

<footer class="site-footer">
  <div class="footer-links">
    <a href="https://github.com/colin-gourlay/todoist-playbook/issues/new?template=template-request.yml"
       target="_blank" rel="noopener noreferrer">
      💡 Request a Template
    </a>
    <a href="https://github.com/colin-gourlay/todoist-playbook/issues/new?template=bug-report.yml"
       target="_blank" rel="noopener noreferrer">
      🐛 Report a Bug
    </a>
    <a href="https://github.com/colin-gourlay/todoist-playbook"
       target="_blank" rel="noopener noreferrer">
      ⭐ View on GitHub
    </a>
  </div>
  <div>Built with ❤️ · <a href="https://github.com/colin-gourlay/todoist-playbook/blob/main/CONTRIBUTING"
       target="_blank" rel="noopener noreferrer">Contributing Guide</a></div>
</footer>

<script type="application/json" id="tp-data">{combined_json}</script>
<script src="vendor/marked.min.js"{marked_integrity}></script>
<script src="vendor/purify.min.js"{purify_integrity}></script>
<script src="app.js" defer></script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Build-time security assertion
# ---------------------------------------------------------------------------

def assert_data_island(output_html_path):
    """Verify the JSON data island was written and round-trips cleanly."""
    with open(output_html_path, encoding="utf-8") as f:
        rendered = f.read()
    m = re.search(
        r'<script[^>]+type="application/json"[^>]+id="tp-data"[^>]*>(.+?)</script>',
        rendered,
        re.DOTALL,
    )
    assert m, "Data island <script type='application/json' id='tp-data'> not found in rendered HTML"
    # Round-trip: unescape <\/ back to </ for JSON parsing
    raw = m.group(1).replace("<\\/", "</")
    json.loads(raw)  # raises json.JSONDecodeError if malformed


def _is_old_generate_html():
    """Return False — kept for signature compatibility."""
    return False


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    if not os.path.isdir(TEMPLATES_DIR):
        print(f"Error: CSV templates directory not found: {TEMPLATES_DIR}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Disable Jekyll processing on GitHub Pages
    with open(os.path.join(OUTPUT_DIR, ".nojekyll"), "w"):
        pass

    # Vendor marked.js and DOMPurify into docs/vendor/ (download + verify)
    print("Vendoring JS libraries…")
    integrity = vendor_assets()

    # Write gallery CSS and JS as sibling files (required for strict CSP 'self')
    css_src = os.path.join(SCRIPTS_DIR, "gallery.css")
    js_src  = os.path.join(SCRIPTS_DIR, "gallery.js")
    shutil.copy2(css_src, os.path.join(OUTPUT_DIR, "styles.css"))
    shutil.copy2(js_src,  os.path.join(OUTPUT_DIR, "app.js"))

    # Copy each CSV template's template.csv and README.md into the output
    # directory so download links and modal sources work. Supports the
    # nested csv-templates/{group}/{slug}/ layout.
    for location in iter_template_locations(TEMPLATES_DIR):
        dest_dir = os.path.join(OUTPUT_DIR, "csv-templates", location.relative_path)
        os.makedirs(dest_dir, exist_ok=True)
        if os.path.exists(location.csv_path):
            shutil.copy2(location.csv_path, os.path.join(dest_dir, "template.csv"))
        if os.path.exists(location.readme_path):
            shutil.copy2(location.readme_path, os.path.join(dest_dir, "README.md"))

    # Copy each prompt template's prompt.md and README.md into the output directory
    if os.path.isdir(PROMPT_TEMPLATES_DIR):
        for slug in os.listdir(PROMPT_TEMPLATES_DIR):
            template_dir = os.path.join(PROMPT_TEMPLATES_DIR, slug)
            if not os.path.isdir(template_dir):
                continue
            dest_dir = os.path.join(OUTPUT_DIR, "prompt-templates", slug)
            os.makedirs(dest_dir, exist_ok=True)
            prompt_src = os.path.join(template_dir, "prompt.md")
            if os.path.exists(prompt_src):
                shutil.copy2(prompt_src, os.path.join(dest_dir, "prompt.md"))
            readme_src = os.path.join(template_dir, "README.md")
            if os.path.exists(readme_src):
                shutil.copy2(readme_src, os.path.join(dest_dir, "README.md"))

    templates = load_templates()
    spotlight = get_spotlight_template(templates)
    html = generate_html(templates, spotlight, integrity=integrity)

    output_path = os.path.join(OUTPUT_DIR, "index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    # Build-time assertion: data island must be present and round-trip cleanly
    assert_data_island(output_path)

    print(f"✅ Gallery generated: {output_path} ({len(templates)} templates)")


if __name__ == "__main__":
    main()
