#!/usr/bin/env python3
"""Generate a browsable Template Gallery as a self-contained static HTML page.

Usage:
    python3 generate_gallery.py

Environment variables:
    TEMPLATES_DIR   Path to the templates folder (default: templates)
    OUTPUT_DIR      Path to the output folder (default: docs)
"""

import csv
import json
import os
import re
import shutil
import sys

TEMPLATES_DIR = os.environ.get("TEMPLATES_DIR", "templates")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "docs")


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def parse_meta(path):
    """Parse a simple meta.yml file without a YAML library."""
    meta = {"tags": []}
    in_tags = False
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            # Detect the start of a tags block
            if re.match(r"^tags:\s*$", line):
                in_tags = True
                continue
            if in_tags:
                m = re.match(r"^\s+-\s+(.+)$", line)
                if m:
                    meta["tags"].append(m.group(1).strip())
                    continue
                # Any non-indented line ends the tags block
                if line and not line[0].isspace():
                    in_tags = False
            m = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*):\s*(.*)$", line)
            if m:
                key = m.group(1)
                value = m.group(2).strip().strip("\"'")
                if key != "tags":
                    in_tags = False
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

def load_templates():
    templates = []
    for slug in sorted(os.listdir(TEMPLATES_DIR)):
        template_dir = os.path.join(TEMPLATES_DIR, slug)
        if not os.path.isdir(template_dir):
            continue
        meta_path = os.path.join(template_dir, "meta.yml")
        csv_path = os.path.join(template_dir, "template.csv")
        if not os.path.exists(meta_path):
            continue
        meta = parse_meta(meta_path)
        rows = parse_csv_rows(csv_path) if os.path.exists(csv_path) else []
        task_count = sum(1 for r in rows if r["type"] == "task")
        section_count = sum(1 for r in rows if r["type"] == "section")
        templates.append({
            "slug": slug,
            "name": meta.get("name", slug),
            "description": meta.get("description", ""),
            "category": meta.get("category", ""),
            "tags": meta.get("tags", []),
            "estimated_duration": meta.get("estimated_duration", ""),
            "recurrence_suggestion": meta.get("recurrence_suggestion", ""),
            "author": meta.get("author", ""),
            "version": meta.get("version", ""),
            "task_count": task_count,
            "section_count": section_count,
            "rows": rows,
            "csv_url": f"templates/{slug}/template.csv",
        })
    return templates


# ---------------------------------------------------------------------------
# HTML generation
# ---------------------------------------------------------------------------

def generate_html(templates):
    all_tags = sorted({tag for t in templates for tag in t["tags"]})
    templates_json = json.dumps(templates, ensure_ascii=False)
    all_tags_json = json.dumps(all_tags, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Todoist Playbook — Template Gallery</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    :root {{
      --red: #db4035;
      --red-dark: #b83227;
      --bg: #f5f5f5;
      --card-bg: #ffffff;
      --text: #202020;
      --muted: #666666;
      --border: #e0e0e0;
      --tag-bg: #f0f0f0;
      --tag-active-bg: #db4035;
      --tag-active-text: #ffffff;
      --section-color: #7b68ee;
      --radius: 8px;
      --shadow: 0 1px 4px rgba(0,0,0,0.08);
    }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
      min-height: 100vh;
    }}

    header {{
      background: var(--red);
      color: #fff;
      padding: 1.5rem 1rem;
      text-align: center;
    }}
    header h1 {{ font-size: 1.6rem; font-weight: 700; letter-spacing: -0.02em; }}
    header p {{ margin-top: 0.35rem; opacity: 0.88; font-size: 0.95rem; }}

    .container {{ max-width: 1100px; margin: 0 auto; padding: 1.5rem 1rem; }}

    /* Search */
    .search-bar {{
      display: flex;
      gap: 0.5rem;
      margin-bottom: 1rem;
    }}
    .search-bar input {{
      flex: 1;
      padding: 0.6rem 0.9rem;
      border: 1px solid var(--border);
      border-radius: var(--radius);
      font-size: 1rem;
      outline: none;
      background: var(--card-bg);
      color: var(--text);
    }}
    .search-bar input:focus {{ border-color: var(--red); box-shadow: 0 0 0 2px rgba(219,64,53,0.15); }}

    /* Tag filters */
    .tag-filters {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.4rem;
      margin-bottom: 1.5rem;
    }}
    .tag-btn {{
      padding: 0.3rem 0.7rem;
      border: 1px solid var(--border);
      border-radius: 999px;
      background: var(--tag-bg);
      color: var(--text);
      font-size: 0.8rem;
      cursor: pointer;
      transition: background 0.15s, color 0.15s, border-color 0.15s;
      white-space: nowrap;
    }}
    .tag-btn:hover {{ background: #e0e0e0; }}
    .tag-btn.active {{
      background: var(--tag-active-bg);
      color: var(--tag-active-text);
      border-color: var(--tag-active-bg);
    }}

    /* Results count */
    .results-count {{
      font-size: 0.85rem;
      color: var(--muted);
      margin-bottom: 1rem;
    }}

    /* Grid */
    .gallery {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
      gap: 1.25rem;
    }}

    /* Card */
    .card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      display: flex;
      flex-direction: column;
      overflow: hidden;
      transition: box-shadow 0.15s;
    }}
    .card:hover {{ box-shadow: 0 4px 16px rgba(0,0,0,0.13); }}

    .card-header {{
      padding: 1rem 1rem 0.5rem;
    }}
    .card-category {{
      font-size: 0.72rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--red);
      margin-bottom: 0.3rem;
    }}
    .card-title {{ font-size: 1.1rem; font-weight: 700; }}
    .card-description {{ font-size: 0.88rem; color: var(--muted); margin-top: 0.35rem; }}

    .card-tags {{
      padding: 0.5rem 1rem;
      display: flex;
      flex-wrap: wrap;
      gap: 0.3rem;
    }}
    .tag {{
      padding: 0.18rem 0.55rem;
      background: var(--tag-bg);
      border-radius: 999px;
      font-size: 0.75rem;
      color: var(--muted);
      cursor: pointer;
      transition: background 0.12s, color 0.12s;
    }}
    .tag:hover {{ background: #e0e0e0; color: var(--text); }}
    .tag.active {{
      background: var(--tag-active-bg);
      color: var(--tag-active-text);
    }}

    .card-stats {{
      padding: 0 1rem 0.5rem;
      display: flex;
      gap: 1rem;
      font-size: 0.8rem;
      color: var(--muted);
    }}
    .card-stats span {{ display: flex; align-items: center; gap: 0.25rem; }}

    /* Preview */
    .card-preview {{
      margin: 0 1rem 0.75rem;
      border: 1px solid var(--border);
      border-radius: var(--radius);
      overflow: hidden;
      font-size: 0.8rem;
    }}
    .preview-row {{
      padding: 0.28rem 0.6rem;
      border-bottom: 1px solid var(--border);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .preview-row:last-child {{ border-bottom: none; }}
    .preview-row.section {{
      font-weight: 600;
      background: #fafafa;
      color: var(--section-color);
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}
    .preview-row.task {{ color: var(--text); padding-left: 1.2rem; }}
    .preview-more {{
      padding: 0.28rem 0.6rem;
      color: var(--muted);
      font-size: 0.75rem;
      background: #fafafa;
    }}

    /* Footer / download */
    .card-footer {{
      padding: 0.75rem 1rem;
      margin-top: auto;
      border-top: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.5rem;
    }}
    .card-meta {{ font-size: 0.75rem; color: var(--muted); }}
    .btn-download {{
      display: inline-flex;
      align-items: center;
      gap: 0.3rem;
      padding: 0.45rem 0.9rem;
      background: var(--red);
      color: #fff;
      border-radius: var(--radius);
      font-size: 0.82rem;
      font-weight: 600;
      text-decoration: none;
      transition: background 0.15s;
      white-space: nowrap;
    }}
    .btn-download:hover {{ background: var(--red-dark); }}

    /* Empty state */
    .empty-state {{
      grid-column: 1 / -1;
      text-align: center;
      padding: 3rem 1rem;
      color: var(--muted);
    }}
    .empty-state p {{ font-size: 1rem; }}

    @media (max-width: 480px) {{
      header h1 {{ font-size: 1.3rem; }}
      .gallery {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>

<header>
  <h1>📋 Todoist Playbook</h1>
  <p>Browse, filter, and download reusable Todoist templates</p>
</header>

<div class="container">
  <div class="search-bar">
    <input type="search" id="search" placeholder="Search templates…" aria-label="Search templates">
  </div>
  <div class="tag-filters" id="tag-filters" aria-label="Filter by tag"></div>
  <p class="results-count" id="results-count"></p>
  <div class="gallery" id="gallery"></div>
</div>

<script>
const TEMPLATES = {templates_json};
const ALL_TAGS  = {all_tags_json};

let activeTag = null;

function escHtml(str) {{
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}}

function formatCategory(cat) {{
  return cat.replace(/-/g, ' ').replace(/\\b\\w/g, c => c.toUpperCase());
}}

function formatDuration(d) {{
  if (!d) return '';
  return d.replace('m', ' min').replace('h', ' hr');
}}

function buildTagFilters() {{
  const container = document.getElementById('tag-filters');
  ALL_TAGS.forEach(tag => {{
    const btn = document.createElement('button');
    btn.className = 'tag-btn';
    btn.textContent = tag;
    btn.dataset.tag = tag;
    btn.addEventListener('click', () => toggleTag(tag));
    container.appendChild(btn);
  }});
}}

function toggleTag(tag) {{
  activeTag = activeTag === tag ? null : tag;
  document.querySelectorAll('.tag-btn').forEach(b => {{
    b.classList.toggle('active', b.dataset.tag === activeTag);
  }});
  render();
}}

function buildPreview(rows) {{
  const MAX_PREVIEW = 8;
  const shown = rows.slice(0, MAX_PREVIEW);
  const rest = rows.length - shown.length;
  let html = '';
  shown.forEach(r => {{
    const cls = r.type === 'section' ? 'section' : 'task';
    // Strip @label tokens from task content for cleaner preview
    const content = r.content.replace(/@[\\w-]+/g, '').trim();
    html += `<div class="preview-row ${{cls}}">${{escHtml(content)}}</div>`;
  }});
  if (rest > 0) {{
    html += `<div class="preview-more">+ ${{rest}} more item${{rest > 1 ? 's' : ''}}</div>`;
  }}
  return html;
}}

function buildCard(t) {{
  const tagHtml = t.tags.map(tag => {{
    const isActive = tag === activeTag;
    return `<span class="tag${{isActive ? ' active' : ''}}" data-tag="${{escHtml(tag)}}">${{escHtml(tag)}}</span>`;
  }}).join('');

  const stats = [];
  if (t.task_count)   stats.push(`<span>✔ ${{t.task_count}} task${{t.task_count !== 1 ? 's' : ''}}</span>`);
  if (t.section_count) stats.push(`<span>▸ ${{t.section_count}} section${{t.section_count !== 1 ? 's' : ''}}</span>`);
  if (t.estimated_duration) stats.push(`<span>⏱ ${{escHtml(formatDuration(t.estimated_duration))}}</span>`);
  if (t.recurrence_suggestion) stats.push(`<span>🔁 ${{escHtml(t.recurrence_suggestion)}}</span>`);

  const previewHtml = t.rows.length ? buildPreview(t.rows) : '';
  const metaLine = [t.author ? `by ${{escHtml(t.author)}}` : '', t.version ? `v${{escHtml(t.version)}}` : ''].filter(Boolean).join(' · ');

  return `
<div class="card" data-slug="${{escHtml(t.slug)}}" data-tags="${{escHtml(t.tags.join(','))}}">
  <div class="card-header">
    ${{t.category ? `<div class="card-category">${{escHtml(formatCategory(t.category))}}</div>` : ''}}
    <div class="card-title">${{escHtml(t.name)}}</div>
    ${{t.description ? `<div class="card-description">${{escHtml(t.description)}}</div>` : ''}}
  </div>
  ${{tagHtml ? `<div class="card-tags">${{tagHtml}}</div>` : ''}}
  ${{stats.length ? `<div class="card-stats">${{stats.join('')}}</div>` : ''}}
  ${{previewHtml ? `<div class="card-preview">${{previewHtml}}</div>` : ''}}
  <div class="card-footer">
    <span class="card-meta">${{metaLine}}</span>
    <a class="btn-download" href="${{escHtml(t.csv_url)}}" download>⬇ Download CSV</a>
  </div>
</div>`;
}}

function matchesSearch(t, query) {{
  if (!query) return true;
  const q = query.toLowerCase();
  return (
    t.name.toLowerCase().includes(q) ||
    t.description.toLowerCase().includes(q) ||
    t.tags.some(tag => tag.toLowerCase().includes(q)) ||
    t.category.toLowerCase().includes(q)
  );
}}

function render() {{
  const query = document.getElementById('search').value.trim();
  const gallery = document.getElementById('gallery');
  const counter = document.getElementById('results-count');

  const visible = TEMPLATES.filter(t =>
    matchesSearch(t, query) &&
    (!activeTag || t.tags.includes(activeTag))
  );

  if (visible.length === 0) {{
    gallery.innerHTML = '<div class="empty-state"><p>No templates match your search.</p></div>';
  }} else {{
    gallery.innerHTML = visible.map(buildCard).join('');
    // Attach tag click handlers on cards
    gallery.querySelectorAll('.tag[data-tag]').forEach(el => {{
      el.addEventListener('click', () => toggleTag(el.dataset.tag));
    }});
  }}

  counter.textContent = `Showing ${{visible.length}} of ${{TEMPLATES.length}} template${{TEMPLATES.length !== 1 ? 's' : ''}}`;
}}

document.getElementById('search').addEventListener('input', render);

buildTagFilters();
render();
</script>

</body>
</html>
"""


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    if not os.path.isdir(TEMPLATES_DIR):
        print(f"Error: templates directory not found: {TEMPLATES_DIR}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Disable Jekyll processing on GitHub Pages
    with open(os.path.join(OUTPUT_DIR, ".nojekyll"), "w"):
        pass

    # Copy each template's CSV into the output directory so download links work
    for slug in os.listdir(TEMPLATES_DIR):
        template_dir = os.path.join(TEMPLATES_DIR, slug)
        csv_src = os.path.join(template_dir, "template.csv")
        if os.path.isdir(template_dir) and os.path.exists(csv_src):
            dest_dir = os.path.join(OUTPUT_DIR, "templates", slug)
            os.makedirs(dest_dir, exist_ok=True)
            shutil.copy2(csv_src, os.path.join(dest_dir, "template.csv"))

    templates = load_templates()
    html = generate_html(templates)

    output_path = os.path.join(OUTPUT_DIR, "index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Gallery generated: {output_path} ({len(templates)} templates)")


if __name__ == "__main__":
    main()
