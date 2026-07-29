---
name: athanor-maintain
description: Maintain an Athanor project operating system by validating required files, repairing stale paths and duplicate truth, curating decisions and memory, checking tool and integration freshness, and propagating corrections. Use after project changes, migrations, agent drift, contradictory documentation, or periodic governance review.
---

# Athanor Maintain

Keep the operating system smaller and truer over time.

## Validate structure

Resolve `<skill-directory>` as the directory containing this `SKILL.md`.

Run:

```bash
python <skill-directory>/scripts/validate_project_os.py <project-root>
```

Fix structural errors before adding new documentation.

## Maintain by ownership

- Stable identity and source hierarchy → `PROJECT.md`
- Human decisions and provenance → `DECISIONS.md`
- Open work and blockers → `TASKS.md`
- Verified tool capability → `TOOLS.md`
- Connection and authorization state → `INTEGRATIONS.md`
- Ownership and handoffs → `ROSTER.md`
- Risks and mitigations → `RISKS.md`
- Agent-specific verified learning → `memory/`

Read `references/memory-and-drift.md`.

## Propagate corrections

When a fact changes:

1. identify its canonical owner;
2. update the owner with date and source;
3. search for the obsolete value across summaries, role specs, paths, and
   filenames;
4. update derived references or mark historical mentions explicitly;
5. validate again.

Do not preserve two current truths to avoid editing.

## Review freshness

Tool, integration, pricing, policy, and external capability claims require a
last-verified date. Mark stale claims as stale rather than silently trusting
them.

## Curate memory

Memory records verified reusable learning, not a diary. Promote shared facts to
canonical documents. Remove or correct contradicted memory. Never store secrets.

## Deliver

Report:

- validations passed and failed;
- stale or contradictory claims;
- corrections applied;
- human decisions still needed;
- next review date in `YYYY-MM-DD`.
