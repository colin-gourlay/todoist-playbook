#!/usr/bin/env python3
"""Assert security properties of the generated gallery HTML.

Usage:
    python3 assert_gallery_security.py [docs/index.html]

Exits non-zero with a descriptive message on any failure.
"""

import json
import os
import re
import sys

OUTPUT_PATH = sys.argv[1] if len(sys.argv) > 1 else "docs/index.html"


def fail(msg):
    print(f"❌ SECURITY ASSERTION FAILED: {msg}", file=sys.stderr)
    sys.exit(1)


def main():
    try:
        with open(OUTPUT_PATH, encoding="utf-8") as f:
            html = f.read()
    except FileNotFoundError:
        fail(f"{OUTPUT_PATH} not found — run generate_gallery.py first")

    # 1. CSP meta present and correct
    csp_match = re.search(
        r'<meta\s+http-equiv="Content-Security-Policy"\s+content="([^"]+)"',
        html,
    )
    if not csp_match:
        fail("No <meta http-equiv='Content-Security-Policy'> found")
    csp = csp_match.group(1)
    if "default-src 'none'" not in csp:
        fail(f"CSP missing 'default-src 'none'': {csp!r}")
    if "script-src 'self'" not in csp:
        fail(f"CSP missing 'script-src 'self'': {csp!r}")
    if "frame-ancestors 'none'" not in csp:
        fail(f"CSP missing 'frame-ancestors 'none'': {csp!r}")
    if "'unsafe-eval'" in csp:
        fail(f"CSP contains 'unsafe-eval': {csp!r}")
    # 'unsafe-inline' may appear only inside style-src-attr, not in script-src
    script_src_match = re.search(r"script-src\s+([^;]+)", csp)
    if script_src_match and "'unsafe-inline'" in script_src_match.group(1):
        fail(f"script-src contains 'unsafe-inline': {csp!r}")
    print("✅ CSP meta present and correct")

    # 2. Every vendor <script src> has integrity + crossorigin
    for m in re.finditer(r'<script\s+([^>]+)>', html):
        attrs = m.group(1)
        if 'src="vendor/' not in attrs:
            continue
        if 'integrity="sha384-' not in attrs:
            fail(f"Vendor script missing integrity attribute: {m.group(0)!r}")
        if 'crossorigin="anonymous"' not in attrs:
            fail(f"Vendor script missing crossorigin attribute: {m.group(0)!r}")
    print("✅ Vendor script integrity attributes present")

    # 3. JSON data island round-trips
    island = re.search(
        r'<script[^>]+type="application/json"[^>]+id="tp-data"[^>]*>(.+?)</script>',
        html,
        re.DOTALL,
    )
    if not island:
        fail("JSON data island <script type='application/json' id='tp-data'> not found")
    raw = island.group(1).replace("<\\/", "</")
    try:
        json.loads(raw)
    except json.JSONDecodeError as e:
        fail(f"JSON data island does not parse: {e}")
    print("✅ JSON data island round-trips cleanly")

    # 4. No inline <style> tags with body content
    inline_styles = re.findall(r'<style[^>]*>[^<\s][^<]*</style>', html, re.DOTALL)
    if inline_styles:
        fail(f"Inline <style> with content found: {inline_styles[0][:80]!r}")
    print("✅ No inline <style> blocks with content")

    # 5. No inline event handler attributes
    if re.search(r'\s(on[a-z]+)\s*=', html, re.IGNORECASE):
        m = re.search(r'\s(on[a-z]+)\s*=', html, re.IGNORECASE)
        fail(f"Inline event handler attribute found: {m.group(0)!r}")
    print("✅ No inline event handler attributes")

    # 6. app.js contains frame-busting guard
    check_appjs_framebust(OUTPUT_PATH)

    print(f"\n✅ All security assertions passed for {OUTPUT_PATH}")


def check_appjs_framebust(output_path):
    """Assert that docs/app.js contains the frame-busting guard."""
    appjs_path = os.path.join(os.path.dirname(os.path.abspath(output_path)), "app.js")
    try:
        with open(appjs_path, encoding="utf-8") as f:
            appjs = f.read()
    except FileNotFoundError:
        fail(f"{appjs_path} not found")
    if "window.top !== window.self" not in appjs:
        fail("app.js is missing the frame-busting guard (window.top !== window.self)")
    print("✅ app.js frame-busting guard present")


if __name__ == "__main__":
    main()
