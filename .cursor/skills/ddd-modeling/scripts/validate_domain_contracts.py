#!/usr/bin/env python3
"""Validate machine-readable DDD contracts."""
from __future__ import annotations
import argparse
import re
from pathlib import Path

INV_RE = re.compile(r"INV-\d{3}")
PATTERN_MARKERS = ("OHS", "ACL", "Conformist", "Partnership", "Shared Kernel")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def pick_file(root: Path, name: str) -> Path:
    md = root / f"{name}.md"
    tmpl = root / f"{name}.md.tmpl"
    if md.exists():
        return md
    if tmpl.exists():
        return tmpl
    return md


def validate(path: Path) -> int:
    errors: list[str] = []
    ul_path = pick_file(path, "ubiquitous-language")
    dm_path = pick_file(path, "domain-model")
    cm_path = pick_file(path, "context-map")

    ul = read_text(ul_path)
    dm = read_text(dm_path)
    cm = read_text(cm_path)

    if ul:
        if "Aliases to AVOID" not in ul:
            errors.append("UL missing 'Aliases to AVOID'")
        if "| BC |" not in ul and "|BC|" not in ul:
            errors.append("UL table missing BC column")
    else:
        errors.append(f"Missing {ul_path.name}")

    if dm:
        if not INV_RE.search(dm):
            errors.append("domain-model missing INV-xxx invariant")
    else:
        errors.append(f"Missing {dm_path.name}")

    if cm:
        if not any(marker in cm for marker in PATTERN_MARKERS):
            errors.append("context-map missing relationship pattern marker (OHS/ACL/Conformist/Partnership/Shared Kernel)")
    else:
        errors.append(f"Missing {cm_path.name}")

    if errors:
        print("DDD CONTRACT CHECK: ERROR")
        for err in errors:
            print(f"- {err}")
        return 1

    print("DDD CONTRACT CHECK: PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", required=True, help="Domain directory path")
    args = parser.parse_args()
    return validate(Path(args.path))


if __name__ == "__main__":
    raise SystemExit(main())
