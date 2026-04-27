---
applyTo: "wiki/**"
description: Conventions for the GitHub wiki source files.
---

# Wiki Conventions

The `wiki/` folder holds the source of truth for the published GitHub wiki: architecture notes, setup, screenshots, roadmap, and per-area deep dives.

## Rules

- File names use `Title-Case-With-Hyphens.md` to match GitHub wiki page slugs (e.g. `Awesome-List-Outreach.md`)
- `Home.md` is the wiki landing page — keep its links up to date when adding or removing pages
- Cross-link wiki pages with bare relative links (e.g. `[Architecture](Architecture.md)`)
- When adding a new wiki page, update `Home.md` and any sibling page that should reference it
- Wiki content can go deeper than `README.md`; `README.md` should remain the high-level entry point and link out to the wiki for detail
