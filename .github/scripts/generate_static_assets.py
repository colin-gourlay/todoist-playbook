#!/usr/bin/env python3
"""Generate static assets that require optional image libraries.

Run this script once to (re)generate docs/apple-touch-icon.png.
If Pillow is installed it draws a proper icon; otherwise it generates
a minimal solid-colour placeholder PNG using only stdlib.

Usage:
    python3 .github/scripts/generate_static_assets.py
"""

import os
import struct
import zlib

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "docs")


# ---------------------------------------------------------------------------
# Minimal PNG encoder (stdlib only, no Pillow required)
# ---------------------------------------------------------------------------

def _chunk(name: bytes, data: bytes) -> bytes:
    crc = zlib.crc32(name + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + name + data + struct.pack(">I", crc)


def _make_minimal_png(width: int, height: int, color: tuple) -> bytes:
    """Return bytes of a minimal solid-colour PNG (no alpha)."""
    r, g, b = color
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    header = b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr_data)
    raw = b""
    row = bytes([r, g, b] * width)
    for _ in range(height):
        raw += b"\x00" + row
    idat = _chunk(b"IDAT", zlib.compress(raw, 9))
    iend = _chunk(b"IEND", b"")
    return header + idat + iend


# ---------------------------------------------------------------------------
# Icon generation
# ---------------------------------------------------------------------------

def generate_apple_touch_icon() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out = os.path.join(OUTPUT_DIR, "apple-touch-icon.png")

    try:
        from PIL import Image, ImageDraw  # type: ignore

        img = Image.new("RGB", (180, 180), (211, 66, 68))
        draw = ImageDraw.Draw(img)
        # Clipboard body (white rectangle)
        draw.rounded_rectangle([35, 48, 145, 148], radius=8, fill=(255, 255, 255))
        # Clipboard clip (darker red rectangle at top)
        draw.rounded_rectangle([65, 34, 115, 60], radius=5, fill=(174, 59, 61))
        # Task lines
        for y in [75, 90, 105, 120]:
            draw.rectangle([50, y, 130, y + 6], fill=(211, 66, 68))
        img.save(out, "PNG")
        print(f"✅ Generated {out} using Pillow (180×180)")

    except ImportError:
        png = _make_minimal_png(180, 180, (211, 66, 68))
        with open(out, "wb") as f:
            f.write(png)
        print(f"⚠️  Pillow not available — generated solid-colour placeholder PNG at {out}")
        print("   Re-run with Pillow installed for a proper branded icon.")


if __name__ == "__main__":
    generate_apple_touch_icon()
