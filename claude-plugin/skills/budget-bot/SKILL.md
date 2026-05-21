---
name: budget-bot
description: Build and query Philippine budget datasets from GAA/NEP budget spreadsheet files. Use when Codex needs to ingest raw budget XLSX files, create year-specific SQLite databases, generate department/agency lookup JSONs, normalize renamed agencies across years, or answer Budget Bot-style questions using exact UACS fields and transparent filters.
---

# Budget Bot

Version: `0.2.0`

## Overview

Use this skill for end-to-end Philippine budget spreadsheet analysis. It starts from official budget XLSX files, builds lean SQLite databases, generates lookup JSONs, and answers questions using the bundled Budget Bot instructions.

This skill is spreadsheet-only. Do not use PDF workflows unless another skill is explicitly invoked.

## Workflow

When the user asks to set up or prepare a Budget Bot project, do the work end to end. Do not stop at listing commands unless the user explicitly asks for instructions only.

1. Create `raw/xlsx/`, `sqlite/`, `lookups/`, and `reports/` when missing.
2. Ask the user to download the relevant budget XLSX files from DBM's budget page (`https://www.dbm.gov.ph/index.php/budget`) and place them under `raw/xlsx/` when the files are not already available locally.
3. If downloaded files are elsewhere on disk, copy or move official XLSX files into `raw/xlsx/` after confirming source paths when needed.
4. Inspect `raw/xlsx/` before importing; if a filename does not make the budget year obvious, import that file individually with an explicit `--year`.
5. Build one SQLite database per year with the bundled `scripts/build_budget_sqlite.py`, resolved relative to this skill directory.
6. Generate lookup JSONs with the bundled `scripts/build_department_agency_lookup.py`, resolved relative to this skill directory.
7. Create or update `BUDGET_BOT_PROJECT.md` when the project lacks one.
8. Validate by running a simple row count or department aggregate query against each SQLite file.
9. Read `references/budget_bot_instructions.md` before answering queries. Also read root `BUDGET_BOT_PROJECT.md` when present.
10. Query the year-specific SQLite files directly.
11. Explain source files, years, fields, filters, and amount conversion in the answer.

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

The importer creates a single `budget_rows` table with original spreadsheet columns plus SQLite's implicit `rowid`. It does not add helper columns such as `source_year`, `source_file`, `source_row_number`, or `AMT_PHP`.

## Generate Lookups

After building SQLite files, run bundled script `scripts/build_department_agency_lookup.py`. Resolve it relative to this skill directory.

Use:

- `--sqlite-dir sqlite`
- `--output lookups/department_agency_lookup.json`

The lookup records exact `UACS_DPT_DSC` and `UACS_AGY_DSC` labels by year. Use it to resolve abbreviations, informal names, old names, or possible renamed departments before querying.

Maintain known cross-year renames in the lookup or query logic. Current known normalization:

- `National Economic and Development Authority (NEDA)` in FY2024/FY2025 corresponds to `Department of Economy, Planning, and Development (DEPDev)` in FY2026.

## Query Rules

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

Normalize object fields across years:

- FY2024/FY2025: `UACS_SOBJ_CD`, `UACS_SOBJ_DSC`
- FY2026 and later by-object files may use: `UACS_OBJ_CD`, `UACS_OBJ_DSC`

Amounts in `AMT` are in thousands of Philippine pesos. Multiply by `1,000` for full-peso display.

## References

- `references/budget_bot_instructions.md`: reusable Budget Bot investigation and answer rules.
- `references/query_contract.md`: fallback Budget Bot answer/query contract.
- `references/environment.md`: install locations and path-resolution notes for Codex, Claude Code, and manual use.
- Root `BUDGET_BOT_PROJECT.md`: project-specific data inventory when present.
