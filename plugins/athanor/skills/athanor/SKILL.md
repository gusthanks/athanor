---
name: athanor
description: Diagnose, structure, preserve, operate, or evolve a project as a governed workspace. Use when a user starts a project from zero, asks what is missing, wants a project operating system, needs help choosing an Athanor workflow, or has a mixed request involving organization, Git, memory, agents, integrations, governance, or ongoing maintenance.
---

# Athanor

Transform the current project without assuming that one structure, tool, or
agent roster fits every workspace.

## Start safely

1. Locate and read the nearest applicable `AGENTS.md`, `CLAUDE.md`, or other
   project instructions before inspecting or changing files.
2. Identify the workspace boundary. Treat nested repositories, vaults, media
   libraries, and parent portfolios as distinct objects until evidence links
   them.
3. Start read-only. Inventory existing sources before asking the user to repeat
   information or proposing new files.
4. Mark uncertain claims as `unknown` or `unverified`. Do not turn a missing
   filename into a missing business capability.
5. Use `YYYY-MM-DD` everywhere.
6. Respond in the user's language unless the project has a documented language
   requirement. Keep filenames and structured status values stable and clear.

## Select interaction mode

Use the user's saved mode when one exists. Otherwise use **Alchemist**.

- **Scribe:** explain, propose, and ask before any write.
- **Alchemist:** recommend and collaborate on structural choices.
- **Adept:** minimize questions and perform reversible, in-scope work.
- **Guardian:** add evidence, adversarial review, and auditability.

Interaction mode never disables approval gates. Read
`references/system-map.md` for the full safety and routing model.

## Route the request

- Bootstrap project context and sources of truth → `$athanor-init`
- Assess maturity, gaps, contradictions, or readiness → `$athanor-audit`
- Organize or rename files safely → `$athanor-organize`
- Introduce Git, GitHub, backup, or repository hygiene → `$athanor-chronicle`
- Design agents, responsibilities, authority, or handoffs → `$athanor-team`
- Choose or configure APIs, MCP, connectors, or automation → `$athanor-integrate`
- Repair memory, stale paths, duplicate truth, or ongoing drift → `$athanor-maintain`
- Explain Athanor or recommend the next step → `$athanor-help`

When a request spans modules, sequence them by dependency. Audit before
organization, understand responsibilities before designing agents, and define
the desired outcome before choosing an integration.

## Keep these gates invariant

Require explicit human approval before:

- publication, external messaging, or public repository creation;
- spending, payment, subscription, or paid API activation;
- deletion, overwrite, irreversible migration, or broad filesystem moves;
- credential creation, permission expansion, or secret handling;
- legal commitment, signature, regulated advice, or production mutation;
- processing or exporting sensitive personal data.

Use drafts, dry-runs, local plans, and read-only checks to make progress before
the gate.

## Deliver a useful first response

Return:

1. the workspace type and boundary;
2. verified sources already found;
3. important unknowns or contradictions;
4. the recommended Athanor module;
5. one safe next action;
6. any human decision that genuinely blocks progress.

Do not overwhelm a new user with the entire system. Reveal concepts when they
become relevant.
