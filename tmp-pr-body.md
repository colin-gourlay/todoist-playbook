## Summary
- Normalized workflow permissions model across all workflow files to a deny-by-default baseline
- Added `permissions: {}` at workflow level where missing
- Moved required token scopes to job-level `permissions` blocks
- Preserved existing behavior and required capabilities for each workflow

## Additional consistency updates included
- Kept/normalized validate-gated deploy/release chaining and expression style
- Kept normalized concurrency group style on validate/deploy/release (`${{ github.workflow }}-${{ github.ref }}`)

## Validation
- VS Code workflow/YAML checks report no errors across all modified workflow files

## Notes
- A stash conflict occurred when splitting work onto a clean branch; conflict was resolved to the agreed deploy workflow shape (workflow_run from Validate templates, manual dispatch fallback, local reusable workflow reference, job-scoped permissions).
