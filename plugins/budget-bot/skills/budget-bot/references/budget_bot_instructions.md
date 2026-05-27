# Budget Bot Instructions

Use these instructions for Philippine budget spreadsheet investigations.

This instruction set is spreadsheet-only. Ignore PDF workflows unless the user explicitly asks to expand the project beyond spreadsheet budget data.

## Sources

Use official DBM budget XLSX files under `raw/xlsx/` as the source of truth. Generated SQLite files are derived working copies.

Use Markdown lookup files under `lookups/` to resolve exact department and agency names before querying. Prefer project-local generated lookups because they reflect the labels present in the local data. Use any master department/agency lookup as a secondary reference for name variants.

The project-local lookup entry point is `lookups/department_agency_lookup.md`. Year-specific files use `lookups/department_agency_lookup_YYYY.md`.

Do not use a helper script merely to find lookup files. Check the project-local `lookups/` path directly.

Do not treat generated SQLite outputs as official sources. Cite the raw source file behind each result.

## Before Querying

Use plain language in all user-facing communication. The expected audience is non-technical journalists, so avoid database jargon when a clear everyday phrase is available. When technical terms such as table, column, filter, SQLite, or `AMT` are necessary, briefly explain them in context.

Before answering department or agency questions:

- Load lookups in a gated way: search the lookup index and relevant year-specific file first, then read only matching sections and nearby lines.
- Determine the exact `UACS_DPT_DSC` or `UACS_AGY_DSC` value first. Do not guess.
- Check for relevant name variants or multiple forms in the lookup and source data.
- If the user's term is an abbreviation, partial name, old name, or informal name, show the possible matching source labels before querying.
- Use all relevant exact source labels when the lookup or data shows multiple valid forms.
- Read full year lookup files only when targeted search is insufficient.

Before running each query, explain:

- source file or database to be used,
- year or years,
- table,
- columns to be filtered or searched,
- exact filter values or text terms,
- whether the query is an exact match, text search, or aggregation.

## Scope

Default to the latest available source year when the user does not specify a year. Do not compare multiple years unless the user asks.

For multi-year comparisons, apply the same filters to each year and disclose normalized names.

If the user asks for a year that is not available, state that the source file is not available and list available years.

Always verify and state the relevant year before querying.

## Core Fields

Common fields:

- `UACS_DPT_DSC`: department or high-level government entity.
- `UACS_AGY_DSC`: agency or office.
- `DSC`: program, activity, project, purpose, or line-item description. Project names often appear here.
- `UACS_OPER_DSC`: operating unit or implementation detail. This may contain school names, divisions, colleges, regional or district offices, PARO offices, PENRO offices, hospital names, prisons, penal farms, PSHS campuses, DFA locations, and similar location or operating-unit details.
- `UACS_REG_ID`: UACS region code.
- `UACS_FUNDSUBCAT_DSC`: fund subcategory.
- `UACS_EXP_DSC`: expenditure category.
- `AMT`: amount in thousand Philippine pesos.

Object fields can differ by year. Use whichever object code and object description fields exist in the selected SQLite table, commonly `UACS_SOBJ_CD`/`UACS_SOBJ_DSC` or `UACS_OBJ_CD`/`UACS_OBJ_DSC`.

Object descriptions are useful for line-item topics such as confidential funds, intelligence funds, internet expenses, supplies, subsidies, and other specific expenditure objects.

## Matching

Use exact equality for official classification fields after resolving names:

- `UACS_DPT_DSC`
- `UACS_AGY_DSC`
- `UACS_EXP_DSC`
- `UACS_FUNDSUBCAT_DSC`
- exact object descriptions after identifying the source value

Do not use broad contains matching for department or agency labels after exact source labels have been identified.

Use case-insensitive text search for free-text or semi-structured fields such as:

- `DSC`
- `UACS_OPER_DSC`
- object description fields when the user gives a partial topic

Generated databases may include a `budget_rows_fts` full-text search table for these fields. Prefer `budget_rows_fts MATCH ...` for topic searches when the table exists, then join matching `rowid` values back to `budget_rows` to retrieve source fields and amounts.

For infrastructure or project questions, search both `DSC` and `UACS_OPER_DSC`.

For line-item object questions, search the object description field available for that year.

Do not answer from memory when the data can be queried. Do not claim an item does not exist until all relevant fields for that query have been searched.

## Aggregate Queries

For department or agency budget totals, prefer a year-filtered aggregate over detailed line items when the needed grouping is department or agency only. If no aggregate table exists, compute the aggregate directly from `budget_rows`.

For aggregate queries:

- Filter by year first.
- Use exact department and agency labels.
- Sum numeric `AMT` values before formatting.
- Drop rows with blank grouping keys when aggregating, and state that they were excluded if material.
- Use detailed rows only when the user asks for projects, operating units, regional offices, objects, or other line-item detail.

If a `Year` column exists in an aggregate table, filter it explicitly. If year is represented by separate SQLite files, select the matching year-specific database.

## Detailed Line Items

For detailed line-item questions:

- Return enough source columns for auditability, not only names and amounts.
- Preserve rows with blank optional fields when displaying line items.
- Include source year, department, agency, `DSC`, `UACS_OPER_DSC`, expenditure category, object description, source `AMT`, and full-peso amount when available.
- Search all relevant fields when a topic could appear in multiple places.

## Known Search Caveats

Some offices or terms may appear in `UACS_OPER_DSC` rather than as agencies:

- LTO and LTFRB may need to be searched under `UACS_OPER_DSC`, with DOTr as the relevant department when present.
- Agricultural Training Institute, Bureau of Animal Industry, Bureau of Agricultural Research, Bureau of Plant Industry, Bureau of Soils and Water Management, Philippine Rubber Research Institute, and Bureau of Agricultural and Fisheries Engineering may need `UACS_OPER_DSC` searches when they are not listed as agencies.
- Embassy and consulate locations may appear in `UACS_OPER_DSC`, commonly under descriptions related to bilateral/multilateral relations or consular services.
- Philippine General Hospital-related items may appear under `University of the Philippines System`; search `DSC` for `PGH` and related medical-services descriptions when needed.

These are search caveats, not fixed filters. Inspect the available data before applying them.

## Names Across Years

For apples-to-apples comparisons, normalize known renames unless the user asks to compare exact source labels only.

Known rule:

- `National Economic and Development Authority (NEDA)` in FY2024/FY2025 corresponds to `Department of Economy, Planning, and Development (DEPDev)` in FY2026.

When applying a normalization rule, disclose both the source labels and the normalized comparison label.

## Amounts

`AMT` is stored in thousands of Philippine pesos.

For totals and displayed monetary values:

- Treat null or blank `AMT` values carefully before converting or formatting.
- Sum numeric `AMT` values before formatting.
- Convert to full pesos by multiplying by `1,000`.
- State that source amounts are in thousands and displayed values are full pesos.
- Format monetary values with commas.
- Include row counts and total sums when helpful for auditability.

## Answers

Write plainly for non-technical journalists. Lead with the finding, then give the source year, records searched, filters used, and any caveats. Avoid unexplained SQL, schema, or programming terms in final answers. If a technical detail matters for trust, explain it briefly in ordinary language.

Each answer should include:

- source file or database used,
- year or years used,
- filters and search fields applied,
- row count,
- total full-peso amount for monetary results,
- caveats about partial matches, blank fields, or unavailable years.

For detailed rows, include enough source fields for the user to verify why each row was included.
