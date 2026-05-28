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
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generate_gallery import SITE_URL

OUTPUT_PATH = sys.argv[1] if len(sys.argv) > 1 else "docs/index.html"
EXPECTED_CANONICAL = SITE_URL
EXPECTED_SITEMAP = SITE_URL + "sitemap.xml"
EXPECTED_HREFLANGS = {
    "en": SITE_URL,
    "x-default": SITE_URL,
}


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

    # 1b. Canonical link present and absolute
    canonical_tag_match = re.search(
        r'<link[^>]*\brel="canonical"[^>]*>',
        html,
    )
    if not canonical_tag_match:
        fail('No <link rel="canonical"> found')
    canonical_tag = canonical_tag_match.group(0)
    canonical_href_match = re.search(r'\bhref="([^"]+)"', canonical_tag)
    if not canonical_href_match:
        fail('Canonical link missing href attribute')
    canonical = canonical_href_match.group(1)
    if not canonical.startswith("https://"):
        fail(f"Canonical URL must be absolute HTTPS: {canonical!r}")
    if canonical != EXPECTED_CANONICAL:
        fail(f"Canonical URL must use production site URL: {canonical!r}")
    print("✅ Canonical link present and valid")

    # 1c. hreflang alternate links present and valid for current single-language strategy
    hreflang_links = {}
    for tag in re.findall(r'<link[^>]*\brel="alternate"[^>]*>', html):
        hreflang_match = re.search(r'\bhreflang="([^"]+)"', tag)
        href_match = re.search(r'\bhref="([^"]+)"', tag)
        if not hreflang_match or not href_match:
            fail(f"Alternate link must include both hreflang and href: {tag!r}")
        hreflang_links[hreflang_match.group(1)] = href_match.group(1)

    for code, expected_href in EXPECTED_HREFLANGS.items():
        if code not in hreflang_links:
            fail(f"Missing hreflang alternate for {code!r}")
        href = hreflang_links[code]
        if not href.startswith("https://"):
            fail(f"hreflang URL must be absolute HTTPS for {code!r}: {href!r}")
        if href != expected_href:
            fail(f"hreflang URL for {code!r} must match production URL: {href!r}")
    print("✅ hreflang alternate links present and valid")

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

    # 6. robots.txt exists with valid baseline directives and absolute sitemap URL
    output_dir = os.path.dirname(os.path.abspath(OUTPUT_PATH))
    robots_path = os.path.join(output_dir, "robots.txt")
    try:
        with open(robots_path, encoding="utf-8") as f:
            robots = f.read()
    except FileNotFoundError:
        fail(f"{robots_path} not found - robots.txt must be generated")

    if "User-agent: *" not in robots:
        fail("robots.txt missing 'User-agent: *'")
    if "Allow: /" not in robots:
        fail("robots.txt missing 'Allow: /'")

    sitemap_match = re.search(r'^Sitemap:\s*(\S+)\s*$', robots, re.MULTILINE)
    if not sitemap_match:
        fail("robots.txt missing Sitemap directive")
    sitemap_url = sitemap_match.group(1)
    if not sitemap_url.startswith("https://"):
        fail(f"robots.txt Sitemap must be absolute HTTPS URL: {sitemap_url!r}")
    if sitemap_url != EXPECTED_SITEMAP:
        fail(f"robots.txt Sitemap must match production URL: {sitemap_url!r}")
    print("✅ robots.txt directives and sitemap URL are valid")

    # 7. sitemap.xml exists, parses, and includes canonical root URL
    sitemap_path = os.path.join(output_dir, "sitemap.xml")
    try:
        with open(sitemap_path, encoding="utf-8") as f:
            sitemap_xml = f.read()
    except FileNotFoundError:
        fail(f"{sitemap_path} not found - sitemap.xml must be generated")

    try:
        root = ET.fromstring(sitemap_xml)
    except ET.ParseError as exc:
        fail(f"sitemap.xml is not valid XML: {exc}")

    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    loc_values = [
        (loc.text or "").strip()
        for loc in root.findall("sm:url/sm:loc", ns)
    ]
    if EXPECTED_CANONICAL not in loc_values:
        fail("sitemap.xml must include canonical site URL in <loc>")
    print("✅ sitemap.xml exists and includes canonical URL")

    print(f"\n✅ All security assertions passed for {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
