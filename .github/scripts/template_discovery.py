"""Shared CSV template discovery helpers.

CSV templates may live either directly under ``csv-templates/{slug}/`` or under
a single optional grouping folder, ``csv-templates/{group}/{slug}/``. In both
cases the slug remains the terminal folder name, must be kebab-case, and must
match ``slug:`` in ``meta.yml``.

These helpers are the canonical discovery surface for repository automation so
that scripts do not duplicate ``os.walk`` logic and keep slug semantics
consistent.

Prompt templates remain flat (``prompt-templates/{slug}/``) and are intentionally
out of scope here.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable, Optional


CSV_TEMPLATES_DIR = "csv-templates"
META_FILENAME = "meta.yml"


@dataclass(frozen=True)
class TemplateLocation:
    """Resolved location of a CSV template on disk."""

    slug: str
    template_dir: str  # e.g. "csv-templates/github/github-trending-repositories-daily-review"
    group: Optional[str]  # e.g. "github" when nested, otherwise None
    relative_path: str  # template_dir relative to CSV_TEMPLATES_DIR

    @property
    def meta_path(self) -> str:
        return os.path.join(self.template_dir, META_FILENAME)

    @property
    def csv_path(self) -> str:
        return os.path.join(self.template_dir, "template.csv")

    @property
    def readme_path(self) -> str:
        return os.path.join(self.template_dir, "README.md")


def _is_template_dir(path: str) -> bool:
    return os.path.isfile(os.path.join(path, META_FILENAME))


def iter_template_locations(base_dir: str = CSV_TEMPLATES_DIR) -> Iterable[TemplateLocation]:
    """Yield every CSV template under *base_dir* in deterministic slug order.

    Supports two layouts:

    * Flat: ``base_dir/{slug}/meta.yml``
    * Grouped: ``base_dir/{group}/{slug}/meta.yml`` (single grouping level)

    Directories that do not contain a ``meta.yml`` are skipped. If a directory
    contains a ``meta.yml`` it is treated as a template and its children are not
    inspected; this keeps semantics simple and avoids accidental nested groups.
    """
    if not os.path.isdir(base_dir):
        return

    found: list[TemplateLocation] = []

    for first in sorted(os.listdir(base_dir)):
        first_path = os.path.join(base_dir, first)
        if not os.path.isdir(first_path):
            continue

        if _is_template_dir(first_path):
            found.append(
                TemplateLocation(
                    slug=first,
                    template_dir=first_path,
                    group=None,
                    relative_path=first,
                )
            )
            continue

        # Treat as a grouping folder: look one level deeper for templates.
        for second in sorted(os.listdir(first_path)):
            second_path = os.path.join(first_path, second)
            if not os.path.isdir(second_path):
                continue
            if _is_template_dir(second_path):
                found.append(
                    TemplateLocation(
                        slug=second,
                        template_dir=second_path,
                        group=first,
                        relative_path=os.path.join(first, second),
                    )
                )

    found.sort(key=lambda loc: loc.slug)
    yield from found


def list_template_locations(base_dir: str = CSV_TEMPLATES_DIR) -> list[TemplateLocation]:
    """Return all CSV template locations as a list, sorted by slug."""
    return list(iter_template_locations(base_dir))


def find_template_location(slug: str, base_dir: str = CSV_TEMPLATES_DIR) -> Optional[TemplateLocation]:
    """Return the template location for *slug*, or None if it does not exist."""
    if not slug:
        return None
    for location in iter_template_locations(base_dir):
        if location.slug == slug:
            return location
    return None


def resolve_template_dir(slug: str, base_dir: str = CSV_TEMPLATES_DIR) -> Optional[str]:
    """Return the on-disk template directory for *slug*, or None if absent."""
    location = find_template_location(slug, base_dir)
    return location.template_dir if location else None


def slug_exists(slug: str, base_dir: str = CSV_TEMPLATES_DIR) -> bool:
    """Return True if a CSV template with *slug* exists under *base_dir*."""
    return find_template_location(slug, base_dir) is not None
