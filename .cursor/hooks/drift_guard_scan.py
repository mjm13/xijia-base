#!/usr/bin/env python3
"""Scan updated rules/skills files for stack-specific drift terms."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SCAN_ROOTS = (
    (ROOT / ".cursor" / "rules").resolve(),
    (ROOT / ".cursor" / "skills").resolve(),
)
DRIFT_RE = re.compile(r"Flyway|MyBatis|Spring|JUnit|@SpringBootTest|Mapper|Maven|org_node|BCrypt|Vitest|vite\.config")


def _extract_paths(payload: Any) -> list[str]:
    found: list[str] = []
    if isinstance(payload, dict):
        for key in (
            "path",
            "file_path",
            "relativePath",
            "filePath",
            "target_file",
            "oldPath",
            "newPath",
        ):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                found.append(value.strip())
        for nested_key in ("input", "arguments", "data", "payload", "tool_input", "edits", "changes"):
            nested = payload.get(nested_key)
            found.extend(_extract_paths(nested))
    elif isinstance(payload, list):
        for item in payload:
            found.extend(_extract_paths(item))
    return found


def _normalize(path_value: str) -> Path | None:
    candidate = Path(path_value)
    if not candidate.is_absolute():
        candidate = (ROOT / candidate).resolve()
    else:
        candidate = candidate.resolve()
    for scan_root in SCAN_ROOTS:
        try:
            candidate.relative_to(scan_root)
            return candidate
        except ValueError:
            continue
    return None


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return 0

    checked: set[Path] = set()
    for raw_path in _extract_paths(payload):
        path = _normalize(raw_path)
        if path is None or path in checked or not path.is_file():
            continue
        checked.add(path)
        text = path.read_text(encoding="utf-8", errors="ignore")
        hits = sorted(set(DRIFT_RE.findall(text)))
        if hits:
            rel = path.relative_to(ROOT).as_posix()
            print(f"[drift-scan] potential stack term in {rel}: {', '.join(hits)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
