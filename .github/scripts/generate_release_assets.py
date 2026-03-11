#!/usr/bin/env python3
"""Generate release assets: index.json and templates.zip.

Usage:
    python3 generate_release_assets.py

Environment variables:
    TEMPLATES_DIR   Path to the templates folder (default: templates)
    OUTPUT_DIR      Path to write generated files to (default: dist)
"""

import csv
import json
import os
import re
import sys
import zipfile
from datetime import datetime, timezone

TEMPLATES_DIR = os.environ.get("TEMPLATES_DIR", "templates")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "dist")


# ---------------------------------------------------------------------------
# Parsing helpers (shared logic with generate_gallery.py)
# ---------------------------------------------------------------------------

def parse_meta(path):
    """Parse a simple meta.yml file without a YAML library."""
    meta = {"tags": []}
    in_tags = False
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if re.match(r"^tags:\s*$", line):
                in_tags = True
                continue
            if in_tags:
                m = re.match(r"^\s+-\s+(.+)$", line)
                if m:
                    meta["tags"].append(m.group(1).strip())
                    continue
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
            "version": meta.get("version", ""),
            "estimated_duration": meta.get("estimated_duration", ""),
            "recurrence_suggestion": meta.get("recurrence_suggestion", ""),
            "author": meta.get("author", ""),
            "task_count": task_count,
            "section_count": section_count,
        })
    return templates


# ---------------------------------------------------------------------------
# Asset generation
# ---------------------------------------------------------------------------

def generate_index_json(templates):
    """Return the index.json content as a string."""
    catalog = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "template_count": len(templates),
        "templates": templates,
    }
    return json.dumps(catalog, indent=2, ensure_ascii=False)


def generate_templates_zip(output_path):
    """Create a zip archive of all template folders."""
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for slug in sorted(os.listdir(TEMPLATES_DIR)):
            template_dir = os.path.join(TEMPLATES_DIR, slug)
            if not os.path.isdir(template_dir):
                continue
            for filename in sorted(os.listdir(template_dir)):
                file_path = os.path.join(template_dir, filename)
                if os.path.isfile(file_path):
                    arcname = os.path.join("templates", slug, filename)
                    zf.write(file_path, arcname)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    if not os.path.isdir(TEMPLATES_DIR):
        print(f"Error: templates directory not found: {TEMPLATES_DIR}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    templates = load_templates()

    # Generate index.json
    index_path = os.path.join(OUTPUT_DIR, "index.json")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(generate_index_json(templates))
    print(f"✅ index.json written: {index_path} ({len(templates)} templates)")

    # Generate templates.zip
    zip_path = os.path.join(OUTPUT_DIR, "templates.zip")
    generate_templates_zip(zip_path)
    print(f"✅ templates.zip written: {zip_path}")


if __name__ == "__main__":
    main()
