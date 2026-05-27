---
name: budget-bot
description: Build and query Philippine budget datasets from GAA/NEP budget spreadsheet files. Use when an agent needs to ingest raw budget XLSX files, create year-specific SQLite databases, generate department/agency lookup Markdown files, normalize renamed agencies across years, or answer Budget Bot-style questions using exact UACS fields and transparent filters.
---

# Budget Bot

Version: `0.2.2`

## Overview

Use this skill for end-to-end Philippine budget spreadsheet analysis. It starts from official budget XLSX files, builds lean SQLite databases, generates Markdown lookups, and answers questions using the bundled Budget Bot instructions.

This skill is spreadsheet-only. Do not use PDF workflows unless another skill is explicitly invoked.

## Requirements

Budget Bot setup requires:

- Python 3.10 or newer.
- Python's standard `sqlite3` module, which is included with normal Python installs.
- Python package dependencies from `requirements.txt`, currently `openpyxl` for XLSX import.

Before importing XLSX files, verify that Python, Python's `sqlite3` module, and `openpyxl` are available. If Python package dependencies are missing, install them with:

```powershell
python -m pip install -r skills\budget-bot\requirements.txt
```

Do not install dependencies for simple queries against existing SQLite databases unless a required dependency is actually missing.

## Workflow

When the user asks to set up or prepare a Budget Bot project, do the work end to end. Do not stop at listing commands unless the user explicitly asks for instructions only.

1. Create `raw/xlsx/`, `sqlite/`, `lookups/`, `reports/`, `logs/`, and `data/` when missing.
2. Ask the user to download the relevant budget XLSX files from DBM's budget page (`https://www.dbm.gov.ph/index.php/budget`) and place them under `raw/xlsx/` when the files are not already available locally.
3. If downloaded files are elsewhere on disk, copy or move official XLSX files into `raw/xlsx/` after confirming source paths when needed.
4. Inspect `raw/xlsx/` before importing; if a filename does not make the budget year obvious, import that file individually with an explicit `--year`.
5. Build one SQLite database per year with the bundled `scripts/build_budget_sqlite.py`, resolved relative to this skill directory.
6. Generate Markdown lookups with the bundled `scripts/build_department_agency_lookup.py`, resolved relative to this skill directory.
7. Create or update `BUDGET_BOT_PROJECT.md` when the project lacks one.
8. After creating databases, ensure `logs/` and `data/` exist for query audit artifacts.
9. Validate by running a simple row count or department aggregate query against each SQLite file.
10. Read `references/budget_bot_instructions.md` before answering queries. Also read root `BUDGET_BOT_PROJECT.md` when present.
11. Query the year-specific SQLite files directly.
12. Save the exact data query text to `logs/` and save the resulting data to `data/` before answering. This can be a simple export of the executed SQL and result rows; do not reread everything or manually regenerate outputs when a direct query/export is enough.
13. Explain source files, years, fields, filters, zero-amount filtering, and amount conversion in the answer.

## SQLite Is Canonical

Use direct XLSX-to-SQLite import. SQLite is the only generated data target in setup.

## Build Databases

Use bundled script `scripts/build_budget_sqlite.py`. Resolve it relative to this skill directory; do not hardcode an installation path. For environment-specific path examples, read `references/environment.md`.

For straightforward filenames, batch import with:

- `--xlsx-dir raw/xlsx`
- `--sqlite-dir sqlite`

For ambiguous filenames, import the file individually with:

- `--xlsx`
- `--sqlite`
- `--year`

The importer creates a `budget_rows` table with original spreadsheet columns plus SQLite's implicit `rowid`. It also adds query support without changing source rows:

- indexes on exact-match fields when present: `UACS_DPT_DSC`, `UACS_AGY_DSC`, `UACS_EXP_DSC`, `UACS_FUNDSUBCAT_DSC`, `UACS_REG_ID`, object codes, and object descriptions
- a `budget_rows_fts` full-text search table over available topic fields: `DSC`, `UACS_OPER_DSC`, `UACS_SOBJ_DSC`, and `UACS_OBJ_DSC`

It does not add helper columns such as `source_year`, `source_file`, `source_row_number`, or `AMT_PHP`.

## Generate Lookups

After building SQLite files, run bundled script `scripts/build_department_agency_lookup.py`. Resolve it relative to this skill directory.

Use:

- `--sqlite-dir sqlite`
- `--output lookups/department_agency_lookup.md`

The script writes a compact lookup index at `lookups/department_agency_lookup.md` and one year-specific lookup per source year, named `lookups/department_agency_lookup_YYYY.md`. The lookup records exact `UACS_DPT_DSC` and `UACS_AGY_DSC` labels by year. Use it to resolve abbreviations, informal names, old names, or possible renamed departments before querying.

Do not use a helper script merely to find lookup files. Check the project-local `lookups/` path directly.

Load lookups in a gated way:

1. Determine the relevant year or years from the user's query.
2. Search `lookups/department_agency_lookup.md` and the relevant `lookups/department_agency_lookup_YYYY.md` file for the user's term with `rg` or `Select-String`.
3. Read only matching sections and nearby lines first.
4. If multiple exact labels are plausible, show the candidate labels before querying.
5. Read full year lookup files only when targeted search is insufficient.

Maintain known cross-year renames in the lookup or query logic. Current known normalization:

- `National Economic and Development Authority (NEDA)` in FY2024/FY2025 corresponds to `Department of Economy, Planning, and Development (DEPDev)` in FY2026.

## Query Rules

Use plain language in all user-facing communication. The expected audience is non-technical journalists, so avoid database jargon when a clear everyday phrase is available. When technical terms such as table, column, filter, SQLite, or `AMT` are necessary, briefly explain them in context.

Before querying, state:

- database or source file,
- year or years,
- table,
- exact columns searched,
- search terms,
- whether filters are exact, text search, or aggregation.

For official classification fields, use exact equality after resolving names:

- `UACS_DPT_DSC`
- `UACS_AGY_DSC`
- `UACS_EXP_DSC`
- `UACS_FUNDSUBCAT_DSC`

For free-text topics, search relevant text fields:

- `DSC`
- `UACS_OPER_DSC`
- object description field

When `budget_rows_fts` exists, use it for these free-text searches and join back to `budget_rows` by `rowid` for amounts and source fields.

Normalize object fields across years:

- FY2024/FY2025: `UACS_SOBJ_CD`, `UACS_SOBJ_DSC`
- FY2026 and later by-object files may use: `UACS_OBJ_CD`, `UACS_OBJ_DSC`

Amounts in `AMT` are in thousands of Philippine pesos. Multiply by `1,000` for full-peso display.

## Query Artifacts

For every user data query, create `logs/` and `data/` if they are missing.

Save the exact executed query text under `logs/`, using a timestamped filename. Save the resulting rows under `data/`, using a matching timestamped filename. Prefer simple, direct exports such as SQL text plus CSV or JSON query results. Do not perform broad rereads or manual regeneration when the executed query and direct result export are sufficient.

If query results include rows where `AMT` is zero, filter those zero-amount rows out by default and tell the user how many were filtered. The user can explicitly ask to include zero-amount rows; only then return them.

## Answer Style

Write plainly for non-technical journalists. Lead with the finding, then give the source year, records searched, filters used, and any caveats. Avoid unexplained SQL, schema, or programming terms in final answers. If a technical detail matters for trust, explain it briefly in ordinary language.

## References

- `references/budget_bot_instructions.md`: reusable Budget Bot investigation and answer rules.
- `references/query_contract.md`: fallback Budget Bot answer/query contract.
- `references/environment.md`: install locations and path-resolution notes for agent environments and manual shell use.
- Root `BUDGET_BOT_PROJECT.md`: project-specific data inventory when present.
