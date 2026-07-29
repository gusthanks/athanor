# Checkpoints

Use a checkpoint when work pauses before completion, context is likely to reset,
or another agent must continue. A checkpoint is an append-only handoff, not a
backup and not a raw transcript.

Resolve `<skill-directory>` as the directory containing the active
`SKILL.md`.

## Save

```bash
python <skill-directory>/scripts/checkpoint.py <project-root> save \
  --goal "Prepare pilot launch" \
  --completed "TASK-002 evidence reviewed" \
  --task "TASK-003 remains blocked by DEC-004" \
  --verification "Project validator passed" \
  --path "athanor/TASKS.md" \
  --remaining "Resolve parental-consent policy" \
  --next-action "Ask the owner to decide DEC-004"
```

Store goal, completed work, referenced decision/task IDs, verification, relevant
paths, blockers, and one exact next action. The script adds branch and commit
when Git exists.

## Resume

```bash
python <skill-directory>/scripts/checkpoint.py <project-root> list
python <skill-directory>/scripts/checkpoint.py <project-root> restore
```

Restore is read-only. Revalidate current files, branch, decisions, and tasks
before trusting an old checkpoint.

## Invariants

- Never overwrite a checkpoint.
- Never store credentials, raw chat, or unnecessary personal data.
- Keep current truth in canonical project documents.
- Use checkpoints for handoff; use backup and Git for recovery.
