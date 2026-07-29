---
name: athanor-init
description: Bootstrap a durable project operating system in a new or existing workspace. Use when starting from zero, adding AGENTS.md and project governance, establishing sources of truth, creating decision/task/tool/integration registries, or adopting Athanor without overwriting existing project instructions.
---

# Athanor Init

Create the minimum useful operating system for the project.

## Before writing

1. Establish the target root, then read only instructions applicable to that
   root. Do not inherit unrelated instructions from the launcher directory.
2. Run or reuse an `$athanor-audit` inventory.
3. Identify existing equivalents of project identity, decisions, tasks, tools,
   integrations, risks, agent roster, and memory.
4. Ask only for identity, authority, or strategic choices that cannot be
   discovered safely.
5. Read `references/bootstrap.md`.

## Scaffold safely

Resolve `<skill-directory>` as the directory containing this `SKILL.md`.

Preview:

```bash
python <skill-directory>/scripts/scaffold_project.py <project-root> --name "<project name>"
```

Apply only after reviewing the preview:

```bash
python <skill-directory>/scripts/scaffold_project.py <project-root> --name "<project name>" --apply
```

The script creates missing files only. It does not overwrite `AGENTS.md`,
`CLAUDE.md`, or an existing `athanor/` file. If an entrypoint exists, produce a
merge note instead of replacing it.

## Populate with evidence

After scaffolding:

- put stable identity and source hierarchy in `athanor/PROJECT.md`;
- put project-specific non-negotiable invariants in `PROJECT.md`;
- put human decisions with date and provenance in `DECISIONS.md`;
- put open work, dependencies, and the current handoff in `TASKS.md`;
- put verified capabilities and last-check dates in `TOOLS.md`;
- put external connections and authorization state in `INTEGRATIONS.md`;
- put ownership and handoffs in `ROSTER.md`;
- put risks, mitigations, and owners in `RISKS.md`.

Do not fill templates with invented facts. Use `[UNKNOWN]` and a precise
question when evidence is missing.

## Stop condition

Finish when a new agent can identify the project, locate authoritative sources,
find ready and blocked work, understand approval gates, and know which unknowns
remain.
