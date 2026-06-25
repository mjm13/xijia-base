#!/usr/bin/env python3
"""Log docs read events from Cursor beforeReadFile hook."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DOCS_ROOT = (ROOT / "docs").resolve()
USAGE_LOG = ROOT / "scripts" / ".generated" / "docs_usage.jsonl"


def _extract_path(payload: Any) -> str | None:
    if isinstance(payload, dict):
        for key in ("file_path", "path", "relativePath", "filePath", "target_file"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        for nested_key in ("input", "arguments", "data", "payload", "tool_input"):
            nested = payload.get(nested_key)
            candidate = _extract_path(nested)
            if candidate:
                return candidate
    elif isinstance(payload, list):
        for item in payload:
            candidate = _extract_path(item)
            if candidate:
                return candidate
    return None


def _resolve_doc(path_value: str) -> str | None:
    candidate = Path(path_value)
    if not candidate.is_absolute():
        candidate = (ROOT / candidate).resolve()
    else:
        candidate = candidate.resolve()
    try:
        rel = candidate.relative_to(DOCS_ROOT)
    except ValueError:
        return None
    return f"docs/{rel.as_posix()}"


def _extract_session(payload: Any) -> str | None:
    if not isinstance(payload, dict):
        return None
    for key in ("session_id", "sessionId", "conversation_id", "conversationId", "chat_id", "chatId"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    for nested_key in ("input", "arguments", "data", "payload", "tool_input"):
        nested = payload.get(nested_key)
        candidate = _extract_session(nested)
        if candidate:
            return candidate
    return None


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return 0

    path_value = _extract_path(payload)
    if not path_value:
        return 0

    doc = _resolve_doc(path_value)
    if not doc:
        return 0

    USAGE_LOG.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "doc": doc,
        "source": "hook",
        "session": _extract_session(payload),
    }
    with USAGE_LOG.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
