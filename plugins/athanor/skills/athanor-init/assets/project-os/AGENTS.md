# AGENTS.md — {{PROJECT_NAME}}

This file is the entry point for AI collaborators working in this repository.

## Read first

1. `athanor/PROJECT.md` — purpose, audience, stage, and boundaries
2. `athanor/DECISIONS.md` — durable decisions and their rationale
3. `athanor/TASKS.md` — active work and next actions
4. `athanor/TOOLS.md` — approved tools and local commands
5. `athanor/INTEGRATIONS.md` — APIs, MCPs, connectors, and automation status
6. `athanor/ROSTER.md` — human and agent roles
7. `athanor/RISKS.md` — known risks and safeguards

## Operating settings

- Collaboration style: `{{COLLABORATION_STYLE}}`
- Assurance level: `{{ASSURANCE_LEVEL}}`

Collaboration controls participation:

- `scribe`: explain and ask before writing.
- `alchemist`: recommend a best path and discuss meaningful choices.
- `adept`: act autonomously inside documented boundaries.

Assurance controls verification:

- `lean`: keep checks proportional for low-risk reversible work.
- `standard`: validate important assumptions and outcomes.
- `guardian`: require stronger evidence, review, and auditability.

Sensitive work temporarily escalates to Guardian assurance. No setting weakens
the approval gates below.

## Invariants

- Use `YYYY-MM-DD` for dates.
- Inspect before proposing changes.
- Plan before moving, renaming, deleting, publishing, or sending.
- Never expose secrets or personal data in logs, prompts, commits, or reports.
- Do not overwrite existing files unless the user explicitly approves the exact
  scope.
- Keep decisions, tasks, integrations, and risks current when work changes them.
- Stop and ask when authority, ownership, or the intended result is genuinely
  ambiguous.

## Project-specific rules

Add only rules that are stable and specific to this project.

- Read the `Project invariants` section in `athanor/PROJECT.md`.
