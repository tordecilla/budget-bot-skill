#!/usr/bin/env python
"""Generate department/agency lookup Markdown from Budget Bot SQLite databases."""

from __future__ import annotations

import argparse
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def infer_year(path: Path) -> int:
    match = re.search(r"(20\d{2})", path.name)
    if not match:
        raise ValueError(f"Could not infer year from filename: {path}")
    return int(match.group(1))


def sqlite_files(sqlite_dir: Path) -> list[Path]:
    return sorted(path for path in sqlite_dir.glob("*.sqlite") if re.search(r"(20\d{2})", path.name))


def has_budget_rows(conn: sqlite3.Connection) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'budget_rows'"
    ).fetchone()
    return row is not None


def amount_text(amount_thousand_php: float) -> str:
    return f"PHP {amount_thousand_php * 1000:,.0f}"


def year_lookup_path(index_path: Path, year: str) -> Path:
    return index_path.with_name(f"{index_path.stem}_{year}{index_path.suffix}")


def write_year_lookup(path: Path, year: str, source: str, rows: list[dict[str, object]]) -> None:
    lines = [
        f"# Department/Agency Lookup {year}",
        "",
        "Use this file only when a query needs department or agency name resolution for this year.",
        "",
        f"- Source database: `{source}`",
        "- Fields: `UACS_DPT_DSC`, `UACS_AGY_DSC`",
        "",
        "## Departments",
        "",
    ]

    current_department: str | None = None
    for row in rows:
        department = str(row["department"] or "")
        agency = str(row["agency"] or "")
        row_count = int(row["row_count"] or 0)
        amount = float(row["amount_thousand_php"] or 0)
        if department != current_department:
            if current_department is not None:
                lines.append("")
            lines.extend([f"### {department}", "", f"- `UACS_DPT_DSC`: `{department}`"])
            current_department = department
        agency_label = agency if agency else "(blank agency)"
        lines.append(
            f"- Agency: `{agency_label}` | `UACS_AGY_DSC`: `{agency}` | Rows: {row_count:,} | Amount: {amount_text(amount)}"
        )

    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_index_lookup(
    path: Path,
    generated_at_utc: str,
    sources: dict[str, str],
    departments: dict[str, dict[str, object]],
) -> None:
    lines = [
        "# Department/Agency Lookup Index",
        "",
        "This is a compact index for gated lookup loading. Do not load every year file by default.",
        "",
        f"- Generated at UTC: `{generated_at_utc}`",
        "- Fields: `UACS_DPT_DSC`, `UACS_AGY_DSC`",
        "",
        "## Gated Loading",
        "",
        "1. Determine the relevant year or years from the user's query.",
        "2. Search this index and the relevant `department_agency_lookup_YYYY.md` file for the user's exact term, abbreviation, old name, or informal name.",
        "3. Read only matching sections and nearby lines first.",
        "4. If multiple exact labels are plausible, show candidates before querying.",
        "5. Read full year lookup files only when targeted search is insufficient.",
        "",
        "## Year Files",
        "",
    ]
    for year, source in sorted(sources.items()):
        year_path = year_lookup_path(path, year).name
        lines.append(f"- `{year}`: `{year_path}` from `{source}`")

    lines.extend(
        [
            "",
            "## Known Cross-Year Normalizations",
            "",
            "- `National Economic and Development Authority (NEDA)` in FY2024/FY2025 corresponds to `Department of Economy, Planning, and Development (DEPDev)` in FY2026.",
            "",
            "## Department Index",
            "",
        ]
    )

    for dept, entry in sorted(departments.items()):
        years = ", ".join(str(year) for year in sorted(entry["years_present"]))
        counts = ", ".join(
            f"{year}: {entry['row_counts_by_year'][year]:,} rows"
            for year in sorted(entry["row_counts_by_year"])
        )
        lines.append(f"- `{dept}` | Years: {years} | {counts}")

    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sqlite-dir", type=Path, default=Path("sqlite"))
    parser.add_argument("--output", type=Path, default=Path("lookups/department_agency_lookup.md"))
    args = parser.parse_args()

    departments: dict[str, dict[str, object]] = {}
    sources: dict[str, str] = {}
    rows_by_year: dict[str, list[dict[str, object]]] = {}

    for db_path in sqlite_files(args.sqlite_dir):
        year = infer_year(db_path)
        conn = sqlite3.connect(db_path)
        if not has_budget_rows(conn):
            conn.close()
            print(f"Skipping {db_path}: no budget_rows table")
            continue
        sources[str(year)] = str(db_path).replace("\\", "/")
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT UACS_DPT_DSC AS department,
                   UACS_AGY_DSC AS agency,
                   COUNT(*) AS row_count,
                   SUM(CAST(REPLACE(COALESCE(AMT, '0'), ',', '') AS REAL)) AS amount_thousand_php
            FROM budget_rows
            WHERE COALESCE(TRIM(UACS_DPT_DSC), '') <> ''
            GROUP BY UACS_DPT_DSC, UACS_AGY_DSC
            ORDER BY UACS_DPT_DSC, UACS_AGY_DSC
            """
        ).fetchall()
        conn.close()

        year_key = str(year)
        rows_by_year[year_key] = [dict(row) for row in rows]
        for row in rows:
            dept = row["department"]
            agency = row["agency"] or ""
            entry = departments.setdefault(
                dept,
                {
                    "UACS_DPT_DSC": dept,
                    "years_present": [],
                    "agencies_by_year": {},
                    "row_counts_by_year": {},
                    "amount_thousand_php_by_year": {},
                },
            )
            year_key = str(year)
            if year not in entry["years_present"]:
                entry["years_present"].append(year)
            entry["agencies_by_year"].setdefault(year_key, [])
            if agency and agency not in entry["agencies_by_year"][year_key]:
                entry["agencies_by_year"][year_key].append(agency)
            entry["row_counts_by_year"][year_key] = entry["row_counts_by_year"].get(year_key, 0) + int(row["row_count"] or 0)
            entry["amount_thousand_php_by_year"][year_key] = entry["amount_thousand_php_by_year"].get(year_key, 0) + float(row["amount_thousand_php"] or 0)

    for entry in departments.values():
        entry["years_present"] = sorted(entry["years_present"])
        for agencies in entry["agencies_by_year"].values():
            agencies.sort()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    generated_at_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    write_index_lookup(args.output, generated_at_utc, sources, departments)
    for year, rows in rows_by_year.items():
        write_year_lookup(year_lookup_path(args.output, year), year, sources[year], rows)
    print(f"Wrote {args.output} and {len(rows_by_year):,} year lookup file(s) ({len(departments):,} departments)")


if __name__ == "__main__":
    main()
