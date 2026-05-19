"""Export FastAPI's OpenAPI schema to a target JSON file.

The frontend's openapi-ts pipeline reads this file to regenerate the typed
TanStack Query client. Run via `just gen-openapi-schema` or directly with
`python -m app.cli.export_openapi --out <path>`.
"""

import argparse
import json
from pathlib import Path

from app.main import app


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        required=True,
        help="Output path for the OpenAPI JSON file.",
    )
    args = parser.parse_args()

    schema = app.openapi()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes((json.dumps(schema, indent=2) + "\n").encode("utf-8"))
    print(f"wrote {args.out} ({len(schema['paths'])} paths)")


if __name__ == "__main__":
    main()
