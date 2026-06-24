---
name: /xijia-init
id: xijia-init
category: Workflow
description: Xijia project bootstrap entrypoint for empty repository
---

Use `xijia-project-init` as the single initialization skill for this request.

## Goal

Initialize project documentation and structure for a new/empty repository:

1. Guard against overwriting existing initialized repositories
2. Collect minimal project bootstrap information
3. Generate skeleton docs and workflow files
4. Ask user to confirm technology stack
5. Install top-rated skills matching the confirmed stack

## Input

The argument after `/xijia:init` can be:

- A project bootstrap description
- A request to initialize docs and process structure from scratch

## Mandatory behavior

- Stop by default if `docs/` or `AGENTS.md` already exists
- Do not set technology stack without user confirmation
- Install 2-3 top-rated skills per confirmed stack
- Run `self-check` before marking `done`
- Report created files, installed skills, and self-check result

## Output format

Always return a concise status block:

```markdown
## Xijia Init Status

- Stage: <guard|interview|manifest-confirm|scaffold|skills-bootstrap|self-check|done>
- Created: <files/directories>
- Stack Confirmed: <yes/no + summary>
- Skills Installed: <list>
- SelfCheck:
  - requiredFiles: <pass/fail + details>
  - frontmatterValidity: <pass/fail + details>
  - entrypointAvailability: <pass/fail + details>
  - driftScan: <pass/fail + details>
- Next: <next suggested action>
- Blockers: <none or list>
```
