---
name: /xijia-stop
id: xijia-stop
category: Workflow
description: Stop current change with symmetric closeout (dropped path)
---

Terminate the current change using the standard dropped path.

## Goal

Provide a safe, auditable stop flow instead of leaving half-done artifacts.

## Mandatory behavior

1. Confirm which change is being stopped.
2. Confirm stop reason (required).
3. Invoke and follow `abandon-change`.
4. Ensure the dropped path is complete:
   - Do not run `/opsx:sync`
   - Discard the change's domain drafts (in `docs/openspec/changes/<name>/domain/`); `docs/domain` is untouched
   - Mark requirement status as `dropped`
5. Summarize what was discarded vs retained.

## Output format

```markdown
## Xijia Stop Result

- Change: <name>
- Reason: <text>
- Action: abandoned
- Synced Specs: no
- Domain Draft Cleanup: <done/pending + notes>
- Requirement Status: dropped
- Next: <optional follow-up>
```

## Guardrails

- Do not silently delete uncertain data; ask when scope is unclear.
- If change has already been archived/released, stop and ask for explicit offboarding plan.
