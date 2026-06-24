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
6. Keep `docs/architecture.md` and `docs/capability-map.md` as on-demand artifacts (not init pre-generated)

## Input

The argument after `/xijia:init` can be:

- A project bootstrap description
- A request to initialize docs and process structure from scratch

## Mandatory behavior

- Stop by default if `docs/` or `AGENTS.md` already exists
- Do not set technology stack without user confirmation
- Support two install strategies after stack confirmation:
  - auto install top 2-3 skills per stack
  - recommendation-only (do not install, only report candidates and scores)
- Run `self-check` before marking `done`
- Report created files, installed skills, and self-check result
- In init `requiredFiles`, do not treat on-demand files as required:
  - `docs/architecture.md`
  - `docs/capability-map.md`
- These two files should only be created/updated at requirement closeout based on real changes, not during active development

## Output format

Always return a concise status block:

```markdown
## Xijia Init Status

- Stage: <guard|interview|manifest-confirm|scaffold|skills-bootstrap|self-check|done>
- Mode: <empty-repo|supplement-only>
- Created: <files/directories>
- Skipped: <existing files kept untouched>
- Stack Confirmed: <yes/no + summary>
- Skills Selected: <name + score + source>
- Skills Installed: <success/fail list or recommendation-only>
- SelfCheck:
  - requiredFiles: <pass/fail + details>
  - frontmatterValidity: <pass/fail + details>
  - entrypointAvailability: <pass/fail + details>
  - driftScan: <pass/fail + details>
- Next: <next suggested action>
- Blockers: <none or list>
```
