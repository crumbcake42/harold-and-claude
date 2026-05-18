"""Export FastAPI's OpenAPI schema to backend/openapi.json.

The frontend's openapi-ts pipeline reads this file to regenerate the typed
TanStack Query client. Run via `just gen-openapi-schema` or directly.
"""

import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = BACKEND_ROOT.parent
sys.path.insert(0, str(BACKEND_ROOT))

from app.main import app  # noqa: E402

OUTPUT = REPO_ROOT / "contracts" / "openapi.json"


def main() -> None:
    schema = app.openapi()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(REPO_ROOT)} ({len(schema['paths'])} paths)")


if __name__ == "__main__":
    main()
