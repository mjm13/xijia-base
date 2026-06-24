---
name: /xijia-sync-knowledge
id: xijia-sync-knowledge
category: Workflow
description: Promote confirmed knowledge from developing to established after archive
---

Run post-archive knowledge promotion using the project standard.

## Goal

After a change is archived, promote valid domain knowledge from:

- `docs/domain/developing/*`
- to `docs/domain/established/*`

and capture durable ADR-level decisions.

## Mandatory behavior

1. Confirm target change name.
2. Verify the change is archived; if not archived, stop and explain why.
3. Invoke and follow `sync-knowledge`.
4. Produce a promotion report:
   - Promoted entries
   - Dropped/rolled-back entries
   - ADR updates
5. Ensure no accidental write to `established/*` from unarchived work.

## Output format

```markdown
## Xijia Knowledge Sync Result

- Change: <name>
- Archived: <yes/no>
- Promoted to Established:
  - <item 1>
  - <item 2>
- Removed from Developing:
  - <item A>
- ADR Updates:
  - <adr file or none>
- Next: <optional follow-up>
```

## Guardrails

- If evidence is insufficient, keep content in `developing/*` and report uncertainty.
- Prefer incremental updates; avoid rewriting whole files unless necessary.
