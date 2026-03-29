#!/usr/bin/env python3
"""Generate a browsable Template Gallery as a self-contained static HTML page.

Usage:
    python3 generate_gallery.py

Environment variables:
  TEMPLATES_DIR         Path to the CSV templates folder (default: csv-templates)
    PROMPT_TEMPLATES_DIR  Path to the prompt-templates folder (default: prompt-templates)
    OUTPUT_DIR            Path to the output folder (default: docs)
"""

import csv
import json
import os
import re
import shutil
import sys

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

def load_templates():
    templates = []

    # Load CSV templates
    if os.path.isdir(TEMPLATES_DIR):
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
                "csv_url": f"csv-templates/{slug}/template.csv",
                "prompt_url": "",
                "inputs": [],
                "type": "template",
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


def get_spotlight_template(templates):
    """Return the template with the highest semantic version, excluding 0.0.0.

    Returns None if all templates are at version 0.0.0 (unreviewed).
    Only regular templates (type == 'template') are considered.
    """
    candidates = [
        t for t in templates
        if t.get("type") == "template" and _semver_key(t) > (0, 0, 0)
    ]
    if not candidates:
        return None
    return max(candidates, key=_semver_key)




def generate_html(templates, spotlight=None):
    templates_json = json.dumps(templates, ensure_ascii=False)
    category_meta_json = json.dumps(CATEGORY_META, ensure_ascii=False)
    spotlight_json = json.dumps(spotlight, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Todoist Playbook — Template Gallery</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    :root {{
      --red: #d34244;
      --red-dark: #a83436;
      --red-light: #fff0ef;
      --red-lighter: #fef8f7;
      --bg: #fafbfc;
      --bg-secondary: #f3f5f7;
      --card-bg: #ffffff;
      --text: #1a202c;
      --text-secondary: #2d3748;
      --muted: #718096;
      --muted-light: #a0aec0;
      --border: #e2e8f0;
      --tag-bg: #edf2f7;
      --tag-text: #2d3748;
      --section-color: #6d28d9;
      --section-bg: #f5f3ff;
      --radius: 8px;
      --radius-lg: 12px;
      --shadow: 0 1px 2px rgba(0,0,0,0.04);
      --shadow-sm: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
      --shadow-md: 0 4px 6px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.05);
      --shadow-lg: 0 10px 15px rgba(0,0,0,0.08), 0 4px 6px rgba(0,0,0,0.05);
      --shadow-hover: 0 20px 25px rgba(0,0,0,0.12), 0 10px 10px rgba(0,0,0,0.04);
      --transition: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                   Helvetica, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.6;
      font-size: 15px;
      min-height: 100vh;
      letter-spacing: -0.01em;
    }}

    /* ── Header ── */
    .site-header {{
      background: linear-gradient(135deg, #d34244 0%, #ae3b3d 100%);
      color: #fff;
      padding: 2.5rem 1rem 2rem;
      text-align: center;
      box-shadow: 0 2px 8px rgba(211, 66, 68, 0.15);
    }}
    .site-header h1 {{
      font-size: 2rem;
      font-weight: 800;
      letter-spacing: -0.04em;
      line-height: 1.2;
    }}
    .site-header p {{
      margin-top: 0.5rem;
      opacity: 0.92;
      font-size: 1.05rem;
      font-weight: 500;
      letter-spacing: -0.01em;
    }}

    /* ── Search bar ── */
    .search-bar {{
      margin: 1.5rem auto 0;
      max-width: 520px;
      position: relative;
    }}
    .search-bar input {{
      width: 100%;
      padding: 0.75rem 2.75rem 0.75rem 1.25rem;
      border: none;
      border-radius: 999px;
      font-size: 0.95rem;
      background: rgba(255,255,255,0.22);
      color: #fff;
      outline: none;
      transition: background var(--transition), box-shadow var(--transition);
      backdrop-filter: blur(8px);
    }}
    .search-bar input::placeholder {{ color: rgba(255,255,255,0.75); font-weight: 500; }}
    .search-bar input:focus {{
      background: rgba(255,255,255,0.32);
      box-shadow: 0 0 0 3px rgba(255,255,255,0.15);
    }}
    .search-bar .search-clear {{
      display: none;
      position: absolute;
      right: 0.75rem;
      top: 50%;
      transform: translateY(-50%);
      background: none;
      border: none;
      cursor: pointer;
      color: rgba(255,255,255,0.85);
      font-size: 1.1rem;
      line-height: 1;
      padding: 0.25rem;
      transition: color var(--transition), transform var(--transition);
    }}
    .search-bar .search-clear:hover {{ color: #fff; transform: translateY(-50%) scale(1.1); }}

    /* ── Search results ── */
    .search-summary {{
      font-size: 0.95rem;
      color: var(--muted);
      margin-bottom: 1.5rem;
      font-weight: 500;
    }}
    .search-summary strong {{ color: var(--text-secondary); font-weight: 700; }}
    .no-results {{
      text-align: center;
      padding: 3.5rem 1rem;
      color: var(--muted);
    }}
    .no-results .no-results-icon {{ font-size: 2.8rem; margin-bottom: 1rem; }}
    .no-results p {{
      font-size: 0.95rem;
      line-height: 1.6;
      max-width: 400px;
      margin: 0 auto;
    }}

    /* ── Breadcrumb bar ── */
    .breadcrumb {{
      display: none;
      background: var(--bg-secondary);
      border-bottom: 1px solid var(--border);
      padding: 0.9rem 1.5rem;
      animation: slideDown 0.25s ease-out;
    }}\n    @keyframes slideDown {{
      from {{ transform: translateY(-8px); opacity: 0; }}
      to {{ transform: translateY(0); opacity: 1; }}
    }}
    .breadcrumb button {{
      background: none;
      border: none;
      cursor: pointer;
      color: var(--red);
      font-size: 0.9rem;
      font-weight: 700;
      display: inline-flex;
      align-items: center;
      gap: 0.3rem;
      padding: 0.25rem 0;
      transition: color var(--transition);
    }}
    .breadcrumb button:hover {{
      color: var(--red-dark);
      text-decoration: underline;
    }}
    .breadcrumb .crumb-sep {{
      color: var(--muted-light);
      margin: 0 0.5rem;
    }}
    .breadcrumb .crumb-current {{
      color: var(--text-secondary);
      font-weight: 700;
      font-size: 0.9rem;
    }}

    /* ── Container ── */
    .container {{ max-width: 1100px; margin: 0 auto; padding: 2.5rem 1.25rem; }}

    /* ── Intro text ── */
    .intro {{
      font-size: 0.95rem;
      color: var(--muted);
      margin-bottom: 2rem;
      font-weight: 500;
    }}
    .intro strong {{ color: var(--text-secondary); font-weight: 600; }}

    /* ── Category grid ── */
    .category-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 1.5rem;
    }}

    /* ── Category card ── */
    .cat-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      box-shadow: var(--shadow-sm);
      padding: 1.75rem;
      cursor: pointer;
      transition: box-shadow var(--transition), transform var(--transition), border-color var(--transition);
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
      color: inherit;
      text-decoration: none;
    }}
    .cat-card:hover {{
      box-shadow: var(--shadow-md);
      transform: translateY(-4px);
      border-color: var(--red-light);
    }}
    .cat-card:focus-visible {{
      outline: 2px solid var(--red);
      outline-offset: 3px;
    }}
    .cat-icon {{ font-size: 2.2rem; line-height: 1; margin-bottom: 0.25rem; }}
    .cat-title {{
      font-size: 1.15rem;
      font-weight: 700;
      line-height: 1.3;
      color: var(--text-secondary);
    }}
    .cat-count {{
      font-size: 0.85rem;
      color: var(--red);
      font-weight: 700;
      letter-spacing: 0.01em;
    }}
    .cat-previews {{
      list-style: none;
      font-size: 0.85rem;
      color: var(--muted);
      display: flex;
      flex-direction: column;
      gap: 0.3rem;
      margin-top: 0.25rem;
    }}
    .cat-previews li::before {{ content: "◆ "; opacity: 0.3; color: var(--red); }}
    .cat-more {{
      font-size: 0.8rem;
      color: var(--muted-light);
      font-style: italic;
      margin-top: 0.25rem;
    }}
    .cat-arrow {{
      margin-top: auto;
      font-size: 0.85rem;
      color: var(--red);
      font-weight: 700;
      transition: transform var(--transition);
      letter-spacing: 0.01em;
    }}
    .cat-card:hover .cat-arrow {{ transform: translateX(3px); }}

    /* ── Category detail heading ── */
    .cat-detail-header {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      margin-bottom: 2rem;
      padding-bottom: 1.5rem;
      border-bottom: 2px solid var(--border);
    }}
    .cat-detail-icon {{ font-size: 2.2rem; line-height: 1; }}
    .cat-detail-title {{
      font-size: 1.5rem;
      font-weight: 800;
      line-height: 1.2;
      color: var(--text-secondary);
    }}
    .cat-detail-count {{
      font-size: 0.9rem;
      color: var(--muted);
      margin-top: 0.2rem;
      font-weight: 500;
    }}

    /* ── Template grid ── */
    .template-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
      gap: 1.5rem;
    }}

    /* ── Template card ── */
    .tpl-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
      overflow: hidden;
      transition: box-shadow var(--transition), border-color var(--transition), transform var(--transition);
    }}
    .tpl-card:hover {{
      box-shadow: var(--shadow-md);
      border-color: var(--border);
      transform: translateY(-2px);
    }}

    .tpl-card-header {{ padding: 1.25rem 1.25rem 0.5rem; }}
    .tpl-type-badge {{
      display: inline-block;
      font-size: 0.7rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--red);
      background: var(--red-light);
      border-radius: 6px;
      padding: 0.25rem 0.65rem;
      margin-bottom: 0.5rem;
    }}
    .tpl-title {{
      font-size: 1.1rem;
      font-weight: 800;
      line-height: 1.3;
      color: var(--text-secondary);
    }}
    .tpl-desc {{
      font-size: 0.9rem;
      color: var(--muted);
      margin-top: 0.4rem;
      line-height: 1.5;
    }}

    .tpl-tags {{
      padding: 0.5rem 1.25rem 0.25rem;
      display: flex;
      flex-wrap: wrap;
      gap: 0.4rem;
    }}
    .tag {{
      padding: 0.2rem 0.65rem;
      background: var(--tag-bg);
      border-radius: 6px;
      font-size: 0.75rem;
      color: var(--tag-text);
      font-weight: 500;
      border: 1px solid transparent;
      transition: border-color var(--transition), background var(--transition);
    }}

    .tpl-stats {{
      padding: 0.25rem 1.25rem 0.5rem;
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem;
      font-size: 0.8rem;
      color: var(--muted);
      font-weight: 500;
    }}

    /* Preview rows */
    .tpl-preview {{
      margin: 0.5rem 1.25rem 0.75rem;
      border: 1px solid var(--border);
      border-radius: 6px;
      overflow: hidden;
      font-size: 0.8rem;
      background: var(--bg-secondary);
    }}
    .preview-row {{
      padding: 0.35rem 0.75rem;
      border-bottom: 1px solid var(--border);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      color: var(--text);
    }}
    .preview-row:last-child {{ border-bottom: none; }}
    .preview-row.section {{
      font-weight: 700;
      background: var(--section-bg);
      color: var(--section-color);
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    .preview-row.task {{
      color: var(--text);
      padding-left: 1.5rem;
      font-weight: 500;
    }}
    .preview-row.task::before {{ content: "▪ "; opacity: 0.4; margin-right: 0.3rem; }}
    .preview-more {{
      padding: 0.35rem 0.75rem;
      color: var(--muted-light);
      font-size: 0.75rem;
      background: var(--section-bg);
      font-weight: 500;
    }}

    /* Prompt inputs */
    .tpl-inputs {{ margin: 0.5rem 1.25rem 0.75rem; font-size: 0.85rem; }}
    .tpl-inputs-label {{ font-weight: 700; color: var(--text-secondary); margin-bottom: 0.35rem; }}
    .input-chip {{
      display: inline-block;
      background: var(--tag-bg);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 0.25rem 0.65rem;
      margin: 0.15rem 0.2rem 0.15rem 0;
      font-size: 0.75rem;
      font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
      color: var(--text);
      font-weight: 500;
    }}

    .tpl-card-footer {{
      padding: 1rem 1.25rem;
      margin-top: auto;
      border-top: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.75rem;
      background: var(--bg-secondary);
    }}
    .tpl-meta {{
      font-size: 0.75rem;
      color: var(--muted-light);
      font-weight: 500;
    }}
    .btn-primary {{
      display: inline-flex;
      align-items: center;
      gap: 0.3rem;
      padding: 0.5rem 1rem;
      background: var(--red);
      color: #fff;
      border-radius: 6px;
      font-size: 0.85rem;
      font-weight: 700;
      text-decoration: none;
      transition: background var(--transition), transform var(--transition), box-shadow var(--transition);
      white-space: nowrap;
      user-select: none;
    }}
    .btn-primary:hover {{
      background: var(--red-dark);
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(211, 66, 68, 0.2);
    }}
    .btn-primary:focus-visible {{
      outline: 2px solid var(--red);
      outline-offset: 2px;
    }}

    /* ── Spotlight ── */
    .spotlight-section {{
      margin-bottom: 3rem;
    }}
    .spotlight-heading {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
      font-size: 0.95rem;
      font-weight: 800;
      color: var(--text-secondary);
      margin-bottom: 1.25rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}
    .spotlight-card {{
      background: linear-gradient(135deg, var(--red-lighter) 0%, #fdfdfe 85%);
      border: 2px solid var(--red);
      border-radius: var(--radius-lg);
      box-shadow: 0 8px 20px rgba(211, 66, 68, 0.12);
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 0;
      overflow: hidden;
    }}
    .spotlight-body {{
      padding: 1.75rem;
    }}
    .spotlight-badge {{
      display: inline-flex;
      align-items: center;
      gap: 0.3rem;
      font-size: 0.7rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--red);
      background: var(--red-light);
      border-radius: 6px;
      padding: 0.3rem 0.7rem;
      margin-bottom: 0.75rem;
    }}
    .spotlight-name {{
      font-size: 1.5rem;
      font-weight: 900;
      margin-bottom: 0.4rem;
      line-height: 1.2;
      color: var(--text-secondary);
    }}
    .spotlight-desc {{
      font-size: 0.95rem;
      color: var(--muted);
      margin-bottom: 1rem;
      line-height: 1.6;
    }}
    .spotlight-tags {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.4rem;
      margin-bottom: 1rem;
    }}
    .spotlight-tags .tag {{ background: rgba(255,255,255,0.5); }}
    .spotlight-stats {{
      display: flex;
      flex-wrap: wrap;
      gap: 1rem;
      font-size: 0.85rem;
      color: var(--muted);
      margin-bottom: 1.25rem;
      font-weight: 500;
    }}
    .spotlight-footer {{
      display: flex;
      align-items: center;
      gap: 1.25rem;
      flex-wrap: wrap;
    }}
    .spotlight-meta {{
      font-size: 0.78rem;
      color: var(--muted-light);
      font-weight: 500;
    }}
    .spotlight-preview {{
      border-left: 2px solid var(--border);
      min-width: 240px;
      max-width: 300px;
      font-size: 0.8rem;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      background: rgba(255,255,255,0.6);
    }}
    .spotlight-preview .preview-row {{
      border-bottom: 1px solid var(--border);
      padding: 0.4rem 0.75rem;
    }}
    .spotlight-preview .preview-row:last-child {{ border-bottom: none; }}
    .spotlight-preview .preview-row.section {{
      background: var(--section-bg);
    }}
    @media (max-width: 680px) {{
      .spotlight-card {{ grid-template-columns: 1fr; }}
      .spotlight-preview {{ border-left: none; border-top: 2px solid var(--border); max-width: 100%; }}
    }}

    /* ── Responsive ── */
    @media (max-width: 640px) {{
      .site-header {{
        padding: 2rem 1rem 1.75rem;
      }}
      .site-header h1 {{ font-size: 1.5rem; }}
      .site-header p {{ font-size: 0.95rem; }}
      .container {{ padding: 2rem 1rem; }}
      .category-grid, .template-grid {{ grid-template-columns: 1fr; gap: 1.25rem; }}
      .search-bar {{ margin: 1.25rem auto 0; }}
      .cat-detail-header {{ flex-direction: column; align-items: flex-start; }}
    }}
    @media (max-width: 768px) {{
      .template-grid {{ grid-template-columns: repeat(auto-fill, minmax(calc(50% - 0.75rem), 1fr)); }}
    }}

    /* ── Footer ── */
    .site-footer {{
      margin-top: 5rem;
      border-top: 1px solid var(--border);
      padding: 2rem 1rem;
      text-align: center;
      font-size: 0.85rem;
      color: var(--muted);
      background: var(--bg-secondary);
    }}
    .site-footer .footer-links {{
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 0.75rem 1.75rem;
      margin-bottom: 1rem;
    }}
    .site-footer a {{
      color: var(--red);
      text-decoration: none;
      font-weight: 700;
      transition: color var(--transition), text-decoration var(--transition);
    }}
    .site-footer a:hover {{
      text-decoration: underline;
      color: var(--red-dark);
    }}
    .site-footer > div {{ color: var(--muted-light); font-weight: 500; }}
  </style>
</head>
<body>

<header class="site-header">
  <h1>📋 Todoist Playbook</h1>
  <p>Curated templates for getting things done</p>
  <div class="search-bar" role="search">
    <input type="search" id="search-input" placeholder="🔍 Search templates…"
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

<footer class="site-footer">
  <div class="footer-links">
    <a href="https://github.com/colin-gourlay/todoist-playbook/issues/new?template=template-request.yml">
      💡 Request a Template
    </a>
    <a href="https://github.com/colin-gourlay/todoist-playbook/issues/new?template=bug-report.yml">
      🐛 Report a Bug
    </a>
    <a href="https://github.com/colin-gourlay/todoist-playbook">
      ⭐ View on GitHub
    </a>
  </div>
  <div>Built with ❤️ · <a href="https://github.com/colin-gourlay/todoist-playbook/blob/main/CONTRIBUTING">Contributing Guide</a></div>
</footer>

<script>
const TEMPLATES = {templates_json};
const CATEGORY_META = {category_meta_json};
const SPOTLIGHT = {spotlight_json};

// Preprocessed lowercase search index — built once at load time
const SEARCH_INDEX = TEMPLATES.map(t => ({{
  template: t,
  name: t.name.toLowerCase(),
  description: t.description.toLowerCase(),
  category: t.category.toLowerCase(),
  tags: t.tags.map(tag => tag.toLowerCase()),
}}));

// ── Helpers ──────────────────────────────────────────────────────────────────

function esc(str) {{
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}}

function catIcon(slug) {{
  return CATEGORY_META[slug] ? CATEGORY_META[slug][0] : '📁';
}}

function catLabel(slug) {{
  if (CATEGORY_META[slug]) return CATEGORY_META[slug][1];
  return slug.replace(/-/g, ' ').replace(/\\b\\w/g, c => c.toUpperCase());
}}

function groupByCategory(templates) {{
  const map = {{}};
  templates.forEach(t => {{
    const c = t.category || 'uncategorised';
    if (!map[c]) map[c] = [];
    map[c].push(t);
  }});
  return map;
}}

function formatDuration(d) {{
  if (!d) return '';
  return d.replace(/m$/, '\u202fmin').replace(/h$/, '\u202fhr');
}}

// ── Category home view ────────────────────────────────────────────────────────

function buildSpotlight(t) {{
  if (!t) return '';

  const tags = t.tags.map(tag => `<span class="tag">${{esc(tag)}}</span>`).join('');

  const stats = [];
  if (t.task_count)    stats.push(`\u2714\ufe0f ${{t.task_count}}\u202ftask${{t.task_count !== 1 ? 's' : ''}}`);
  if (t.section_count) stats.push(`\u25b8 ${{t.section_count}}\u202fsection${{t.section_count !== 1 ? 's' : ''}}`);
  if (t.estimated_duration) stats.push(`\u23f1\ufe0f ${{esc(formatDuration(t.estimated_duration))}}`);
  if (t.recurrence_suggestion) stats.push(`🔁 ${{esc(t.recurrence_suggestion)}}`);

  const metaLine = [
    t.author  ? `by ${{esc(t.author)}}`  : '',
    t.version ? `v${{esc(t.version)}}` : '',
  ].filter(Boolean).join(' \u00b7 ');

  const previewHtml = t.rows && t.rows.length
    ? `<div class="spotlight-preview">${{buildPreview(t.rows)}}</div>`
    : '';

  const actionBtn = t.csv_url
    ? `<a class="btn-primary" href="${{esc(t.csv_url)}}" download>\u2b07\ufe0f Download CSV</a>`
    : '';

  return `
<div class="spotlight-section">
  <div class="spotlight-heading">\u2b50 Template Spotlight</div>
  <div class="spotlight-card">
    <div class="spotlight-body">
      <div class="spotlight-badge">Featured Template</div>
      <div class="spotlight-name">${{esc(t.name)}}</div>
      ${{t.description ? `<div class="spotlight-desc">${{esc(t.description)}}</div>` : ''}}
      ${{tags ? `<div class="spotlight-tags">${{tags}}</div>` : ''}}
      ${{stats.length ? `<div class="spotlight-stats">${{stats.join('<span style="margin:0 .2rem;opacity:.4">\u00b7</span>')}}</div>` : ''}}
      <div class="spotlight-footer">
        ${{actionBtn}}
        <span class="spotlight-meta">${{metaLine}}</span>
      </div>
    </div>
    ${{previewHtml}}
  </div>
</div>`;
}}

function renderHome() {{
  const groups = groupByCategory(TEMPLATES);
  const cats = Object.keys(groups).sort();
  const container = document.getElementById('container');

  let html = buildSpotlight(SPOTLIGHT);
  html += `<p class="intro">Browse <strong>${{TEMPLATES.length}}</strong> templates across <strong>${{cats.length}}</strong> categories.</p>
<div class="category-grid">`;

  cats.forEach(cat => {{
    const items = groups[cat];
    const icon = catIcon(cat);
    const label = catLabel(cat);
    const count = items.length;
    const MAX_PREVIEW = 4;
    const previews = items.slice(0, MAX_PREVIEW);
    const more = count - previews.length;

    const previewItems = previews.map(t => `<li>${{esc(t.name)}}</li>`).join('');
    const moreHtml = more > 0 ? `<li class="cat-more">+\u202f${{more}} more</li>` : '';

    html += `
<div class="cat-card" role="button" tabindex="0"
     aria-label="Browse ${{esc(label)}} templates"
     data-category="${{esc(cat)}}">
  <div class="cat-icon">${{icon}}</div>
  <div class="cat-title">${{esc(label)}}</div>
  <div class="cat-count">${{count}}\u202ftemplate${{count !== 1 ? 's' : ''}}</div>
  <ul class="cat-previews">${{previewItems}}${{moreHtml}}</ul>
  <div class="cat-arrow">View all \u2192</div>
</div>`;
  }});

  html += '</div>';
  container.innerHTML = html;

  container.querySelectorAll('.cat-card').forEach(card => {{
    card.addEventListener('click', () => navigate(card.dataset.category));
    card.addEventListener('keydown', e => {{
      if (e.key === 'Enter' || e.key === ' ') navigate(card.dataset.category);
    }});
  }});
}}

// ── Template card ─────────────────────────────────────────────────────────────

function buildPreview(rows) {{
  const MAX = 7;
  const shown = rows.slice(0, MAX);
  const rest = rows.length - shown.length;
  let html = '';
  shown.forEach(r => {{
    const cls = r.type === 'section' ? 'section' : 'task';
    const content = r.content.replace(/@[\\w-]+/g, '').trim();
    html += `<div class="preview-row ${{cls}}">${{esc(content)}}</div>`;
  }});
  if (rest > 0) html += `<div class="preview-more">+\u202f${{rest}} more</div>`;
  return html;
}}

function buildTemplateCard(t) {{
  const tags = t.tags.map(tag => `<span class="tag">${{esc(tag)}}</span>`).join('');

  const stats = [];
  if (t.task_count)    stats.push(`\u2714\ufe0f ${{t.task_count}}\u202ftask${{t.task_count !== 1 ? 's' : ''}}`);
  if (t.section_count) stats.push(`\u25b8 ${{t.section_count}}\u202fsection${{t.section_count !== 1 ? 's' : ''}}`);
  if (t.estimated_duration) stats.push(`\u23f1\ufe0f ${{esc(formatDuration(t.estimated_duration))}}`);
  if (t.recurrence_suggestion) stats.push(`🔁 ${{esc(t.recurrence_suggestion)}}`);

  const metaLine = [
    t.author  ? `by ${{esc(t.author)}}`  : '',
    t.version ? `v${{esc(t.version)}}` : '',
  ].filter(Boolean).join(' \u00b7 ');

  let previewHtml = '';
  if (t.type === 'template' && t.rows.length) {{
    previewHtml = `<div class="tpl-preview">${{buildPreview(t.rows)}}</div>`;
  }} else if (t.type === 'prompt' && t.inputs && t.inputs.length) {{
    const chips = t.inputs.map(i => `<span class="input-chip">${{esc(i)}}</span>`).join('');
    previewHtml = `<div class="tpl-inputs">
  <div class="tpl-inputs-label">Inputs</div>${{chips}}</div>`;
  }}

  let actionBtn = '';
  if (t.type === 'template' && t.csv_url) {{
    actionBtn = `<a class="btn-primary" href="${{esc(t.csv_url)}}" download>\u2b07\ufe0f Download CSV</a>`;
  }} else if (t.type === 'prompt' && t.prompt_url) {{
    actionBtn = `<a class="btn-primary" href="${{esc(t.prompt_url)}}">View Prompt</a>`;
  }}

  const badgeLabel = t.type === 'prompt' ? 'AI Prompt' : 'Template';

  return `<div class="tpl-card">
  <div class="tpl-card-header">
    <span class="tpl-type-badge">${{badgeLabel}}</span>
    <div class="tpl-title">${{esc(t.name)}}</div>
    ${{t.description ? `<div class="tpl-desc">${{esc(t.description)}}</div>` : ''}}
  </div>
  ${{tags ? `<div class="tpl-tags">${{tags}}</div>` : ''}}
  ${{stats.length ? `<div class="tpl-stats">${{stats.join('<span style="margin:0 .2rem;opacity:.4">\u00b7</span>')}}</div>` : ''}}
  ${{previewHtml}}
  <div class="tpl-card-footer">
    <span class="tpl-meta">${{metaLine}}</span>
    ${{actionBtn}}
  </div>
</div>`;
}}

// ── Category detail view ──────────────────────────────────────────────────────

function renderCategory(cat) {{
  const groups = groupByCategory(TEMPLATES);
  const items = groups[cat] || [];
  const label = catLabel(cat);
  const icon = catIcon(cat);
  const container = document.getElementById('container');

  const html = `
<div class="cat-detail-header">
  <span class="cat-detail-icon">${{icon}}</span>
  <div>
    <div class="cat-detail-title">${{esc(label)}}</div>
    <div class="cat-detail-count">${{items.length}}\u202ftemplate${{items.length !== 1 ? 's' : ''}}</div>
  </div>
</div>
<div class="template-grid">
  ${{items.map(buildTemplateCard).join('')}}
</div>`;

  container.innerHTML = html;
  document.getElementById('crumb-label').textContent = `${{icon}} ${{label}}`;
  document.getElementById('breadcrumb').style.display = 'block';
}}

// ── Search ────────────────────────────────────────────────────────────────────

function matchesQuery(entry, query) {{
  return (
    entry.name.includes(query) ||
    entry.description.includes(query) ||
    entry.category.includes(query) ||
    entry.tags.some(tag => tag.includes(query))
  );
}}

function renderSearch(query) {{
  const trimmed = query.trim();
  const container = document.getElementById('container');

  if (!trimmed) {{
    renderHome();
    document.getElementById('breadcrumb').style.display = 'none';
    return;
  }}

  const q = trimmed.toLowerCase();
  const results = SEARCH_INDEX.filter(entry => matchesQuery(entry, q)).map(entry => entry.template);

  let html = `<p class="search-summary">`;
  if (results.length === 0) {{
    html += `No results for <strong>${{esc(trimmed)}}</strong>`;
  }} else {{
    html += `<strong>${{results.length}}</strong> result${{results.length !== 1 ? 's' : ''}} for <strong>${{esc(trimmed)}}</strong>`;
  }}
  html += `</p>`;

  if (results.length === 0) {{
    html += `<div class="no-results">
  <div class="no-results-icon">🔍</div>
  <p>No templates matched your search. Try different keywords or browse by category.</p>
</div>`;
  }} else {{
    html += `<div class="template-grid">${{results.map(buildTemplateCard).join('')}}</div>`;
  }}

  container.innerHTML = html;
  document.getElementById('breadcrumb').style.display = 'none';
}}

// ── Hash-based routing ────────────────────────────────────────────────────────

function navigate(cat) {{
  window.location.hash = '#/category/' + encodeURIComponent(cat);
}}

function handleRoute() {{
  const hash = window.location.hash;
  const match = hash.match(/^#\\/category\\/(.+)$/);
  if (match) {{
    renderCategory(decodeURIComponent(match[1]));
    document.getElementById('breadcrumb').style.display = 'block';
  }} else {{
    renderHome();
    document.getElementById('breadcrumb').style.display = 'none';
  }}
}}

document.getElementById('btn-back').addEventListener('click', () => {{
  document.getElementById('search-input').value = '';
  document.getElementById('search-clear').style.display = 'none';
  window.location.hash = '';
}});

// ── Search input wiring ───────────────────────────────────────────────────────

const searchInput = document.getElementById('search-input');
const searchClear = document.getElementById('search-clear');

searchInput.addEventListener('input', () => {{
  const query = searchInput.value;
  searchClear.style.display = query ? 'block' : 'none';
  renderSearch(query);
}});

searchClear.addEventListener('click', () => {{
  searchInput.value = '';
  searchClear.style.display = 'none';
  renderHome();
  document.getElementById('breadcrumb').style.display = 'none';
  searchInput.focus();
}});

window.addEventListener('hashchange', () => {{
  // When navigating via hash, clear any active search
  if (searchInput.value) {{
    searchInput.value = '';
    searchClear.style.display = 'none';
  }}
  handleRoute();
}});
handleRoute();
</script>
</body>
</html>
"""


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

    # Copy each template's CSV into the output directory so download links work
    for slug in os.listdir(TEMPLATES_DIR):
        template_dir = os.path.join(TEMPLATES_DIR, slug)
        csv_src = os.path.join(template_dir, "template.csv")
        if os.path.isdir(template_dir) and os.path.exists(csv_src):
            dest_dir = os.path.join(OUTPUT_DIR, "csv-templates", slug)
            os.makedirs(dest_dir, exist_ok=True)
            shutil.copy2(csv_src, os.path.join(dest_dir, "template.csv"))

    # Copy each prompt template's prompt.md into the output directory
    if os.path.isdir(PROMPT_TEMPLATES_DIR):
        for slug in os.listdir(PROMPT_TEMPLATES_DIR):
            template_dir = os.path.join(PROMPT_TEMPLATES_DIR, slug)
            prompt_src = os.path.join(template_dir, "prompt.md")
            if os.path.isdir(template_dir) and os.path.exists(prompt_src):
                dest_dir = os.path.join(OUTPUT_DIR, "prompt-templates", slug)
                os.makedirs(dest_dir, exist_ok=True)
                shutil.copy2(prompt_src, os.path.join(dest_dir, "prompt.md"))

    templates = load_templates()
    spotlight = get_spotlight_template(templates)
    html = generate_html(templates, spotlight)

    output_path = os.path.join(OUTPUT_DIR, "index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Gallery generated: {output_path} ({len(templates)} templates)")


if __name__ == "__main__":
    main()
