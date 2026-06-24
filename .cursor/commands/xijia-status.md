---
name: /xijia-status
id: xijia-status
category: Workflow
description: Show current Xijia pipeline stage and next actions
---

Inspect current workspace context and report the current Xijia pipeline status.

## Goal

Provide a fast, decision-ready snapshot:

- Tier: `green | yellow | red`
- Change type: `business | technical | hybrid` (if identified)
- Current stage
- Progress signals (artifacts/tasks)
- Next best action
- Blockers / required confirmations

## How to determine status

1. Read `.cursor/rules/00-workflow.mdc` for tiering and gate criteria.
2. Inspect active change context (if any) via OpenSpec status/instructions.
3. Infer stage from evidence, using this order:
   - `explore` -> `propose` -> `apply` -> `verify` -> `sync` -> `archive` -> `sync-knowledge`
4. If no active OpenSpec change is needed, report as green/yellow plan path.
5. If information is ambiguous, explicitly mark fields as `unknown` and ask one focused follow-up question.

## Output format

Always use this block:

```markdown
## Xijia Pipeline Status

- Tier: <green|yellow|red|unknown>
- Change: <name|none>
- Change Type: <business|technical|hybrid|unknown>
- Stage: <explore|propose|apply|verify|sync|archive|sync-knowledge|abandon|plan>
- Progress: <N/M tasks, artifacts state, or n/a>
- Next: <single best next command/skill>
- Blockers: <none or list>
```

## Guardrails

- Do not implement code in this command.
- Do not mutate artifacts unless the user asks.
- Prefer concrete evidence over assumptions.
