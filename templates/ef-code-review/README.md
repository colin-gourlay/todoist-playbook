# Entity Framework Code Review

A structured checklist for reviewing Entity Framework POCOs and their configuration, ensuring correctness, convention compliance, and zero Roslyn Analyzer violations.

---

## Objective

- Confirm POCO classes are correctly scoped, typed, and organised
- Ensure navigation properties follow aggregate-root conventions
- Validate lazy/eager loading markers are applied consistently
- Verify all EF configuration builder settings are complete and correct

Estimated duration: 30 minutes per entity under review.

---

## When to Use

- During pull request review of any EF entity or configuration class
- When onboarding a new entity into an existing DbContext
- As a final self-review checklist before raising a PR

---

## Structure Overview

1. POCOs
2. Configuration

---

## Section Details

### 1️⃣ POCOs

| Check | Notes |
|-------|-------|
| Class scoped correctly | Accessibility modifier matches intended visibility (e.g. `public`, `internal`) |
| Class inherits expected type(s) | Base class or interface contracts are satisfied |
| Properties in alphabetic order | Improves readability and reduces merge conflicts |
| Navigation properties typed as `ICollection` / `IReadOnlyCollection` | Required when the property is set/managed by its aggregate root |
| Lazy loaded properties marked `virtual` | Required for EF proxy-based lazy loading to function |
| Eager loaded properties not marked `virtual` | Prevents unintentional lazy loading on eagerly loaded relationships |
| No Roslyn Analyzer warnings/errors | Clean build with zero analyzer diagnostics |

### 2️⃣ Configuration

| Check | Notes |
|-------|-------|
| Index applied | Relevant columns have an index for query performance |
| Unique constraint on index (if applicable) | Applied when the indexed column(s) must be unique |
| Property requiredness set | `.IsRequired()` / `.IsRequired(false)` explicitly configured |
| Unicode support set | `.IsUnicode()` / `.IsUnicode(false)` explicitly configured |
| String lengths set | `.HasMaxLength(n)` applied to all string columns |
| Collations set | `.UseCollation(...)` applied where case-sensitivity or locale matters |
| `AutoInclude` for eagerly loaded properties | Builder uses `.Navigation(x => x.Prop).AutoInclude()` |

---

## Import Instructions

1. Download `template.csv`
2. Create a new project in Todoist named after the entity under review (e.g. `Code Review – UserAccount`)
3. Import from CSV
4. Work through each section during the review session
5. Archive or delete the project once the review is complete
