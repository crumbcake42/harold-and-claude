"""
Redact proprietary values in a CSV by mapping each unique value (per column)
to an arbitrary placeholder. Emits a redacted CSV plus a JSON map so the
import can be reviewed against the original data afterward.

Usage:
    python -m app.cli.redact_csv INPUT.csv OUTPUT.csv MAP.json
    python -m app.cli.redact_csv INPUT.csv OUTPUT.csv MAP.json --keep date,hours
    python -m app.cli.redact_csv INPUT.csv OUTPUT.csv MAP.json --only project,person
"""
import argparse
import csv
import json
from pathlib import Path


def redact(input_path: Path, output_path: Path, map_path: Path,
           keep: set[str] | None = None, only: set[str] | None = None) -> None:
    with input_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    if only:
        cols = [c for c in fieldnames if c in only]
    else:
        cols = [c for c in fieldnames if c not in (keep or set())]

    mapping: dict[str, dict[str, str]] = {c: {} for c in cols}

    for row in rows:
        for col in cols:
            val = row[col]
            if val not in mapping[col]:
                mapping[col][val] = f"{col}_{len(mapping[col]) + 1:04d}"
            row[col] = mapping[col][val]

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    with map_path.open("w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(rows)} rows to {output_path}")
    for col in cols:
        print(f"  {col}: {len(mapping[col])} unique values redacted")
    print(f"Map written to {map_path}")


def parse_csv_list(s: str) -> set[str]:
    return {x.strip() for x in s.split(",") if x.strip()}


def main() -> None:
    p = argparse.ArgumentParser(description="Redact proprietary CSV values.")
    p.add_argument("input", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("map", type=Path, help="JSON file mapping original -> redacted, per column")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--keep", type=parse_csv_list, default=None,
                   help="Comma-separated columns to leave untouched (default: redact all)")
    g.add_argument("--only", type=parse_csv_list, default=None,
                   help="Comma-separated columns to redact (others pass through unchanged)")
    args = p.parse_args()
    redact(args.input, args.output, args.map, keep=args.keep, only=args.only)


if __name__ == "__main__":
    main()
