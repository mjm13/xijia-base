---
name: /xijia-status
id: xijia-status
category: Workflow
description: Lightweight pipeline snapshot (fast, no full guard audit)
---

Provide a **fast, read-only** Xijia pipeline snapshot. Optimized for speed — not a release/verify audit.

## Goal

Decision-ready snapshot in **≤3 tool rounds**:

- Active requirement / change (if any)
- Tier, change type, stage (from file evidence only)
- Git working tree summary
- Optional quick test signal (only when backend changed)
- Next single action + blockers

## Scope (strict — do NOT expand)

### Allowed reads (pick minimal set)

1. **One** active requirement: `docs/requirements/inbox/*.md` — prefer the file user named; else the most recently modified inbox file only.
2. **If red tier suspected**: list `docs/openspec/changes/<name>/` for that change only (do not scan all changes).
3. `git status --short` (once).
4. **Optional** (only if requirement or git shows backend code touched): `cd backend && pytest -q --tb=no` with 60s budget; on failure report exit code only.

### Forbidden in this command

- Do **not** run `pipeline_guard.py` (`--check-release`, `--audit`, `--check-intake`, etc.).
- Do **not** load `xijia-ops-pipeline` full skill body or invoke verify/comment-sync/code-review/quality-judge.
- Do **not** read `.agents/**`, `document/**`, or unrelated requirement files.
- Do **not** implement code or mutate artifacts unless the user asks.

## How to determine status

1. From the **single** requirement doc: **YAML frontmatter** `tier` / `type`（优先），Gate-0/1/2 fields, AC checklist state. 正文「分级与判型」表格须与 frontmatter 一致。
2. Infer stage from **that doc + one change folder** (if applicable):
   - `plan` → `apply` → `verify` → `sync-knowledge` (green/yellow)
   - `explore` → `propose` → `analyze` → `apply` → … (red)
3. Mark `unknown` when evidence missing; ask **one** focused follow-up question max.

## Output format

```markdown
## Xijia Pipeline Status (lightweight)

- Requirement: <path|none>
- Tier: <green|green-trivial|yellow|red|unknown>
- Change: <name|none>
- Change Type: <business|technical|hybrid|unknown>
- Stage: <explore|propose|analyze|apply|verify|sync|archive|sync-knowledge|plan|unknown>
- Git: <clean | N modified/untracked (summary)>
- Tests: <passed|failed|skipped — reason>
- Next: <single best command/skill>
- Blockers: <none or list>
- Note: Full release audit → `/xijia:start` verify phase or `pipeline_guard.py --check-release`
```

## Guardrails

- Target latency: answer after minimal reads; prefer inference from requirement doc over deep repo scan.
- If user needs full Gate-2 / release guard evidence, tell them to run verify phase explicitly — do not run it here.
