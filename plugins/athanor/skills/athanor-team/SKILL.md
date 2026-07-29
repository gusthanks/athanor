---
name: athanor-team
description: Design a minimal, project-specific team of AI agents with clear ownership, authority, sources, tools, SOPs, review gates, and handoffs. Use when deciding which agents a project needs, creating an orchestrator or specialist roster, repairing overlapping roles, or preparing a team for Maestri or another multi-agent runtime.
---

# Athanor Team

Create agents from real responsibilities, not a generic department list.

## Preconditions

1. Identify the current project objective and work backlog.
2. Read existing ownership and decision records.
3. Audit domains with material workload, risk, or specialized evidence.
4. Confirm which runtime and tools actually exist.
5. Read `references/agent-design.md`.

## Decide whether an agent is justified

Create a specialist only when at least one is true:

- the domain has recurring work;
- errors have materially different consequences;
- the agent needs a distinct source hierarchy or tool set;
- the handoff boundary improves accountability;
- isolation reduces context or privacy risk.

Use a workflow or checklist instead of a permanent agent when the task is rare,
mechanical, or fully deterministic.

## Build the roster

Every agent must declare:

1. role and activation triggers;
2. explicit non-ownership;
3. sources in precedence order;
4. tools verified in the current environment;
5. directives and non-negotiable constraints;
6. SOPs and completion criteria;
7. delivery format;
8. inbound and outbound handoffs;
9. human-only decisions;
10. open gaps.

Use `assets/agent-role.md` as the starting template.

## Design handoffs

A handoff must contain objective, exact question, required sources, already
verified evidence, applicable gates, save destination, out-of-scope work, and
expected return.

One deliverable has one accountable owner. Reviewers may veto quality but do
not silently become the owner or gain publication authority.

## Runtime restraint

Do not claim that a role file creates a live agent. Distinguish the roster from
the runtime, model, permissions, connectors, and memory implementation.
