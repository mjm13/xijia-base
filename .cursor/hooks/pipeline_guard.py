#!/usr/bin/env python3
"""Pipeline stage guard.

Three modes share one entry:

1. Hook mode (no CLI args): reads a Cursor afterEdit JSON payload from stdin.
   When core business code is edited and the edited file has no semantic
   comment tag, prints an immediate comment-sync reminder. It also warns when
   implementation code is edited while a red-tier requirement exists but its
   OpenSpec change products are missing. Never blocks (returns 0 always).

2. ``--check-apply --change <name> [--tier red]``: hard check before entering
   apply. Exits non-zero and lists missing artifacts when a red-tier change is
   missing required OpenSpec products. Used to reject "skip explore/propose".

3. ``--audit``: prints evidence-based stage snapshot (inbox tier, openspec
   change products, tasks.md progress, test files) for session recovery.

4. ``--check-comment-sync [--base <git-ref>]``: verify-stage hard check. Uses
   git diff to find changed core implementation files and fails (exit 1) when
   any of them carry no semantic comment tag. File-level heuristic: it catches
   "core code touched but file has zero semantic annotation"; it cannot prove
   every changed function is annotated.

5. ``--check-release [--base <git-ref>] [--req <path>]``: Gate-2 aggregate
   check. Hard-checks comment-sync, backend-test presence, approval records
   (when req provided), and ADR trigger coverage. Also prints non-blocking
   drift reminder for code-vs-domain docs.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
    except (AttributeError, ValueError):
        pass

ROOT = Path(__file__).resolve().parents[2]
INBOX_DIR = (ROOT / "docs" / "requirements" / "inbox").resolve()
CHANGES_DIR = (ROOT / "docs" / "openspec" / "changes").resolve()
NOTICE_MARKER = ROOT / "scripts" / ".generated" / "pipeline_guard_notice.txt"

# Implementation code (edits here imply we are in apply stage).
IMPL_PREFIXES = ("backend/app/", "frontend/src/")
# Paths that are NOT counted as implementation code.
NON_IMPL_RE = re.compile(r"(^|/)(tests?|__tests__)/|(^|/)test_|\.(test|spec)\.|\.md$|\.json$")
# Files in these areas are treated as core business code for comment-sync.
COMMENT_SYNC_PREFIXES = (
    "backend/app/access/",
    "backend/app/api/",
    "backend/app/models/",
    "backend/app/org/",
    "backend/app/system/",
)

# Frontmatter change types that imply business semantics / red-ish path.
RED_TYPES = {"business", "hybrid"}
RED_TEXT_RE = re.compile(r"tier[^\n]*\bred\b|分级[^\n]*red|🔴", re.IGNORECASE)

# Semantic comment tags from xijia-comment-enhancer (endpoint + internal layers).
SEMANTIC_TAG_RE = re.compile(r"\[(核心目的|接口地址|功能描述|业务逻辑)\]")


# --------------------------------------------------------------------------- #
# Shared helpers
# --------------------------------------------------------------------------- #
def _parse_frontmatter_type(text: str) -> str | None:
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    block = text[3:end]
    match = re.search(r"^\s*type\s*:\s*([A-Za-z]+)\s*$", block, re.MULTILINE)
    return match.group(1).strip().lower() if match else None


def _red_requirements() -> list[str]:
    """Return inbox requirement names that look like red-tier (need OpenSpec)."""
    if not INBOX_DIR.is_dir():
        return []
    found: list[str] = []
    for md in sorted(INBOX_DIR.glob("*.md")):
        text = md.read_text(encoding="utf-8", errors="ignore")
        fm_type = _parse_frontmatter_type(text)
        if fm_type in RED_TYPES or RED_TEXT_RE.search(text):
            found.append(md.stem)
    return found


def _has_any_change_product() -> bool:
    """True if at least one OpenSpec change dir contains a proposal.md."""
    if not CHANGES_DIR.is_dir():
        return False
    return any(child.is_dir() and (child / "proposal.md").is_file() for child in CHANGES_DIR.iterdir())


def _change_dir(change: str) -> Path:
    return (CHANGES_DIR / change).resolve()


def _missing_apply_artifacts(change: str, *, require_domain: bool) -> list[str]:
    base = _change_dir(change)
    missing: list[str] = []
    if not (base / "proposal.md").is_file():
        missing.append(f"{change}/proposal.md")
    if not (base / "tasks.md").is_file():
        missing.append(f"{change}/tasks.md")
    specs_dir = base / "specs"
    if not (specs_dir.is_dir() and any(specs_dir.rglob("*.md"))):
        missing.append(f"{change}/specs/**/*.md")
    if require_domain:
        domain_dir = base / "domain"
        if not (domain_dir.is_dir() and any(domain_dir.glob("*.md"))):
            missing.append(f"{change}/domain/*.md")
    return missing


# --------------------------------------------------------------------------- #
# Data-flow closure helpers (Gate-0)
# --------------------------------------------------------------------------- #
_CONFIRMED = {"已确认", "闭环", "ok", "done", "✓", "yes", "y", "true"}
_SEP_CELL_RE = re.compile(r"^:?-+:?$")
_PLACEHOLDER_RE = re.compile(r"^(-+|待.?补|待.?填|tbd|todo|n/?a|none|\.\.\.|…|<.*>)$", re.IGNORECASE)
_ISO_DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
_STATUS_RE = re.compile(r"(?:状态|status)\s*[:：]\s*([^|；;]+)")
_APPROVER_RE = re.compile(r"(?:审批人|签字|approver)\s*[:：]\s*([^|；;]+)")
_GREEN_TRIVIAL_MARKER = "本需求无数据流（green-trivial）"


def _is_unclosed_cell(value: str) -> bool:
    text = (value or "").strip()
    if not text:
        return True
    if "<" in text or ">" in text:
        return True
    if "待确认" in text or "..." in text or "…" in text:
        return True
    return False


def _is_confirmed_cell(value: str) -> bool:
    return (value or "").strip().lower() in _CONFIRMED


def _find_col(header_cells: list[str], keys: tuple[str, ...]) -> int | None:
    for idx, cell in enumerate(header_cells):
        if any(key.lower() in cell.lower() for key in keys):
            return idx
    return None


def _parse_closure_table(text: str) -> list[dict[str, str]] | None:
    """Return parsed rows, or None when no closure table header is found."""
    lines = text.splitlines()
    header_idx: int | None = None
    header_cells: list[str] = []
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("|") and "来源" in stripped and "去向" in stripped:
            header_idx = idx
            header_cells = [c.strip() for c in stripped.strip("|").split("|")]
            break
    if header_idx is None:
        return None

    i_name = _find_col(header_cells, ("能力", "AC"))
    i_src = _find_col(header_cells, ("来源", "source"))
    i_proc = _find_col(header_cells, ("加工", "process"))
    i_sink = _find_col(header_cells, ("去向", "sink"))
    i_close = _find_col(header_cells, ("闭环", "closure"))

    def cell(cells: list[str], idx: int | None) -> str:
        return cells[idx] if idx is not None and idx < len(cells) else ""

    rows: list[dict[str, str]] = []
    for line in lines[header_idx + 1 :]:
        stripped = line.strip()
        if not stripped.startswith("|"):
            break
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if all(_SEP_CELL_RE.match(c or "-") for c in cells):
            continue
        rows.append(
            {
                "name": cell(cells, i_name) or "(未命名能力)",
                "source": cell(cells, i_src),
                "process": cell(cells, i_proc),
                "sink": cell(cells, i_sink),
                "closure": cell(cells, i_close),
            }
        )
    return rows


def _is_placeholder(value: str) -> bool:
    text = (value or "").strip()
    return (not text) or bool(_PLACEHOLDER_RE.match(text))


def _parse_gate_cell(cell: str) -> dict[str, str]:
    value = (cell or "").strip()
    status = ""
    approver = ""
    date_value = ""

    status_match = _STATUS_RE.search(value)
    if status_match:
        status = status_match.group(1).strip()
    else:
        status = value.split("|")[0].split("（")[0].strip()

    approver_match = _APPROVER_RE.search(value)
    if approver_match:
        approver = approver_match.group(1).strip()

    date_match = _ISO_DATE_RE.search(value)
    if date_match:
        date_value = date_match.group(0)

    return {"status": status, "approver": approver, "date": date_value, "raw": value}


def _parse_gate_records(text: str) -> dict[str, dict[str, str]]:
    records: dict[str, dict[str, str]] = {}
    lines = text.splitlines()
    header_idx: int | None = None
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("|") and "项" in stripped and "值" in stripped:
            header_idx = idx
            break
    if header_idx is None:
        return records

    for line in lines[header_idx + 1 :]:
        stripped = line.strip()
        if not stripped.startswith("|"):
            break
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) < 2 or all(_SEP_CELL_RE.match(c or "-") for c in cells):
            continue
        key = cells[0]
        if key in {"Gate-0", "Gate-1", "Gate-2"}:
            records[key] = _parse_gate_cell(cells[1])
    return records


# --------------------------------------------------------------------------- #
# Hook mode
# --------------------------------------------------------------------------- #
def _extract_paths(payload: Any) -> list[str]:
    found: list[str] = []
    if isinstance(payload, dict):
        for key in ("path", "file_path", "relativePath", "filePath", "target_file", "oldPath", "newPath"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                found.append(value.strip())
        for nested_key in ("input", "arguments", "data", "payload", "tool_input", "edits", "changes"):
            found.extend(_extract_paths(payload.get(nested_key)))
    elif isinstance(payload, list):
        for item in payload:
            found.extend(_extract_paths(item))
    return found


def _to_rel(path_value: str) -> str | None:
    candidate = Path(path_value)
    candidate = candidate.resolve() if candidate.is_absolute() else (ROOT / candidate).resolve()
    try:
        return candidate.relative_to(ROOT).as_posix()
    except ValueError:
        return None


def _is_impl_code(rel: str) -> bool:
    return rel.startswith(IMPL_PREFIXES) and not NON_IMPL_RE.search(rel)


def _is_comment_sync_code(rel: str) -> bool:
    return rel.startswith(COMMENT_SYNC_PREFIXES) and not NON_IMPL_RE.search(rel)


def _already_noticed_today() -> bool:
    today = date.today().isoformat()
    if NOTICE_MARKER.is_file():
        if NOTICE_MARKER.read_text(encoding="utf-8", errors="ignore").strip() == today:
            return True
    NOTICE_MARKER.parent.mkdir(parents=True, exist_ok=True)
    NOTICE_MARKER.write_text(today, encoding="utf-8")
    return False


def _run_hook() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return 0

    edited_impl = {rel for raw in _extract_paths(payload) if (rel := _to_rel(raw)) and _is_impl_code(rel)}
    if not edited_impl:
        return 0

    missing_comments = sorted(
        rel for rel in edited_impl if _is_comment_sync_code(rel) and not _file_has_semantic_comment(rel)
    )
    if missing_comments:
        print("[pipeline-guard] 核心业务代码已编辑，但文件缺少 xijia 语义注释标签：")
        for rel in missing_comments:
            print(f"  - {rel}")
        print(
            "  → 写代码阶段必须同步注释：新增核心代码需按 xijia-comment-enhancer 输出注释；"
            "修改核心逻辑需同步更新既有注释。不得等到 verify 再补。"
        )

    red_reqs = _red_requirements()
    if not red_reqs or _has_any_change_product():
        return 0

    if _already_noticed_today():
        return 0

    print(
        "[pipeline-guard] 正在编辑实现代码，但检测到疑似 🔴/hybrid 需求且 "
        "docs/openspec/changes/ 无 proposal 产物："
    )
    for name in red_reqs:
        print(f"  - inbox/{name}.md")
    print(
        "  → 若为 red 档，应先补 explore→propose→analyze（OpenSpec change 产物）再 apply；"
        "运行 `python .cursor/hooks/pipeline_guard.py --audit` 核对阶段证据。"
    )
    return 0


# --------------------------------------------------------------------------- #
# CLI modes
# --------------------------------------------------------------------------- #
def _run_check_apply(change: str, tier: str) -> int:
    if tier != "red":
        print(f"[pipeline-guard] tier={tier}，跳过 OpenSpec 产物硬校验。")
        return 0
    if not _change_dir(change).is_dir():
        print(f"[pipeline-guard] 缺失 change 目录：docs/openspec/changes/{change}/")
        print("  → red 档进入 apply 前必须先完成 propose。禁止开始改实现代码。")
        return 1
    # require_domain unknown here; warn separately, hard-fail only on core docs.
    missing_core = _missing_apply_artifacts(change, require_domain=False)
    if missing_core:
        print(f"[pipeline-guard] red 档进入 apply 前 OpenSpec 产物缺失（change={change}）：")
        for item in missing_core:
            print(f"  - docs/openspec/changes/{item}")
        print("  → 回退补齐 propose/analyze 后再 apply。")
        return 1
    domain_missing = _missing_apply_artifacts(change, require_domain=True)
    if domain_missing:
        print(f"[pipeline-guard] 提醒：business/hybrid 建议补 domain 草稿（change={change}）：")
        for item in domain_missing:
            print(f"  - docs/openspec/changes/{item}")
    print(f"[pipeline-guard] OK：change={change} 核心 OpenSpec 产物齐备，可进入 apply。")
    return 0


def _run_check_intake(req_path: str, tier: str) -> int:
    path = Path(req_path)
    path = path.resolve() if path.is_absolute() else (ROOT / path).resolve()
    if not path.is_file():
        print(f"[pipeline-guard] 需求文档不存在：{req_path}")
        return 2

    text = path.read_text(encoding="utf-8", errors="ignore")
    if tier == "green-trivial" and _GREEN_TRIVIAL_MARKER in text:
        print("[pipeline-guard] green-trivial 且文档声明“本需求无数据流（green-trivial）”，跳过闭环表硬校验。")
        return 0

    rows = _parse_closure_table(text)
    if rows is None:
        print("[pipeline-guard] 未找到「数据流闭环表」（需含 来源/去向 表头）。Gate-0 不通过。")
        return 1
    if not rows:
        print("[pipeline-guard] 数据流闭环表为空。Gate-0 不通过。")
        return 1

    breaks: list[tuple[str, str, str]] = []
    for row in rows:
        for seg_key, seg_label in (("source", "来源"), ("process", "加工"), ("sink", "去向")):
            if _is_unclosed_cell(row[seg_key]):
                breaks.append((row["name"], seg_label, row[seg_key]))
        if not _is_confirmed_cell(row["closure"]):
            breaks.append((row["name"], "闭环状态", row["closure"]))

    if breaks:
        print("[pipeline-guard] 数据流未闭环，存在断点（Gate-0 不通过）：")
        for name, seg, val in breaks:
            print(f"  - {name} / {seg}: '{val.strip() or '空'}'")
        print("  → 补齐断点并经二次确认回环（重建+复核+用户终认）后再进入分级。")
        return 1

    print(f"[pipeline-guard] OK：{len(rows)} 条能力数据流闭环（来源→加工→去向）齐备，可进入分级。")
    return 0


# --------------------------------------------------------------------------- #
# Comment-sync check (verify stage)
# --------------------------------------------------------------------------- #
def _git_lines(args: list[str]) -> list[str]:
    try:
        out = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except (OSError, ValueError):
        return []
    if out.returncode != 0:
        return []
    return [line.strip() for line in out.stdout.splitlines() if line.strip()]


def _changed_impl_files(base: str) -> list[str]:
    """Changed + untracked core business implementation files relative to base ref."""
    changed = set(_git_lines(["diff", "--name-only", base]))
    changed.update(_git_lines(["ls-files", "--others", "--exclude-standard"]))
    return sorted(
        rel
        for raw in changed
        if (rel := _to_rel(raw)) and _is_comment_sync_code(rel)
    )


def _changed_all_files(base: str) -> list[str]:
    changed = set(_git_lines(["diff", "--name-only", base]))
    changed.update(_git_lines(["ls-files", "--others", "--exclude-standard"]))
    return sorted(rel for raw in changed if (rel := _to_rel(raw)))


def _file_has_semantic_comment(rel: str) -> bool:
    target = (ROOT / rel).resolve()
    if not target.is_file():
        return True  # deleted file: nothing to annotate
    text = target.read_text(encoding="utf-8", errors="ignore")
    return bool(SEMANTIC_TAG_RE.search(text))


def _run_check_comment_sync(base: str) -> int:
    impl_files = _changed_impl_files(base)
    if not impl_files:
        print("[pipeline-guard] 本次未触达核心实现代码，comment-sync 可跳过。")
        return 0

    missing = [rel for rel in impl_files if not _file_has_semantic_comment(rel)]
    if missing:
        print("[pipeline-guard] 以下实现文件无任何语义注释标签（comment-sync 未完成）：")
        for rel in missing:
            print(f"  - {rel}")
        print(
            "  → 必须调用 xijia-comment-enhancer 按内部层/端点层补注释后再宣告完成；"
            "纯文档/配置/样式/测试改动不应出现在此清单。"
        )
        return 1

    print(
        f"[pipeline-guard] OK：{len(impl_files)} 个变更实现文件均含语义注释标签"
        "（文件级启发式，仍需人工确认改动函数已覆盖）。"
    )
    return 0


_TEST_RE = re.compile(r"(^|/)(tests?|__tests__)/|(^|/)test_|\.(test|spec)\.")


def _changed_test_files(base: str) -> list[str]:
    changed = set(_git_lines(["diff", "--name-only", base]))
    changed.update(_git_lines(["ls-files", "--others", "--exclude-standard"]))
    return sorted(
        rel
        for raw in changed
        if (rel := _to_rel(raw)) and rel.startswith(("backend/", "frontend/"))
        and _TEST_RE.search(rel)
    )


def _needs_adr(files: list[str]) -> bool:
    for rel in files:
        if rel in {"backend/requirements.txt", "frontend/package.json", "frontend/package-lock.json", "frontend/yarn.lock"}:
            return True
        if rel.startswith("backend/alembic/versions/") and rel.endswith(".py"):
            return True
        if rel.startswith("backend/app/access/") or "/auth" in rel:
            return True
    return False


def _run_check_release(base: str, req_path: str) -> int:
    """Gate-2 aggregate backstop: comment-sync + test presence + manual-gate reminder."""
    blocking: list[str] = []
    changed_files = _changed_all_files(base)

    impl_files = _changed_impl_files(base)
    missing = [rel for rel in impl_files if not _file_has_semantic_comment(rel)]
    if missing:
        blocking.append("comment-sync 未完成")
        print("[release] comment-sync 缺失（核心业务文件无语义注释）：")
        for rel in missing:
            print(f"  - {rel}")
    elif impl_files:
        print(f"[release] comment-sync OK：{len(impl_files)} 个核心业务文件均含语义注释标签。")
    else:
        print("[release] 本次未触达核心业务代码（comment-sync 不适用）。")

    backend_impl = [rel for rel in impl_files if rel.startswith("backend/app/")]
    if backend_impl and not _changed_test_files(base):
        blocking.append("后端业务代码变更但无测试文件变更")
        print("[release] 后端核心业务代码已改，但未见 backend/tests 下测试变更（TDD 门禁存疑）：")
        for rel in backend_impl:
            print(f"  - {rel}")
        print("  → 按 backend-test / test-driven-development 补可执行验证，或在验收记录说明豁免理由。")

    if req_path:
        req = Path(req_path)
        req = req.resolve() if req.is_absolute() else (ROOT / req).resolve()
        if not req.is_file():
            blocking.append("需求文档不存在")
            print(f"[release] 审批留痕校验失败：需求文档不存在 {req_path}")
        else:
            req_text = req.read_text(encoding="utf-8", errors="ignore")
            gate_records = _parse_gate_records(req_text)
            gate0 = gate_records.get("Gate-0")
            gate1 = gate_records.get("Gate-1")

            if not gate0:
                blocking.append("Gate-0 记录缺失")
                print("[release] 审批留痕缺失：未找到 Gate-0 记录。")
            else:
                gate0_status = gate0["status"].lower()
                if gate0_status not in {"complete", "passed", "pass"}:
                    blocking.append("Gate-0 状态未通过")
                    print(f"[release] Gate-0 状态不合规：{gate0['raw']}")
                if _is_placeholder(gate0["approver"]) or _is_placeholder(gate0["date"]):
                    blocking.append("Gate-0 审批人/日期缺失")
                    print(f"[release] Gate-0 缺审批人或日期：{gate0['raw']}")

            if not gate1:
                blocking.append("Gate-1 记录缺失")
                print("[release] 审批留痕缺失：未找到 Gate-1 记录。")
            else:
                if "已批准" not in gate1["status"] and "approved" not in gate1["status"].lower():
                    blocking.append("Gate-1 状态未批准")
                    print(f"[release] Gate-1 状态不合规：{gate1['raw']}")
                if _is_placeholder(gate1["approver"]) or _is_placeholder(gate1["date"]):
                    blocking.append("Gate-1 审批人/日期缺失")
                    print(f"[release] Gate-1 缺审批人或日期：{gate1['raw']}")

            gate2 = gate_records.get("Gate-2")
            if gate2 and (("已验收" in gate2["status"]) or ("accepted" in gate2["status"].lower())):
                if _is_placeholder(gate2["approver"]) or _is_placeholder(gate2["date"]):
                    print(f"[release] 提醒：Gate-2 标记已验收，但审批人/日期未填写完整：{gate2['raw']}")
            elif gate2:
                print("[release] 提醒：Gate-2 尚未签字，状态迁移/归档前必须用户人工验收签字。")
            else:
                print("[release] 提醒：未找到 Gate-2 行，归档前请在需求文档补齐验收签字记录。")

    if _needs_adr(changed_files):
        has_adr_change = any(rel.startswith("docs/decisions/") and rel.endswith(".md") for rel in changed_files)
        if not has_adr_change:
            blocking.append("命中 ADR 触发条件但未新增/更新 docs/decisions/*.md")
            print("[release] 命中 ADR 触发条件（依赖/迁移/权限安全），但未检测到 docs/decisions/*.md 变更。")

    has_domain_or_capability_doc = any(
        rel.startswith("docs/domain/") or rel == "docs/capability-map.md" for rel in changed_files
    )
    if impl_files and not has_domain_or_capability_doc:
        print("[release] 提醒：核心业务代码有变更，但未检测到 docs/domain/ 或 docs/capability-map.md 变更。")
        print("  → 请在 sync-knowledge 阶段确认是否需要更新领域知识文档。")

    print(
        "[release] 人工门禁（脚本无法客观判定，须在 verify 输出与 Gate-2 留痕）：\n"
        "  - requesting-code-review: done|skipped+reason\n"
        "  - quality-judge: pass|revise（revise 不得宣告完成）\n"
        "  - Gate-2: 用户人工验收签字后方可状态迁移/归档\n"
        "  - Deferred 项是否已写入 docs/requirements/backlog.md"
    )

    if blocking:
        print(f"[release] BLOCKED：{', '.join(blocking)} —— 不得进入 Gate-2/归档。")
        return 1
    print("[release] 客观项通过；人工门禁请按上方清单逐条确认后再签字。")
    return 0


def _run_audit() -> int:
    print("== pipeline-guard 阶段证据自检 ==")

    red_reqs = _red_requirements()
    print(f"[inbox] 疑似 🔴/hybrid 需求: {', '.join(red_reqs) or '(无)'}")

    if CHANGES_DIR.is_dir():
        change_dirs = [c for c in sorted(CHANGES_DIR.iterdir()) if c.is_dir()]
    else:
        change_dirs = []
    if not change_dirs:
        print("[openspec] docs/openspec/changes/ 无任何 change 目录")
    for change in change_dirs:
        products = [
            name
            for name in ("proposal.md", "design.md", "tasks.md")
            if (change / name).is_file()
        ]
        has_specs = (change / "specs").is_dir() and any((change / "specs").rglob("*.md"))
        has_domain = (change / "domain").is_dir() and any((change / "domain").glob("*.md"))
        tasks_file = change / "tasks.md"
        if tasks_file.is_file():
            text = tasks_file.read_text(encoding="utf-8", errors="ignore")
            done = len(re.findall(r"^\s*-\s*\[x\]", text, re.MULTILINE | re.IGNORECASE))
            total = len(re.findall(r"^\s*-\s*\[[ xX]\]", text, re.MULTILINE))
            tasks_progress = f"{done}/{total}"
        else:
            tasks_progress = "n/a"
        extras = []
        if has_specs:
            extras.append("specs")
        if has_domain:
            extras.append("domain")
        print(
            f"[openspec] {change.name}: products={products + extras or '(空)'} "
            f"tasks={tasks_progress}"
        )

    impl_files = _changed_impl_files("HEAD")
    if impl_files:
        missing = [rel for rel in impl_files if not _file_has_semantic_comment(rel)]
        print(
            f"[comment-sync] 变更实现文件 {len(impl_files)} 个，"
            f"疑似缺语义注释 {len(missing)} 个"
            + (f"：{', '.join(missing)}" if missing else "（文件级启发式）")
        )
    else:
        print("[comment-sync] 本次未触达核心实现代码")

    print("[hint] verify 三件套（comment-enhancer/code-review/quality-judge）若无产出记录，按未完成处理。")
    return 0


def main() -> int:
    if len(sys.argv) <= 1:
        return _run_hook()

    parser = argparse.ArgumentParser(description="Pipeline stage guard")
    parser.add_argument("--check-apply", action="store_true", help="hard-check before apply")
    parser.add_argument("--check-intake", action="store_true", help="check Gate-0 data-flow closure table")
    parser.add_argument(
        "--check-comment-sync",
        action="store_true",
        help="verify-stage: changed impl files must carry semantic comment tags",
    )
    parser.add_argument(
        "--check-release",
        action="store_true",
        help="Gate-2 aggregate backstop: comment-sync + tests + approval traces + ADR trigger",
    )
    parser.add_argument("--audit", action="store_true", help="print stage evidence snapshot")
    parser.add_argument("--change", default="", help="OpenSpec change name")
    parser.add_argument("--req", default="", help="requirement markdown path (for --check-intake/--check-release)")
    parser.add_argument("--base", default="HEAD", help="git base ref for --check-comment-sync / --check-release")
    parser.add_argument("--tier", default="red", help="requirement tier (green/yellow/red/green-trivial)")
    args = parser.parse_args()

    if args.audit:
        return _run_audit()
    if args.check_release:
        return _run_check_release(args.base, args.req)
    if args.check_comment_sync:
        return _run_check_comment_sync(args.base)
    if args.check_intake:
        if not args.req:
            print("[pipeline-guard] --check-intake 需要 --req <path>")
            return 2
        return _run_check_intake(args.req, args.tier.lower())
    if args.check_apply:
        if not args.change:
            print("[pipeline-guard] --check-apply 需要 --change <name>")
            return 2
        return _run_check_apply(args.change, args.tier.lower())

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
