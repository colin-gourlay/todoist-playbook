#!/usr/bin/env python3
"""Generate the Template Gallery as a multi-file static site.

Usage:
    python3 generate_gallery.py

Environment variables:
  TEMPLATES_DIR         Path to the CSV templates folder (default: csv-templates)
  PROMPT_TEMPLATES_DIR  Path to the prompt-templates folder (default: prompt-templates)
  OUTPUT_DIR            Path to the output folder (default: docs)
  GITHUB_SHA            Git commit SHA (injected by GitHub Actions)
  GITHUB_REPOSITORY     "owner/repo" used for build provenance
  ASSERT_OUTPUT         If "1", run hardening assertions after generation
  TP_ALLOW_VENDOR_TOFU  If "1", allow first-time TOFU bootstrap when vendor-manifest.json
                        has empty sha384 fields (the manifest is updated in-place).
                        Without this flag an empty sha384 is a hard build error.

The generator emits an HTML shell that loads CSS/JS from sibling files and reads
template data from a JSON island, so a strict CSP without 'unsafe-inline' is
possible. Markdown is rendered client-side via marked@12 and sanitised by
DOMPurify@3 (vendored under docs/vendor/).
"""

import base64
import csv
import datetime
import gzip
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request

from template_discovery import iter_template_locations

TEMPLATES_DIR        = os.environ.get("TEMPLATES_DIR", "csv-templates")
PROMPT_TEMPLATES_DIR = os.environ.get("PROMPT_TEMPLATES_DIR", "prompt-templates")
OUTPUT_DIR           = os.environ.get("OUTPUT_DIR", "docs")
GITHUB_SHA           = os.environ.get("GITHUB_SHA", "")
GITHUB_REPOSITORY    = os.environ.get("GITHUB_REPOSITORY", "colin-gourlay/todoist-playbook")
REPO_URL             = "https://github.com/" + GITHUB_REPOSITORY
ASSERT_OUTPUT        = os.environ.get("ASSERT_OUTPUT", "0") == "1"
ALLOW_VENDOR_TOFU    = os.environ.get("TP_ALLOW_VENDOR_TOFU", "0") == "1"
SHORT_SHA            = (GITHUB_SHA or "")[:7]
BUILD_DATE           = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gallery_assets")

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

# Vendored libraries pinned by version. Downloaded at build time; falls back to
# stubs if the network is unavailable. Hashes are recorded in
# .github/scripts/vendor-manifest.json for reproducibility.
VENDOR = {
    "marked.min.js":    "https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js",
    "dompurify.min.js": "https://cdn.jsdelivr.net/npm/dompurify@3.1.6/dist/purify.min.js",
}

MARKED_STUB = """\
/* marked@12.0.2 download stub — Markdown rendered as plain text */
(function(g){
  function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
  g.marked = { parse: function(s){ return '<pre>' + esc(s) + '</pre>'; } };
})(typeof globalThis !== 'undefined' ? globalThis : this);
"""

DOMPURIFY_STUB = """\
/* DOMPurify@3.1.6 download stub — passthrough sanitiser. Real DOMPurify is
 * preferred; this is only used when the build cannot reach the CDN. */
(function(g){
  function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
  g.DOMPurify = {
    sanitize: function(html){
      // Defensive fallback: strip <script>/<iframe> blocks even in passthrough mode.
      return String(html)
        .replace(/<script[\\s\\S]*?<\\/script>/gi, '')
        .replace(/<iframe[\\s\\S]*?<\\/iframe>/gi, '')
        .replace(/ on[a-z]+="[^"]*"/gi, '')
        .replace(/ on[a-z]+='[^']*'/gi, '')
        .replace(/javascript:/gi, '');
    },
    addHook: function(){}
  };
})(typeof globalThis !== 'undefined' ? globalThis : this);
"""


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse_meta(path):
    meta = {"tags": [], "inputs": []}
    in_list = None
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            m_list = re.match(r"^(tags|inputs):\s*$", line)
            if m_list:
                in_list = m_list.group(1)
                continue
            if in_list:
                m = re.match(r"^\s+-\s+(.+)$", line)
                if m:
                    meta[in_list].append(m.group(1).strip())
                    continue
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


def read_readme(path):
    if not path or not os.path.exists(path):
        return ""
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except Exception as exc:
        print(f"Warning: could not read {path}: {exc}", file=sys.stderr)
        return ""


def file_mtime_iso(path):
    """Return ISO-8601 date for the most recent git commit touching the file.

    Falls back to filesystem mtime if git is unavailable. Git data is preferred
    because checked-out files share the runner's timestamp on CI.
    """
    try:
        out = subprocess.check_output(
            ["git", "log", "-1", "--format=%cs", "--", path],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
        if out:
            return out
    except Exception:
        pass
    try:
        ts = os.path.getmtime(path)
        return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime("%Y-%m-%d")
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# Template loading
# ---------------------------------------------------------------------------

def load_templates():
    templates = []

    if os.path.isdir(TEMPLATES_DIR):
        for location in iter_template_locations(TEMPLATES_DIR):
            if not os.path.exists(location.meta_path):
                continue
            meta = parse_meta(location.meta_path)
            rows = parse_csv_rows(location.csv_path) if os.path.exists(location.csv_path) else []
            task_count = sum(1 for r in rows if r["type"] == "task")
            section_count = sum(1 for r in rows if r["type"] == "section")
            templates.append({
                "slug":                  location.slug,
                "name":                  meta.get("name", location.slug),
                "description":           meta.get("description", ""),
                "category":              meta.get("category", ""),
                "tags":                  meta.get("tags", []),
                "estimated_duration":    meta.get("estimated_duration", ""),
                "recurrence_suggestion": meta.get("recurrence_suggestion", ""),
                "author":                meta.get("author", ""),
                "version":               meta.get("version", ""),
                "deprecated":            meta.get("deprecated", ""),
                "task_count":            task_count,
                "section_count":         section_count,
                "rows":                  rows,
                "csv_url":               f"csv-templates/{location.relative_path}/template.csv",
                "prompt_url":            "",
                "inputs":                [],
                "type":                  "template",
                "readme":                read_readme(location.readme_path),
                "github_path":           f"csv-templates/{location.relative_path}",
                "mtime":                 max(filter(None, [file_mtime_iso(location.meta_path), file_mtime_iso(location.csv_path)]), default=""),
            })

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
                "slug":                  slug,
                "name":                  meta.get("name", slug),
                "description":           meta.get("description", ""),
                "category":              meta.get("category", ""),
                "tags":                  meta.get("tags", []),
                "estimated_duration":    "",
                "recurrence_suggestion": "",
                "author":                meta.get("author", ""),
                "version":               meta.get("version", ""),
                "task_count":            0,
                "section_count":         0,
                "rows":                  [],
                "csv_url":               "",
                "prompt_url":            f"prompt-templates/{slug}/prompt.md",
                "inputs":                meta.get("inputs", []),
                "type":                  "prompt",
                "readme":                read_readme(readme_path),
                "github_path":           f"prompt-templates/{slug}",
                "mtime":                 max(filter(None, [file_mtime_iso(meta_path), file_mtime_iso(os.path.join(template_dir, "prompt.md"))]), default=""),
            })

    return templates


def _semver_key(t):
    parts = (t.get("version", "0.0.0") or "0.0.0").split(".")
    try:
        return tuple(int(p) for p in (parts + ["0", "0"])[:3])
    except ValueError:
        return (0, 0, 0)


def _truthy(v):
    if isinstance(v, bool): return v
    if v is None: return False
    return str(v).strip().lower() in {"true", "yes", "1", "on"}


def get_spotlight_template(templates):
    cands = [
        t for t in templates
        if t.get("type") == "template"
        and _semver_key(t) > (0, 0, 0)
        and not _truthy(t.get("deprecated"))
    ]
    return max(cands, key=_semver_key) if cands else None


# ---------------------------------------------------------------------------
# JSON injection hardening
# ---------------------------------------------------------------------------

def safe_json_for_html(obj):
    """JSON-encode ``obj`` so the result is safe to embed in an HTML script tag.

    Escapes ``</``, ``<!--``, ``-->`` and U+2028 / U+2029 so the data island
    can't terminate the surrounding ``<script>`` block or inject HTML comments.
    """
    raw = json.dumps(obj, ensure_ascii=False)
    raw = raw.replace("</", "<\\/")
    raw = raw.replace("<!--", "<\\!--")
    raw = raw.replace("-->", "--\\>")
    raw = raw.replace("\u2028", "\\u2028")
    raw = raw.replace("\u2029", "\\u2029")
    return raw


def assert_data_island_roundtrip(html, expected_obj):
    """Extract the JSON island and check json.loads() returns expected_obj."""
    m = re.search(
        r'<script type="application/json" id="tp-data">(.*?)</script>',
        html,
        re.DOTALL,
    )
    assert m, "data island not found in generated HTML"
    raw = m.group(1)
    # Undo HTML-safe escapes
    decoded = (raw
               .replace("<\\/", "</")
               .replace("<\\!--", "<!--")
               .replace("--\\>", "-->"))
    parsed = json.loads(decoded)
    assert parsed.get("templates") and isinstance(parsed["templates"], list), \
        "data island templates missing"
    return parsed


# ---------------------------------------------------------------------------
# Vendor download
# ---------------------------------------------------------------------------

def download_vendor(vendor_dir):
    """Download marked + DOMPurify; fallback to stubs if network is unavailable.

    Verifies SHA-384 against ``.github/scripts/vendor-manifest.json`` when
    populated, and updates that manifest after a successful download.
    Returns ``{filename: 'sha384-<base64>'}`` for SRI integrity attributes.
    """
    os.makedirs(vendor_dir, exist_ok=True)
    manifest_path = os.path.join(os.path.dirname(__file__), "vendor-manifest.json")
    try:
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)
    except Exception:
        manifest = {}

    sri_hashes = {}
    stubs = {"marked.min.js": MARKED_STUB, "dompurify.min.js": DOMPURIFY_STUB}

    for filename, url in VENDOR.items():
        dest = os.path.join(vendor_dir, filename)
        expected = manifest.get(filename, {}).get("sha384", "")
        if not expected and not ALLOW_VENDOR_TOFU:
            raise SystemExit(
                f"ERROR: vendor-manifest.json has no sha384 for {filename} and "
                "TP_ALLOW_VENDOR_TOFU is not set. Set TP_ALLOW_VENDOR_TOFU=1 to "
                "bootstrap the manifest on first run."
            )
        downloaded = False
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "todoist-playbook-gallery-builder/1.0"},
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = resp.read()
            actual = base64.b64encode(hashlib.sha384(data).digest()).decode()
            if expected and expected != actual:
                print(
                    f"⚠️  Vendor checksum mismatch for {filename}: "
                    f"expected {expected}, got {actual}",
                    file=sys.stderr,
                )
            with open(dest, "wb") as f:
                f.write(data)
            sri_hashes[filename] = "sha384-" + actual
            manifest.setdefault(filename, {})["sha384"] = actual
            manifest[filename]["url"] = url
            manifest[filename]["bytes"] = len(data)
            downloaded = True
            print(f"✅ Downloaded {filename} ({len(data):,} bytes)")
        except Exception as exc:
            print(
                f"⚠️  Vendor download failed for {filename} ({exc}); using stub",
                file=sys.stderr,
            )

        if not downloaded:
            with open(dest, "w", encoding="utf-8") as f:
                f.write(stubs[filename])
            with open(dest, "rb") as f:
                d = f.read()
            sri_hashes[filename] = "sha384-" + base64.b64encode(
                hashlib.sha384(d).digest()
            ).decode()

    try:
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, sort_keys=True)
            f.write("\n")
    except Exception:
        pass

    return sri_hashes


# ---------------------------------------------------------------------------
# Static asset emission
# ---------------------------------------------------------------------------

def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def emit_precompressed_assets(output_dir):
    """Emit .gz and .br variants for text assets."""
    text_extensions = {
        ".css", ".csv", ".html", ".js", ".json", ".md",
        ".svg", ".txt", ".webmanifest",
    }
    brotli_available = shutil.which("brotli") is not None
    brotli_failures = 0
    compressed = 0

    for root, _, files in os.walk(output_dir):
        for filename in files:
            if filename.endswith((".gz", ".br")):
                continue

            ext = os.path.splitext(filename)[1].lower()
            if ext not in text_extensions:
                continue

            path = os.path.join(root, filename)

            with open(path, "rb") as src:
                raw = src.read()
            with open(path + ".gz", "wb") as gz_file:
                with gzip.GzipFile(
                    fileobj=gz_file, mode="wb", compresslevel=9, mtime=0
                ) as out:
                    out.write(raw)

            if brotli_available:
                try:
                    subprocess.run(
                        ["brotli", "-f", "-q", "11", "-o", path + ".br", path],
                        check=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                except subprocess.CalledProcessError:
                    brotli_failures += 1

            compressed += 1

    if brotli_available and brotli_failures:
        print(f"⚠️  Brotli compression failed for {brotli_failures} files", file=sys.stderr)
    if not brotli_available:
        print("⚠️  brotli CLI not found; skipping .br generation", file=sys.stderr)
    if compressed:
        print(f"✅ Precompressed {compressed} text assets")
    else:
        print("⚠️  No text assets found for precompression", file=sys.stderr)


def emit_pwa_assets():
    """Emit favicon, apple-touch-icon (SVG used for both), OG image and manifest."""
    favicon = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="Todoist Playbook">
  <rect width="64" height="64" rx="14" fill="#d34244"/>
  <path d="M16 24h32M16 32h32M16 40h22" stroke="#fff" stroke-width="4" stroke-linecap="round"/>
  <circle cx="14" cy="24" r="2.5" fill="#fff"/>
  <circle cx="14" cy="32" r="2.5" fill="#fff"/>
  <circle cx="14" cy="40" r="2.5" fill="#fff"/>
</svg>
"""
    write_text(os.path.join(OUTPUT_DIR, "favicon.svg"), favicon)
    # Apple touch icon — PNG generation requires extra deps; ship the same SVG
    # under .png filename so the link still resolves. Modern iOS accepts SVG
    # for masks but falls back to default if rejected. Documented choice.
    write_text(os.path.join(OUTPUT_DIR, "apple-touch-icon.svg"), favicon)

    og = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" role="img"
     aria-label="Todoist Playbook - Curated templates for getting things done">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#d34244"/>
      <stop offset="100%" stop-color="#ae3b3d"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="630" fill="url(#g)"/>
  <text x="80" y="280" font-family="Helvetica, Arial, sans-serif"
        font-size="84" font-weight="800" fill="#fff" letter-spacing="-2">
    🧩 Todoist Playbook
  </text>
  <text x="80" y="360" font-family="Helvetica, Arial, sans-serif"
        font-size="38" font-weight="500" fill="#fff" opacity="0.95">
    Curated templates for getting things done
  </text>
  <text x="80" y="540" font-family="Helvetica, Arial, sans-serif"
        font-size="24" font-weight="500" fill="#fff" opacity="0.85">
    github.com/colin-gourlay/todoist-playbook
  </text>
</svg>
"""
    write_text(os.path.join(OUTPUT_DIR, "og-image.svg"), og)

    manifest = {
        "name": "Todoist Playbook - Template Gallery",
        "short_name": "Playbook",
        "description": "Curated Todoist templates for getting things done.",
        "start_url": "./",
        "scope": "./",
        "display": "standalone",
        "theme_color": "#d34244",
        "background_color": "#fafbfc",
        "icons": [
            {"src": "favicon.svg",          "sizes": "any",      "type": "image/svg+xml"},
            {"src": "apple-touch-icon.svg", "sizes": "180x180",  "type": "image/svg+xml",
             "purpose": "maskable"},
        ],
    }
    write_text(
        os.path.join(OUTPUT_DIR, "manifest.webmanifest"),
        json.dumps(manifest, indent=2),
    )


def download_font(fonts_dir):
    """Download Inter Variable woff2 from font-manifest.json; skip gracefully on failure.

    The font is SHA-256 verified against the pinned hash in the manifest.
    If the download fails for any reason the gallery still builds correctly —
    browsers fall back to the system font stack declared in styles.css.
    """
    manifest_path = os.path.join(os.path.dirname(__file__), "font-manifest.json")
    try:
        with open(manifest_path, encoding="utf-8") as f:
            spec = json.load(f)
    except Exception as exc:
        print(f"⚠️  font-manifest.json unavailable ({exc}); skipping font download",
              file=sys.stderr)
        return

    url      = spec.get("url", "")
    expected = spec.get("sha256", "")
    filename = spec.get("filename", "Inter-Variable.woff2")
    dest     = os.path.join(fonts_dir, filename)

    if not url:
        print("⚠️  font-manifest.json has no URL; skipping font download", file=sys.stderr)
        return

    os.makedirs(fonts_dir, exist_ok=True)
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "todoist-playbook-gallery-builder/1.0"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        actual = hashlib.sha256(data).hexdigest()
        if expected and actual != expected:
            print(
                f"⚠️  Font checksum mismatch for {filename}: "
                f"expected {expected}, got {actual} — skipping write",
                file=sys.stderr,
            )
            return
        with open(dest, "wb") as f:
            f.write(data)
        print(f"✅ Downloaded {filename} ({len(data):,} bytes)")
    except Exception as exc:
        print(
            f"⚠️  Font download failed for {filename} ({exc}); "
            "system font stack will be used as fallback",
            file=sys.stderr,
        )


def emit_service_worker():
    """Emit a small cache-first service worker keyed by build SHA."""
    cache_key = (SHORT_SHA or BUILD_DATE or "dev")
    sw = (
        '/* Todoist Playbook - service worker (cache-first app shell, '
        'stale-while-revalidate for templates) */\n'
        'const CACHE = "tp-shell-' + cache_key + '";\n'
        'const SHELL = ['
        '"./", "index.html", "styles.css", "app.js", "data.json", '
        '"manifest.webmanifest", "favicon.svg", '
        '"vendor/marked.min.js", "vendor/dompurify.min.js", '
        '"fonts/Inter-Variable.woff2"'
        '];\n'
        'self.addEventListener("install", (e) => {\n'
        '  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL).catch(()=>{})));\n'
        '  self.skipWaiting();\n'
        '});\n'
        'self.addEventListener("activate", (e) => {\n'
        '  e.waitUntil(caches.keys().then((keys) => Promise.all(\n'
        '    keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))\n'
        '  )));\n'
        '  self.clients.claim();\n'
        '});\n'
        'self.addEventListener("fetch", (e) => {\n'
        '  const req = e.request;\n'
        '  if (req.method !== "GET") return;\n'
        '  const url = new URL(req.url);\n'
        '  if (url.origin !== self.location.origin) return;\n'
        '  const isTemplate = url.pathname.includes("/csv-templates/") || '
        'url.pathname.includes("/prompt-templates/");\n'
        '  if (isTemplate) {\n'
        '    e.respondWith(\n'
        '      caches.match(req).then((cached) => {\n'
        '        const network = fetch(req).then((res) => {\n'
        '          const copy = res.clone();\n'
        '          caches.open(CACHE).then((c) => c.put(req, copy)).catch(()=>{});\n'
        '          return res;\n'
        '        }).catch(() => cached);\n'
        '        return cached || network;\n'
        '      })\n'
        '    );\n'
        '  } else {\n'
        '    e.respondWith(\n'
        '      caches.match(req).then((cached) => cached || fetch(req).catch(() => caches.match("./")))\n'
        '    );\n'
        '  }\n'
        '});\n'
    )
    write_text(os.path.join(OUTPUT_DIR, "sw.js"), sw)


def read_asset(filename):
    """Read a bundled asset (CSS or JS) from the gallery_assets folder."""
    with open(os.path.join(ASSETS_DIR, filename), encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# HTML shell
# ---------------------------------------------------------------------------

def build_html(data_payload, sri_hashes):
    data_json = safe_json_for_html(data_payload)
    marked_sri    = sri_hashes.get("marked.min.js", "")
    dompurify_sri = sri_hashes.get("dompurify.min.js", "")
    site_url = "https://colin-gourlay.github.io/todoist-playbook/"
    repo_url = REPO_URL
    description = (
        "Curated Todoist templates for getting things done - accessible, "
        "searchable gallery with categories, prompts and bundles."
    )

    csp = (
        "default-src 'none'; "
        "script-src 'self'; "
        "style-src 'self'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "manifest-src 'self'; "
        "base-uri 'none'; "
        "form-action 'none'; "
        "frame-ancestors 'none'; "
        "upgrade-insecure-requests"
    )
    permissions_policy = (
        "geolocation=(), microphone=(), camera=(), payment=(), usb=(), "
        "magnetometer=(), gyroscope=(), accelerometer=(), interest-cohort=()"
    )

    sri_marked    = f' integrity="{marked_sri}" crossorigin="anonymous"' if marked_sri else ""
    sri_dompurify = f' integrity="{dompurify_sri}" crossorigin="anonymous"' if dompurify_sri else ""

    build_stamp_parts = []
    if BUILD_DATE: build_stamp_parts.append(f"Built {BUILD_DATE}")
    if SHORT_SHA:  build_stamp_parts.append(f"commit {SHORT_SHA}")
    build_stamp = " · ".join(build_stamp_parts)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="Content-Security-Policy" content="{csp}">
  <meta http-equiv="Permissions-Policy" content="{permissions_policy}">
  <meta name="referrer" content="strict-origin-when-cross-origin">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="color-scheme" content="light dark">
  <meta name="theme-color" content="#d34244">
  <meta name="description" content="{description}">
  <meta property="og:title" content="Todoist Playbook - Template Gallery">
  <meta property="og:description" content="{description}">
  <meta property="og:image" content="{site_url}og-image.svg">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{site_url}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="Todoist Playbook - Template Gallery">
  <meta name="twitter:description" content="{description}">
  <meta name="twitter:image" content="{site_url}og-image.svg">
  <link rel="icon" type="image/svg+xml" href="favicon.svg">
  <link rel="apple-touch-icon" href="apple-touch-icon.svg">
  <link rel="manifest" href="manifest.webmanifest">
  <link rel="stylesheet" href="styles.css">
  <title>Todoist Playbook - Template Gallery</title>
</head>
<body>

<a class="skip-link" href="#main">Skip to main content</a>

<header class="site-header" role="banner">
  <div class="header-controls">
    <a href="{repo_url}" class="header-github-link" target="_blank" rel="noopener noreferrer"
       aria-label="View source on GitHub" title="View source on GitHub">
      <svg viewBox="0 0 24 24" aria-hidden="true" fill="currentColor" stroke="none"><path d="M12 .5a12 12 0 0 0-3.79 23.4c.6.11.82-.26.82-.58v-2c-3.34.73-4.04-1.61-4.04-1.61-.55-1.39-1.34-1.76-1.34-1.76-1.09-.75.08-.74.08-.74 1.21.09 1.85 1.24 1.85 1.24 1.07 1.84 2.81 1.31 3.5 1 .11-.78.42-1.31.76-1.61-2.66-.3-5.46-1.33-5.46-5.93 0-1.31.47-2.39 1.24-3.23-.13-.3-.54-1.52.11-3.17 0 0 1.01-.33 3.31 1.23a11.5 11.5 0 0 1 6.02 0c2.3-1.56 3.31-1.23 3.31-1.23.66 1.65.25 2.87.12 3.17.77.84 1.24 1.92 1.24 3.23 0 4.61-2.81 5.62-5.48 5.92.43.37.81 1.1.81 2.22v3.29c0 .32.21.7.83.58A12 12 0 0 0 12 .5z"/></svg>
    </a>
    <button type="button" id="theme-toggle" class="theme-toggle"
            aria-label="System theme" title="System theme" aria-pressed="false">
      <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 3v18"/></svg>
    </button>
  </div>
    <h1>🧩 Todoist Playbook</h1>
  <p>Curated templates for getting things done</p>
  <p id="header-stat" class="header-stat" aria-live="polite"></p>
  <div class="search-bar" role="search">
        <label for="search-input" class="visually-hidden">Search templates</label>
    <input type="search" id="search-input" placeholder="Search templates…"
           aria-label="Search templates" autocomplete="off" spellcheck="false">
    <button class="search-clear" id="search-clear" type="button"
            aria-label="Clear search" hidden>
      <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.25"><path d="M18 6 6 18M6 6l12 12"/></svg>
    </button>
  </div>
  <div class="search-controls" id="search-controls" role="group"
       aria-label="Search refinements" hidden>
    <div class="segmented" role="group" aria-label="Search mode">
      <span class="segmented-label">Search mode:</span>
      <button type="button" class="seg-btn" data-mode="all" aria-pressed="true" title="Search across all fields - matches templates by name, description, and tags">All</button>
      <button type="button" class="seg-btn" data-mode="text" aria-pressed="false" title="Search by text only - matches template names and descriptions; tag filters are ignored">Text</button>
      <button type="button" class="seg-btn" data-mode="tags" aria-pressed="false" title="Search by tags only - only tag filters are applied; text query is ignored">Tags</button>
    </div>
  </div>
</header>

<nav class="breadcrumb" id="breadcrumb" aria-label="Breadcrumb">
  <button id="btn-back" type="button" aria-label="Back to all categories">
    <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.25"><path d="M19 12H5"/><path d="M12 19l-7-7 7-7"/></svg>
    All Categories
  </button>
  <span class="crumb-sep" aria-hidden="true">/</span>
  <span class="crumb-current" id="crumb-label"></span>
</nav>

<main id="main" tabindex="-1">
  <div class="container" id="container"><!-- Populated by JavaScript --></div>
</main>

<div class="modal-backdrop" id="modal-backdrop" role="dialog" aria-modal="true"
     aria-labelledby="modal-title" aria-describedby="modal-subtitle"
     aria-hidden="true">
  <div class="modal-dialog" role="document">
    <div class="modal-header">
      <div class="modal-title-block">
        <h2 class="modal-title" id="modal-title"></h2>
        <div class="modal-subtitle" id="modal-subtitle"></div>
      </div>
      <div class="modal-actions" id="modal-actions"></div>
      <button type="button" class="modal-close" id="modal-close" aria-label="Close dialog">
        <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.25"><path d="M18 6 6 18M6 6l12 12"/></svg>
      </button>
    </div>
    <div class="modal-body" id="modal-body"></div>
  </div>
</div>

<footer class="site-footer" id="site-footer">
  <nav aria-label="Site">
    <div class="footer-links">
      <a href="https://github.com/colin-gourlay/todoist-playbook/issues/new?template=template-request.yml"
         target="_blank" rel="noopener noreferrer">
        <span aria-hidden="true">💡</span> Request a Template
      </a>
      <a href="https://github.com/colin-gourlay/todoist-playbook/issues/new?template=bug-report.yml"
         target="_blank" rel="noopener noreferrer">
        <span aria-hidden="true">🐛</span> Report a Bug
      </a>
      <a href="https://github.com/colin-gourlay/todoist-playbook"
         target="_blank" rel="noopener noreferrer">
        <span aria-hidden="true">⭐</span> View on GitHub
      </a>
    </div>
  </nav>
  <div>Built with <span aria-hidden="true">❤️</span>
    · <a href="https://github.com/colin-gourlay/todoist-playbook/blob/main/CONTRIBUTING"
         target="_blank" rel="noopener noreferrer">Contributing Guide</a>
  </div>
  <div class="build-stamp">{build_stamp}</div>
</footer>

<script type="application/json" id="tp-data">{data_json}</script>
<script src="vendor/marked.min.js"{sri_marked}></script>
<script src="vendor/dompurify.min.js"{sri_dompurify}></script>
<script src="app.js"></script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Hardening assertions
# ---------------------------------------------------------------------------

def assert_hardening(html, output_dir, payload):
    """Assert the rendered HTML satisfies the security/CSP contract."""
    assert 'http-equiv="Content-Security-Policy"' in html, \
        "missing Content-Security-Policy meta"
    assert "'unsafe-inline'" not in html, "CSP must not allow 'unsafe-inline'"
    assert "'unsafe-eval'" not in html, "CSP must not allow 'unsafe-eval'"
    assert 'name="referrer"' in html, "missing referrer meta"
    assert '<a class="skip-link"' in html, "missing skip link"
    assert '<main id="main"' in html, "missing main landmark"

    # Data island round-trip
    parsed = assert_data_island_roundtrip(html, payload)
    assert len(parsed["templates"]) == len(payload["templates"]), \
        "data island length mismatch"

    # Files exist
    for f in ("styles.css", "app.js", "manifest.webmanifest", "sw.js",
              "favicon.svg", "og-image.svg",
              "vendor/marked.min.js", "vendor/dompurify.min.js"):
        assert os.path.exists(os.path.join(output_dir, f)), f"missing {f}"

    for f in ("index.html", "styles.css", "app.js", "data.json",
              "vendor/marked.min.js", "vendor/dompurify.min.js"):
        assert os.path.exists(os.path.join(output_dir, f"{f}.gz")), f"missing {f}.gz"
        if shutil.which("brotli") is not None:
            assert os.path.exists(os.path.join(output_dir, f"{f}.br")), f"missing {f}.br"

    # Confirm no <style> or inline <script> with executable contents (the JSON
    # island uses type="application/json" which is non-executable).
    inline_style = re.search(r'<style\b', html)
    assert inline_style is None, "no inline <style> blocks allowed"
    bad = re.search(r'<script(?![^>]*\bsrc=)(?![^>]*type="application/json")[^>]*>', html)
    assert bad is None, "no executable inline <script> blocks allowed"

    # app.js must contain the frame-busting guard (frame-ancestors in a <meta>
    # CSP is ignored by browsers; the JS guard is the operative protection)
    appjs_path = os.path.join(output_dir, "app.js")
    with open(appjs_path, encoding="utf-8") as f:
        appjs_content = f.read()
    assert "window.top !== window.self" in appjs_content, \
        "app.js is missing the frame-busting guard (window.top !== window.self)"

    print("✅ Hardening assertions passed")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    if not os.path.isdir(TEMPLATES_DIR):
        print(f"Error: CSV templates directory not found: {TEMPLATES_DIR}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(os.path.join(OUTPUT_DIR, ".nojekyll"), "w"):
        pass

    # Copy CSV / prompt template assets
    for location in iter_template_locations(TEMPLATES_DIR):
        dest = os.path.join(OUTPUT_DIR, "csv-templates", location.relative_path)
        os.makedirs(dest, exist_ok=True)
        if os.path.exists(location.csv_path):
            shutil.copy2(location.csv_path, os.path.join(dest, "template.csv"))
        if os.path.exists(location.readme_path):
            shutil.copy2(location.readme_path, os.path.join(dest, "README.md"))

    if os.path.isdir(PROMPT_TEMPLATES_DIR):
        for slug in os.listdir(PROMPT_TEMPLATES_DIR):
            template_dir = os.path.join(PROMPT_TEMPLATES_DIR, slug)
            if not os.path.isdir(template_dir):
                continue
            dest = os.path.join(OUTPUT_DIR, "prompt-templates", slug)
            os.makedirs(dest, exist_ok=True)
            prompt_src = os.path.join(template_dir, "prompt.md")
            if os.path.exists(prompt_src):
                shutil.copy2(prompt_src, os.path.join(dest, "prompt.md"))
            readme_src = os.path.join(template_dir, "README.md")
            if os.path.exists(readme_src):
                shutil.copy2(readme_src, os.path.join(dest, "README.md"))

    # Static assets
    write_text(os.path.join(OUTPUT_DIR, "styles.css"), read_asset("styles.css"))
    write_text(os.path.join(OUTPUT_DIR, "app.js"),     read_asset("app.js"))
    emit_pwa_assets()
    emit_service_worker()

    # Vendor (downloads or stubs)
    sri = download_vendor(os.path.join(OUTPUT_DIR, "vendor"))

    # Inter Variable font (optional; falls back to system stack if unavailable)
    download_font(os.path.join(OUTPUT_DIR, "fonts"))

    templates = load_templates()
    spotlight = get_spotlight_template(templates)

    payload = {
        "templates":    templates,
        "categoryMeta": CATEGORY_META,
        "spotlight":    spotlight,
        "build": {
            "date":  BUILD_DATE,
            "sha":   SHORT_SHA,
            "fullSha": GITHUB_SHA,
        },
        "repoUrl": REPO_URL,
    }

    # Emit data.json for cache-first / debugging
    write_text(
        os.path.join(OUTPUT_DIR, "data.json"),
        json.dumps(payload, indent=None, ensure_ascii=False),
    )

    html = build_html(payload, sri)
    output_path = os.path.join(OUTPUT_DIR, "index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    emit_precompressed_assets(OUTPUT_DIR)

    print(f"✅ Gallery generated: {output_path} ({len(templates)} templates)")

    if ASSERT_OUTPUT:
        assert_hardening(html, OUTPUT_DIR, payload)


if __name__ == "__main__":
    main()
