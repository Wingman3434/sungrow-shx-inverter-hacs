#!/usr/bin/env python3
"""Refresh or verify the vendored library and its exact content hashes."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "custom_components/sungrow_shx_inverter/_vendor"
MANIFEST = DEST / "manifest.json"


def hashes() -> dict[str, str]:
    """Hash only distributable source and licence bytes."""
    return {
        str(p.relative_to(DEST)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(DEST.rglob("*"))
        if p.is_file()
        and p != MANIFEST
        and "__pycache__" not in p.parts
        and p.suffix != ".pyc"
    }


def main() -> None:
    """Copy an explicitly supplied source or validate the committed snapshot."""
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--source", type=Path)
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        expected = json.loads(MANIFEST.read_text())
        if hashes() != expected["sha256"]:
            raise SystemExit("Vendored source differs from its manifest")
        print("Vendored source and licence hashes match")
        return
    source = args.source.resolve()
    package = source / "src/sungrow_shx_inverter"
    if not (package / "device.py").is_file():
        raise SystemExit("Source must be a sungrow-shx-inverter repository")
    wanted = {
        p.relative_to(package)
        for p in package.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
    }
    existing = DEST / "sungrow_shx_inverter"
    stale = [
        p
        for p in existing.rglob("*")
        if p.is_file()
        and "__pycache__" not in p.parts
        and p.suffix != ".pyc"
        and p.relative_to(existing) not in wanted
    ]
    if stale:
        raise SystemExit(f"Remove obsolete vendored files explicitly first: {stale}")
    shutil.copytree(
        package,
        existing,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    for name in ("LICENSE", "NOTICE"):
        shutil.copy2(source / name, DEST / name)
    shutil.copytree(source / "LICENSES", DEST / "LICENSES", dirs_exist_ok=True)
    MANIFEST.write_text(
        json.dumps(
            {
                "package": "sungrow-shx-inverter",
                "upstream_release": "0.1.0-prepublication",
                "source": "https://github.com/Wingman3434/sungrow-shx-inverter-library",
                "sha256": hashes(),
            },
            indent=2,
        )
        + "\n"
    )
    print("Vendored source refreshed; run tests before release")


if __name__ == "__main__":
    main()
