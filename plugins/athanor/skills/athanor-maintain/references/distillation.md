# Distillation

Use this closing ritual after completed work, an incident, or a session that
another agent must continue.

## Filter

Preserve an item only when it is verified, likely to matter again, and has a
clear canonical owner. Never preserve secrets, raw conversation, speculative
claims, or a diary of tool calls.

## Route

| Residue | Destination | Minimum provenance |
| --- | --- | --- |
| Human choice with future consequences | `DECISIONS.md` | date, owner, context |
| Stable project fact or non-negotiable | canonical project document | source or decision |
| Tested command or tool limitation | `TOOLS.md` | verification date and environment |
| Connection or authorization state | `INTEGRATIONS.md` | account type, scope, last check |
| Risk, failure, or new safeguard | `RISKS.md` | impact, mitigation, owner |
| Follow-up or dependency | `TASKS.md` | stable ID, next action, dependency |
| Agent-specific reusable lesson | `memory/` | evidence and scope |
| Routine activity with no future value | nowhere | deliberately discard |

## Handoff

Before pausing, keep `TASKS.md` sufficient for a fresh session:

- current objective;
- last verified state;
- next safe action;
- blockers and dependencies;
- relevant files or evidence.

Do not copy the same fact into the handoff and a canonical owner. Link to the
owner instead.

## Project boundary

Project-specific learning stays in the adopting project. Promote a pattern into
the public Athanor repository only through an intentional, anonymized product
change with independent validation.
