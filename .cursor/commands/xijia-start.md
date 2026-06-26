---
name: /xijia-start
id: xijia-start
category: Workflow
description: Xijia unified R&D entrypoint (tiering -> type -> execution loop)
---

Use `xijia-ops-pipeline` as the single orchestration entry for this request.

## Goal

Run the requirement through a complete and consistent workflow with mandatory human-review stop gates:

1. Tiering: `green | yellow | red`
2. Change type classification: `business | technical | hybrid`
3. Route to the right pipeline branch
4. Enforce closeout (archive + sync-knowledge for red path)

## Input

The argument after `/xijia:start` can be:

- A requirement description
- An existing change name
- A request to continue current work

## Mandatory behavior

- Always follow `.cursor/rules/00-workflow.mdc`
- Always invoke and follow `xijia-ops-pipeline`
- Before tiering, run Gate-0 requirement completeness check and output `complete|partial|reject`
- If requirement info is insufficient, stop and ask user to confirm missing details; do not infer critical implementation details
- If chain is unclear, run spike-probe first and report evidence before implementation planning
- Do not skip tiering or change type classification
- For red tier, do not skip OpenSpec + analyze + Superpowers chain
- Before implementation, present plan/design and STOP for user approval (Gate-1); no non-doc code changes before approval
- Before marking acceptance done, migrating requirement status, or archiving, STOP for user acceptance sign-off (Gate-2)
- At verify stage: if core business code was touched, run `xijia-comment-enhancer` per `44-comment-sync.mdc` before Gate-2
- At verify stage: run `quality-judge`; if verdict is `revise`, do not proceed to Gate-2
- Never auto-migrate requirement status (e.g. inbox -> shipped) or auto-archive without explicit user confirmation
- Do not mark complete without closure checks defined by `xijia-ops-pipeline`

## Output format

Always return a concise status block:

```markdown
## Xijia Pipeline Status

- Completeness: <complete|partial|reject>
- Intake Score: <0-100>
- Tier: <green|yellow|red>
- Tier Rationale: <red triggers hit/miss>
- Change Type: <business|technical|hybrid>
- Stage: <explore|propose|analyze|apply|verify|sync|archive|sync-knowledge|abandon>
- Spike: <not-needed|running|done>
- Comment Sync: <done + files|skipped + reason|blocked>
- Code Review: <done|skipped + reason|blocked>
- Quality Judge: <pass|revise|pending>
- Done: <what completed>
- Next: <next command/skill>
- Blockers: <none or list>
```

