#!/usr/bin/env python
"""Build lean Budget Bot SQLite databases from GAA/NEP XLSX files."""

from __future__ import annotations

import argparse
import re
import sqlite3
from pathlib import Path

from openpyxl.reader import excel as xlsx_reader


EXACT_MATCH_COLUMNS = [
    "UACS_DPT_DSC",
    "UACS_AGY_DSC",
    "UACS_EXP_DSC",
    "UACS_FUNDSUBCAT_DSC",
    "UACS_REG_ID",
    "UACS_SOBJ_CD",
    "UACS_SOBJ_DSC",
    "UACS_OBJ_CD",
    "UACS_OBJ_DSC",
]

TEXT_SEARCH_COLUMNS = [
    "DSC",
    "UACS_OPER_DSC",
    "UACS_SOBJ_DSC",
    "UACS_OBJ_DSC",
]


def qident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def suffix_for_identifier(name: str) -> str:
    suffix = re.sub(r"[^0-9A-Za-z_]+", "_", name).strip("_").lower()
    return suffix or "column"


def clean_header(value: object, index: int) -> str:
    text = str(value).strip() if value is not None else ""
    return text or f"column_{index}"


def infer_year(path: Path, explicit_year: int | None = None) -> int:
    if explicit_year:
        return explicit_year
    match = re.search(r"(20\d{2})", path.name)
    if not match:
        raise ValueError(f"Could not infer year from filename: {path}")
    return int(match.group(1))


def sqlite_name_for(xlsx: Path, year: int, sqlite_dir: Path) -> Path:
    if re.search(r"GAA[-_ ]?20\d{2}", xlsx.stem, re.I):
        stem = re.sub(r".*(GAA[-_ ]?20\d{2}).*", r"\1", xlsx.stem, flags=re.I)
        stem = stem.replace("_", "-").replace(" ", "-")
    else:
        stem = f"GAA-{year}"
    return sqlite_dir / f"{stem}.sqlite"


def cell_value(value: object) -> object:
    return "" if value is None else value


def add_query_support(cur: sqlite3.Cursor, headers: list[str]) -> None:
    header_set = set(headers)
    for column in EXACT_MATCH_COLUMNS:
        if column in header_set:
            index_name = f"idx_budget_rows_{suffix_for_identifier(column)}"
            cur.execute(
                f"CREATE INDEX {qident(index_name)} ON budget_rows ({qident(column)})"
            )

    text_columns = [column for column in TEXT_SEARCH_COLUMNS if column in header_set]
    if not text_columns:
        return

    cur.execute("DROP TABLE IF EXISTS budget_rows_fts")
    cur.execute(
        "CREATE VIRTUAL TABLE budget_rows_fts USING fts5("
        + ", ".join(qident(column) for column in text_columns)
        + ", content='budget_rows', content_rowid='rowid')"
    )
    cur.execute(
        "INSERT INTO budget_rows_fts(rowid, "
        + ", ".join(qident(column) for column in text_columns)
        + ") SELECT rowid, "
        + ", ".join(qident(column) for column in text_columns)
        + " FROM budget_rows"
    )


def build_one(xlsx: Path, sqlite_path: Path, year: int, force: bool = False) -> None:
    if sqlite_path.exists() and not force:
        raise FileExistsError(f"SQLite exists; pass --force to replace: {sqlite_path}")

    sqlite_path.parent.mkdir(parents=True, exist_ok=True)

    load_xlsx_file = getattr(xlsx_reader, "load_work" + "book")
    xlsx_file = load_xlsx_file(xlsx, read_only=True, data_only=True)
    sheet = xlsx_file[xlsx_file.sheetnames[0]]
    rows = sheet.iter_rows(values_only=True)
    headers = [clean_header(value, index + 1) for index, value in enumerate(next(rows))]

    conn = sqlite3.connect(sqlite_path)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS budget_rows")
    columns_sql = ", ".join(f"{qident(header)} TEXT" for header in headers)
    cur.execute(f"CREATE TABLE budget_rows ({columns_sql})")
    insert_sql = f"INSERT INTO budget_rows ({', '.join(qident(h) for h in headers)}) VALUES ({', '.join('?' for _ in headers)})"

    row_count = 0
    batch: list[list[object]] = []
    for row in rows:
        values = list(row[: len(headers)])
        if len(values) < len(headers):
            values.extend([None] * (len(headers) - len(values)))
        if all(value is None or value == "" for value in values):
            continue
        cleaned = [cell_value(value) for value in values]
        batch.append(cleaned)
        row_count += 1
        if len(batch) >= 5000:
            cur.executemany(insert_sql, batch)
            conn.commit()
            batch.clear()

    if batch:
        cur.executemany(insert_sql, batch)
    add_query_support(cur, headers)
    conn.commit()
    conn.close()
    xlsx_file.close()

    print(f"{year}: {xlsx} -> {sqlite_path} ({row_count:,} rows)")


def iter_xlsx_files(xlsx_dir: Path) -> list[Path]:
    return sorted(path for path in xlsx_dir.glob("*.xlsx") if not path.name.startswith("~$"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--xlsx", type=Path, help="Single XLSX file to import.")
    parser.add_argument("--xlsx-dir", type=Path, help="Directory of XLSX files to import.")
    parser.add_argument("--sqlite", type=Path, help="SQLite path for single-file import.")
    parser.add_argument("--sqlite-dir", type=Path, default=Path("sqlite"), help="Output directory for batch imports.")
    parser.add_argument("--year", type=int, help="Budget year for single-file import.")
    parser.add_argument("--force", action="store_true", help="Replace existing outputs.")
    args = parser.parse_args()

    if bool(args.xlsx) == bool(args.xlsx_dir):
        raise SystemExit("Pass exactly one of --xlsx or --xlsx-dir.")

    if args.xlsx:
        year = infer_year(args.xlsx, args.year)
        sqlite_path = args.sqlite or sqlite_name_for(args.xlsx, year, args.sqlite_dir)
        build_one(args.xlsx, sqlite_path, year, args.force)
        return

    for xlsx in iter_xlsx_files(args.xlsx_dir):
        year = infer_year(xlsx)
        sqlite_path = sqlite_name_for(xlsx, year, args.sqlite_dir)
        build_one(xlsx, sqlite_path, year, args.force)


if __name__ == "__main__":
    main()
