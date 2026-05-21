#!/usr/bin/env python
"""Generate department/agency lookup JSON from Budget Bot SQLite databases."""

from __future__ import annotations

import argparse
import json
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sqlite-dir", type=Path, default=Path("sqlite"))
    parser.add_argument("--output", type=Path, default=Path("lookups/department_agency_lookup.json"))
    args = parser.parse_args()

    departments: dict[str, dict[str, object]] = {}
    sources: dict[str, str] = {}

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

    output = {
        "description": "Department and agency lookup generated from Budget Bot SQLite files.",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "sources": sources,
        "fields": ["UACS_DPT_DSC", "UACS_AGY_DSC"],
        "known_cross_year_normalizations": [
            {
                "normalized_label": "National Economic and Development Authority (NEDA) / Department of Economy, Planning, and Development (DEPDev)",
                "labels_by_year": {
                    "2024": "National Economic and Development Authority (NEDA)",
                    "2025": "National Economic and Development Authority (NEDA)",
                    "2026": "Department of Economy, Planning, and Development (DEPDev)",
                },
            }
        ],
        "departments": sorted(departments.values(), key=lambda item: item["UACS_DPT_DSC"]),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.output} ({len(output['departments']):,} departments)")


if __name__ == "__main__":
    main()
