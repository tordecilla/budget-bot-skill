# Budget Bot Query Contract

Use exact budget labels from the project-local Markdown lookup files or actual SQLite data before filtering departments or agencies.

Lookup entry point: `lookups/department_agency_lookup.md`. Year-specific lookup files: `lookups/department_agency_lookup_YYYY.md`.

Load lookups in a gated way. Search the index and relevant year file for the user's term first, then read only matching sections and nearby lines unless broader lookup context is needed.

Use plain language in all user-facing communication. The expected audience is non-technical journalists. Lead with the finding, avoid unexplained database jargon, and briefly explain technical terms when they are needed for trust.

Default to the latest available year when the user does not specify a year. Do not compare multiple years unless the user asks.

For multi-year comparisons, apply the same filters to each year and disclose any normalized names.

Always state:

- source database or source file,
- year or years,
- fields searched,
- exact filters or text terms,
- row count when helpful for auditability,
- totals in full pesos.

Use `AMT * 1000` for full-peso values. Keep source `AMT` in mind as thousands of pesos.

Use exact equality for `UACS_DPT_DSC`, `UACS_AGY_DSC`, `UACS_EXP_DSC`, and `UACS_FUNDSUBCAT_DSC` after resolving names. Use text search for `DSC`, `UACS_OPER_DSC`, and object descriptions.

Generated databases may include ordinary indexes for exact-match fields and a `budget_rows_fts` full-text search table for topic fields. Use `budget_rows_fts MATCH ...` for free-text topic searches when available, joining back to `budget_rows` on `rowid`.


