#!/usr/bin/env python3
"""Fail on syntax that the project's supported Python versions cannot parse.

Ruff is not a syntax gate here: `ruff check` accepts the Python 3.14-only
unparenthesized `except A, B:` form, and the Ruff formatter even writes it, but
CPython 3.12/3.13 reject it with `SyntaxError: multiple exception types must be
parenthesized`. Parsing with `ast.parse(..., feature_version=...)` rejects that
form regardless of the interpreter running this script.
"""

from __future__ import annotations

import ast
from pathlib import Path
import sys

# The sungrow-shx-inverter library declares `requires-python = ">=3.12"`, so the
# shipped source must parse at 3.12 even though it runs on Home Assistant's 3.14.
MIN_VERSION = (3, 12)
SKIP_DIRS = {".venv", "__pycache__", ".ruff_cache", ".mypy_cache", "config"}


def main() -> int:
    """Parse every shipped module with the minimum supported grammar."""
    failures: list[str] = []
    for path in sorted(Path().rglob("*.py")):
        if SKIP_DIRS.intersection(path.parts):
            continue
        source = path.read_text(encoding="utf-8")
        try:
            ast.parse(source, filename=str(path), feature_version=MIN_VERSION)
        except SyntaxError as err:
            failures.append(f"{path}:{err.lineno}: {err.msg}")
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print(f"syntax check passed (feature_version={MIN_VERSION})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
