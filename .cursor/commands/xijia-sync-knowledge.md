---
name: /xijia-sync-knowledge
id: xijia-sync-knowledge
category: Workflow
description: Promote confirmed knowledge from change drafts to docs/domain after archive
---

Run post-archive knowledge promotion using the project standard.

## Goal

After a change is archived, promote valid domain knowledge from:

- `docs/openspec/changes/<name>/domain/*` (in-flight change drafts)
- to `docs/domain/*`

and capture durable ADR-level decisions.

## Mandatory behavior

1. Confirm target change name.
2. Verify the change is archived; if not archived, stop and explain why.
3. Invoke and follow `sync-knowledge`.
4. Produce a promotion report:
   - Promoted entries
   - Dropped/rolled-back entries
   - ADR updates
5. Ensure no accidental write to `docs/domain/*` from unarchived work.

## Output format

```markdown
## Xijia Knowledge Sync Result

- Change: <name>
- Archived: <yes/no>
- Promoted to docs/domain:
  - <item 1>
  - <item 2>
- Removed Change Drafts:
  - <item A>
- ADR Updates:
  - <adr file or none>
- Next: <optional follow-up>
```

## Guardrails

- If evidence is insufficient, keep content in the change draft folder and report uncertainty.
- Prefer incremental updates; avoid rewriting whole files unless necessary.
