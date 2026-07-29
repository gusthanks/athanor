---
name: athanor-audit
description: Audit a project or workspace for maturity, missing foundations, duplicate truth, stale paths, unmanaged risk, weak documentation, and operational gaps. Use when asking what a project lacks, whether it is ready, where knowledge lives, or what should be prioritized before organization, automation, growth, or agent-team design.
---

# Athanor Audit

Assess evidence, not the aesthetic neatness of the folder tree.

## Inventory

Resolve `<skill-directory>` as the directory containing this `SKILL.md`.

Run the read-only scanner:

```bash
python <skill-directory>/scripts/scan_project.py <project-root> --output <report-directory>
```

The scanner reads paths and metadata by default. It does not print secret
values or inspect `.env` content.

## Assess

Read `references/maturity-model.md`. For every relevant domain, assign:

- `unknown`
- `absent`
- `fragmented`
- `documented`
- `canonical`
- `operational`

Attach evidence paths and confidence. Do not mark a capability absent merely
because an expected filename is missing.

## Prioritize

Separate findings into:

- **Now:** blocks safety, identity, delivery, or a current goal.
- **Next:** needed before growth or delegation.
- **Later:** useful after the project proves the need.

Distinguish:

- missing artifact;
- conflicting artifact;
- stale artifact;
- undocumented but working capability;
- unnecessary maturity for the current stage.

## Deliver

Return:

1. project type and boundary;
2. strongest existing foundations;
3. top gaps with evidence;
4. contradictions and stale references;
5. now/next/later plan;
6. recommended Athanor module;
7. questions reserved for humans.

Do not mutate the project during an audit unless the user separately requests a
fix.
