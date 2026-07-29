---
name: athanor-organize
description: Design and safely apply a project folder taxonomy or file-naming convention using inventory, confidence, human review, dry-run manifests, collision checks, and an append-only ledger. Use when files are scattered, duplicated, ambiguously named, stored in a flat folder, or at risk from a previous automated reorganization.
---

# Athanor Organize

Use **Solve et Coagula**. Separate AI judgment from deterministic execution.

## Hard gate

Do not move, rename, delete, overwrite, or bulk-copy files while discovering
the taxonomy. An organization request authorizes planning first, not immediate
mutation.

Read `references/organization-protocol.md`.

## Solve

1. Run `$athanor-audit` or its scanner.
2. Identify project boundaries, nested repositories, generated directories,
   secrets, temporary files, and binary dependency risks.
3. Classify by object and purpose before file format.
4. Detect related source/export families.
5. Use metadata and text before vision. Inspect previews only for ambiguous
   assets.
6. Leave ambiguous files in place and add them to the review queue.

## Plan

Create a CSV manifest using the columns defined in the reference. Include every
proposed move or rename, reason, confidence, risk, and approval state.

Show:

- current tree;
- proposed tree;
- naming convention;
- collisions;
- likely broken references;
- items requiring human review;
- rollback and backup requirements.

## Coagula

Validate or simulate a plan:

```bash
python scripts/apply_plan.py <project-root> <plan.csv>
```

Apply only after explicit approval and a verified backup:

```bash
python scripts/apply_plan.py <project-root> <plan.csv> --apply --ack-backup
```

For editable binary formats or rows marked `risk=high`, require a separate
human review and add `--allow-high-risk`.

The script processes only rows with `approved=true`, refuses destinations
outside the root, refuses overwrite, writes an append-only ledger, and never
deletes.

## Seal

After application, verify file counts, hashes, referenced paths, project tests,
and the ledger. Report anything not mechanically verifiable.
