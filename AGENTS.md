# AGENTS.md

## Purpose

This repository contains Athanor, an open-source project operating system packaged
as a Codex plugin with multiple cooperating skills.

## Sources of truth

- Product overview: `README.md`
- Portuguese overview: `README.pt-BR.md` (keep in sync with `README.md`)
- User guide: `docs/HANDBOOK.md` (Portuguese: `docs/HANDBOOK.pt-BR.md`)
- Architecture: `docs/ARCHITECTURE.md`
- Codex plugin manifest: `plugins/athanor/.codex-plugin/plugin.json`
- Claude Code plugin manifest: `plugins/athanor/.claude-plugin/plugin.json`
  and marketplace `.claude-plugin/marketplace.json` (keep versions in sync)
- Runtime instructions: `plugins/athanor/skills/*/SKILL.md`

## Working rules

- Use `YYYY-MM-DD` in documentation, examples, interfaces, and generated records.
- Keep machine-facing names clear even when user-facing language is alchemical.
- Never include private knowledge, internal brand material, credentials, or
  identifying examples from another project in this public repository.
- Treat inspection as read-only unless a user explicitly authorizes a mutation.
- Never overwrite existing project context while bootstrapping Athanor.
- Keep organization dry-run by default, plan-first, collision-safe, and auditable.
- Never print secret values or read secret-file contents for classification.
- Prefer Python standard-library implementations for portable local utilities.
- Write code, skills, docs, and commits in English first; translations live in
  `*.pt-BR.md` files.

## Verification

Run:

```powershell
python -m unittest discover -s tests -v
python plugins/athanor/scripts/validate_all.py
```

Do not publish or push externally without explicit authorization.
