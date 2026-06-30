#!/usr/bin/env python3
"""Score docs by usage events and usefulness judgments."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
DOCS_ROOT = ROOT / "docs"
GENERATED_DIR = ROOT / "scripts" / ".generated"
USAGE_LOG = GENERATED_DIR / "docs_usage.jsonl"
JUDGMENTS_LOG = GENERATED_DIR / "docs_judgments.jsonl"
SCORE_JSON = GENERATED_DIR / "docs_score.json"
REPORT_MD = ROOT / ".cursor" / "skills" / "xijia-docs-score" / "reports" / "文档评分报告.md"


@dataclass
class DocStats:
    used_count: int = 0
    useful: int = 0
    neutral: int = 0
    misleading: int = 0
    score: int = 0
    last_used_at: str | None = None
    last_judged_at: str | None = None
    last_judgment_reason: str | None = None
    sources: Counter[str] | None = None
    sessions: set[str] | None = None
    classification: str = ""
    useless_candidate: bool = False
    negative_candidate: bool = False
    stale_candidate: bool = False
    candidate_reasons: list[str] | None = None

    def __post_init__(self) -> None:
        if self.sources is None:
            self.sources = Counter()
        if self.sessions is None:
            self.sessions = set()
        if self.candidate_reasons is None:
            self.candidate_reasons = []


def is_aux_doc(doc: str) -> bool:
    name = Path(doc).name
    return name.startswith("_") or name.lower() == "readme.md"


def is_experience_doc(doc: str) -> bool:
    return doc.startswith("docs/pitfalls/") or doc.startswith("docs/patterns/")


def parse_frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return ""
    end = text.find("\n---\n", 4)
    if end == -1:
        return ""
    return text[4:end]


def extract_frontmatter_fields(doc_path: Path) -> tuple[str | None, list[str]]:
    if not doc_path.exists():
        return None, []
    text = doc_path.read_text(encoding="utf-8")
    frontmatter = parse_frontmatter(text)
    if not frontmatter:
        return None, []
    last_verified_match = re.search(r"(?m)^last_verified:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})\s*$", frontmatter)
    last_verified = last_verified_match.group(1) if last_verified_match else None
    source_paths = re.findall(r"(?m)^\s*path:\s*([^\n#]+?)\s*$", frontmatter)
    cleaned = [p.strip().strip("'\"") for p in source_paths if p.strip()]
    return last_verified, cleaned


def git_latest_change_ts(path_str: str) -> datetime | None:
    cmd = ["git", "log", "-1", "--format=%cI", "--", path_str]
    try:
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)
    except OSError:
        return None
    if proc.returncode != 0:
        return None
    return to_dt(proc.stdout.strip())


def iter_docs() -> list[str]:
    docs: list[str] = []
    if DOCS_ROOT.is_dir():
        for path in DOCS_ROOT.rglob("*.md"):
            rel = path.relative_to(ROOT).as_posix()
            if rel.startswith("docs/"):
                docs.append(rel)
    return sorted(docs)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            rows.append(obj)
    return rows


def append_jsonl(path: Path, rows: list[dict[str, Any]]) -> int:
    if not rows:
        return 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return len(rows)


def to_dt(ts: Any) -> datetime | None:
    if not isinstance(ts, str) or not ts.strip():
        return None
    text = ts.strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def latest_judgments_map(rows: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    latest: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        doc = row.get("doc")
        session = row.get("session")
        verdict = row.get("verdict")
        if not isinstance(doc, str) or not isinstance(session, str):
            continue
        if verdict not in {"useful", "neutral", "misleading"}:
            continue
        key = (doc, session)
        ts = to_dt(row.get("ts")) or datetime.min.replace(tzinfo=timezone.utc)
        old = latest.get(key)
        old_ts = to_dt(old.get("ts")) if old else None
        if old is None or old_ts is None or ts >= old_ts:
            latest[key] = row
    return latest


def classify(stats: DocStats) -> str:
    if stats.used_count == 0:
        return "从未被用"
    if (stats.useful + stats.neutral + stats.misleading) == 0:
        return "已用·未判定"
    if stats.score >= 2 and stats.useful > stats.misleading:
        return "高价值"
    if stats.score < 0:
        return "低价值"
    return "一般"


def aggregate_scores() -> dict[str, DocStats]:
    docs = set(iter_docs())
    usage_rows = load_jsonl(USAGE_LOG)
    judgment_rows = load_jsonl(JUDGMENTS_LOG)

    for row in usage_rows:
        doc = row.get("doc")
        if isinstance(doc, str) and doc.startswith("docs/"):
            docs.add(doc)
    for row in judgment_rows:
        doc = row.get("doc")
        if isinstance(doc, str) and doc.startswith("docs/"):
            docs.add(doc)

    stats: dict[str, DocStats] = {doc: DocStats() for doc in sorted(docs)}

    for row in usage_rows:
        doc = row.get("doc")
        if not isinstance(doc, str) or doc not in stats:
            continue
        item = stats[doc]
        item.used_count += 1
        source = row.get("source")
        if isinstance(source, str) and source:
            item.sources[source] += 1
        session = row.get("session")
        if isinstance(session, str) and session:
            item.sessions.add(session)
        ts = to_dt(row.get("ts"))
        if ts:
            current = to_dt(item.last_used_at)
            if current is None or ts > current:
                item.last_used_at = ts.isoformat()

    latest = latest_judgments_map(judgment_rows)
    for row in latest.values():
        doc = row["doc"]
        verdict = row["verdict"]
        item = stats[doc]
        if verdict == "useful":
            item.useful += 1
        elif verdict == "neutral":
            item.neutral += 1
        else:
            item.misleading += 1
        ts = to_dt(row.get("ts"))
        if ts:
            current = to_dt(item.last_judged_at)
            if current is None or ts > current:
                item.last_judged_at = ts.isoformat()
                reason = row.get("reason")
                item.last_judgment_reason = reason if isinstance(reason, str) else None

    for doc, item in stats.items():
        item.score = item.useful - item.misleading
        item.classification = classify(item)
        if is_aux_doc(doc):
            continue
        if item.used_count == 0:
            item.useless_candidate = True
            item.candidate_reasons.append("从未被用")
        if item.used_count >= 3 and item.useful == 0 and item.misleading == 0:
            item.useless_candidate = True
            item.candidate_reasons.append("多次被用但长期未产生有效判定")
        if item.used_count >= 5 and item.neutral >= 3 and item.useful == 0:
            item.useless_candidate = True
            item.candidate_reasons.append("频繁中性且无正向贡献")
        if item.score < 0:
            item.negative_candidate = True
            item.candidate_reasons.append("误导判定多于有用判定")
        if is_experience_doc(doc):
            last_verified, source_paths = extract_frontmatter_fields(ROOT / doc)
            if not last_verified:
                item.stale_candidate = True
                item.candidate_reasons.append("缺少 last_verified，无法确认经验时效")
                continue
            last_verified_dt = to_dt(f"{last_verified}T00:00:00+00:00")
            if not source_paths:
                item.stale_candidate = True
                item.candidate_reasons.append("缺少 sources.path，无法进行腐化检测")
                continue
            if last_verified_dt is None:
                item.stale_candidate = True
                item.candidate_reasons.append("last_verified 格式无效")
                continue
            source_updates = [git_latest_change_ts(path) for path in source_paths]
            source_updates = [ts for ts in source_updates if ts is not None]
            if source_updates and max(source_updates) > last_verified_dt:
                item.stale_candidate = True
                item.candidate_reasons.append("sources 已更新，经验文档待复核")
    return stats


def serialize(stats: dict[str, DocStats]) -> dict[str, Any]:
    summary = Counter(item.classification for item in stats.values())
    docs = []
    for doc, item in sorted(stats.items(), key=lambda kv: (-kv[1].score, -kv[1].used_count, kv[0])):
        docs.append(
            {
                "doc": doc,
                "score": item.score,
                "classification": item.classification,
                "used_count": item.used_count,
                "useful": item.useful,
                "neutral": item.neutral,
                "misleading": item.misleading,
                "last_used_at": item.last_used_at,
                "last_judged_at": item.last_judged_at,
                "last_judgment_reason": item.last_judgment_reason,
                "sources": dict(item.sources),
                "session_count": len(item.sessions),
                "useless_candidate": item.useless_candidate,
                "negative_candidate": item.negative_candidate,
                "stale_candidate": item.stale_candidate,
                "candidate_reasons": item.candidate_reasons,
            }
        )
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "formula": "score = useful - misleading",
        "docs_total": len(stats),
        "summary_by_classification": dict(summary),
        "docs": docs,
    }


def write_report(payload: dict[str, Any]) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    docs = payload["docs"]
    lines = [
        "# 文档评分报告",
        "",
        f"更新时间：{now}",
        "范围：`docs/**`",
        "统计口径：研发使用事件 + 判定事件；`score = useful - misleading`",
        "",
        "## 分类统计",
        "",
    ]
    for key, value in sorted(payload["summary_by_classification"].items()):
        lines.append(f"- {key}：{value}")

    lines.extend(["", "## Top 20 高价值候选", ""])
    top = sorted(docs, key=lambda d: (-d["score"], -d["used_count"], d["doc"]))[:20]
    for item in top:
        lines.append(f"- `{item['doc']}`：score={item['score']} used={item['used_count']}")

    lines.extend(["", "## 从未被用（删除候选）", ""])
    never_used = [d for d in docs if d["used_count"] == 0 and not is_aux_doc(d["doc"])]
    if never_used:
        for item in sorted(never_used, key=lambda d: d["doc"]):
            lines.append(f"- `{item['doc']}`")
    else:
        lines.append("- 无")

    lines.extend(["", "## 低价值/误导候选", ""])
    negative = [d for d in docs if d.get("negative_candidate")]
    if negative:
        for item in sorted(negative, key=lambda d: (d["score"], d["doc"])):
            reasons = "；".join(item.get("candidate_reasons") or [])
            lines.append(f"- `{item['doc']}`（score={item['score']}）: {reasons}")
    else:
        lines.append("- 无")

    lines.extend(["", "## 待复核经验文档（sources 晚于 last_verified）", ""])
    stale = [d for d in docs if d.get("stale_candidate")]
    if stale:
        for item in sorted(stale, key=lambda d: d["doc"]):
            reasons = "；".join(item.get("candidate_reasons") or [])
            lines.append(f"- `{item['doc']}`: {reasons}")
    else:
        lines.append("- 无")

    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def append_judgment(doc: str, session: str, verdict: str, reason: str) -> None:
    if verdict not in {"useful", "neutral", "misleading"}:
        raise SystemExit("judge-verdict must be useful|neutral|misleading")
    doc_norm = doc.replace("\\", "/")
    if not doc_norm.startswith("docs/"):
        doc_norm = f"docs/{doc_norm.lstrip('./')}"
    reason = reason.strip()
    if not reason:
        raise SystemExit("judge-reason cannot be empty")
    event = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "doc": doc_norm,
        "session": session.strip(),
        "verdict": verdict,
        "reason": reason,
    }
    append_jsonl(JUDGMENTS_LOG, [event])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score docs by usage and judgments.")
    parser.add_argument("--doc", type=str, default="", help="Show one doc detail.")
    parser.add_argument("--top", type=int, default=0, help="Show top N docs.")
    parser.add_argument("--never-used", action="store_true", help="List never used docs.")
    parser.add_argument("--useless-candidates", action="store_true", help="List useless candidates.")
    parser.add_argument("--negative-candidates", action="store_true", help="List negative candidates.")
    parser.add_argument("--judge-doc", type=str, default="", help="Append judgment doc path.")
    parser.add_argument("--judge-session", type=str, default="", help="Append judgment session id.")
    parser.add_argument("--judge-verdict", type=str, default="", help="Append verdict.")
    parser.add_argument("--judge-reason", type=str, default="", help="Append reason.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)

    if any([args.judge_doc, args.judge_session, args.judge_verdict, args.judge_reason]):
        if not all([args.judge_doc, args.judge_session, args.judge_verdict, args.judge_reason]):
            raise SystemExit("Provide all --judge-* arguments together")
        append_judgment(args.judge_doc, args.judge_session, args.judge_verdict, args.judge_reason)
        print("judgment appended")

    stats = aggregate_scores()
    payload = serialize(stats)
    SCORE_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_report(payload)
    print(f"score json updated: {SCORE_JSON.relative_to(ROOT).as_posix()}")
    print(f"report updated: {REPORT_MD.relative_to(ROOT).as_posix()}")

    if args.doc:
        target = args.doc.replace("\\", "/")
        if not target.startswith("docs/"):
            target = f"docs/{target.lstrip('./')}"
        row = next((x for x in payload["docs"] if x["doc"] == target), None)
        if not row:
            print(f"未找到文档：{target}")
            return 1
        print(json.dumps(row, ensure_ascii=False, indent=2))
    if args.top > 0:
        rows = sorted(payload["docs"], key=lambda d: (-d["score"], -d["used_count"], d["doc"]))[: args.top]
        for item in rows:
            print(f"{item['doc']} | score={item['score']} | used={item['used_count']}")
    if args.never_used:
        rows = [d for d in payload["docs"] if d["used_count"] == 0]
        for item in sorted(rows, key=lambda d: d["doc"]):
            print(item["doc"])
    if args.useless_candidates:
        rows = [d for d in payload["docs"] if d.get("useless_candidate")]
        for item in sorted(rows, key=lambda d: d["doc"]):
            print(f"{item['doc']} | score={item['score']}")
    if args.negative_candidates:
        rows = [d for d in payload["docs"] if d.get("negative_candidate")]
        for item in sorted(rows, key=lambda d: (d["score"], d["doc"])):
            print(f"{item['doc']} | score={item['score']} | misleading={item['misleading']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
