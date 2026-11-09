# Changelog

All dates use `YYYY-MM-DD`.

## 0.3.0 — 2026-11-09

- Added a native Claude Code plugin: `.claude-plugin/marketplace.json` and
  `plugins/athanor/.claude-plugin/plugin.json`. Install with
  `/plugin marketplace add gusthanks/athanor` and
  `/plugin install athanor@athanor-community`.
- Extended `validate_all.py` to check that the Codex and Claude Code manifests
  agree.
- Rewrote the README in English with a concrete pitch and a 30-second quick
  start; the Portuguese version moved to `README.pt-BR.md`.
- Translated the Handbook to English; the Portuguese original is now
  `docs/HANDBOOK.pt-BR.md`.
- Added a GitHub Actions workflow that runs the tests and the plugin validator.
- Set the copyright holder to Gustavo Costa (gusthx) in `LICENSE` and the plugin
  manifests.
- Fixed an invalid escape sequence warning in the test suite and used neutral
  example paths.
- Separated collaboration style (`scribe`, `alchemist`, `adept`) from assurance
  level (`lean`, `standard`, `guardian`) with schema-v1 compatibility.
- Added project invariants without introducing another competing source file.
- Added lightweight task dependencies and a current-session handoff.
- Added deliberate completed-work distillation and append-only checkpoints.
- Added an installation doctor with source, Git, runtime, registry, and optional
  project-OS diagnostics.
- Added safe runtime refresh with fingerprints, backups for copied skills, and
  collision or local-modification refusal.
- Added a guided, non-destructive update lifecycle based on `git pull --ff-only`
  and explicit runtime refresh.
- Expanded deterministic coverage from 12 to 33 tests.

## 0.2.0 — 2026-07-29

- Added one-command installers for Codex, Claude Code, and Google Antigravity.
- Added linked global installation so every runtime can share one canonical
  Athanor source.
- Added status, dry-run, collision refusal, rollback, and recoverable uninstall.
- Made bundled script instructions independent of the current project directory.
- Added cross-runtime compatibility documentation and installer tests.

## 0.1.0 — 2026-07-29

- Added the Athanor router and eight focused modules.
- Added four collaboration modes: Scribe, Alchemist, Adept, and Guardian.
- Added safe project-memory bootstrap templates.
- Added metadata-only audit and repository-advice utilities.
- Added dry-run organization with path, collision, approval, backup, hash, and
  ledger safeguards.
- Added agent-team, integration, memory, and drift guidance.
- Added plugin and marketplace manifests, documentation, and automated tests.
