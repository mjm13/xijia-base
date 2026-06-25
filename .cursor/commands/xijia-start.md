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
- Do not skip tiering or change type classification
- For red tier, do not skip OpenSpec + analyze + Superpowers chain
- Before implementation, present plan/design and STOP for user approval (Gate-1); no non-doc code changes before approval
- Before marking acceptance done, migrating requirement status, or archiving, STOP for user acceptance sign-off (Gate-2)
- Never auto-migrate requirement status (e.g. inbox -> shipped) or auto-archive without explicit user confirmation
- Do not mark complete without closure checks defined by `xijia-ops-pipeline`

## Output format

Always return a concise status block:

```markdown
## Xijia Pipeline Status

- Tier: <green|yellow|red>
- Change Type: <business|technical|hybrid>
- Stage: <explore|propose|analyze|apply|verify|sync|archive|sync-knowledge|abandon>
- Done: <what completed>
- Next: <next command/skill>
- Blockers: <none or list>
```

