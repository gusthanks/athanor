# Athanor

**English** | [Português (Brasil)](README.pt-BR.md)

[![CI](https://github.com/gusthanks/athanor/actions/workflows/ci.yml/badge.svg)](https://github.com/gusthanks/athanor/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Agent skills for Claude Code, Codex, and Google Antigravity that audit any
project folder and give it durable context your agents actually use: a project
brief, tasks, decisions, tools, and risks, plus safe file reorganization.
Nothing moves, gets published, or connects to a service until you approve it.**

The problem: every new agent session starts cold. It re-asks what the project
is, guesses where the source of truth lives, and happily "tidies" folders it
does not understand. Athanor is for people who run real projects with AI agents
(codebases, creative archives, small-business workspaces) and want those agents
to work from verified, plain-file context instead of memory and guesswork.

## Quick start (30 seconds)

**Claude Code** (native plugin, no clone, no Python setup):

```text
/plugin marketplace add gusthanks/athanor
/plugin install athanor@athanor-community
```

Open any project, then run:

```text
/athanor:athanor diagnose this project and tell me what is missing
```

**Codex or Google Antigravity** (from a clone, Python 3.10+):

```bash
git clone https://github.com/gusthanks/athanor.git
cd athanor
./install.sh codex          # or: ./install.sh antigravity, ./install.sh all
```

Then invoke `$athanor` in Codex, or ask the Antigravity agent to use `athanor`.
On Windows, use `.\install.ps1 -Target codex`. See
[Installation](docs/INSTALLATION.md) for every runtime, dry runs, the doctor,
updates, and uninstall.

## What you get

The first pass is read-only. Athanor inventories the folder (without reading
secret files), reports verified facts, gaps, and immediate risks, and proposes
one next step. When you approve a bootstrap, it adds a small set of plain
Markdown files and never overwrites existing ones:

```text
your-project/
├── AGENTS.md                    # entry point for any agent (merged, not replaced)
├── CLAUDE.md                    # points Claude Code at the same sources
└── athanor/
    ├── PROJECT.md               # identity, sources of truth, invariants
    ├── DECISIONS.md             # human decisions with date and provenance
    ├── TASKS.md                 # open work, dependencies, current handoff
    ├── TOOLS.md                 # verified tool capabilities
    ├── INTEGRATIONS.md          # external connections and their approval state
    ├── RISKS.md
    ├── ROSTER.md                # agents, authority, and handoffs
    ├── ORGANIZATION-REVIEW.md   # files Athanor was not sure about
    └── config.json              # collaboration style and assurance level
```

Any agent or human can read these files. They do not depend on Athanor.

## Modules

One plugin, nine focused skills:

| Skill | What it does |
| --- | --- |
| `athanor` | Entry point. Routes your request to the right module. |
| `athanor-help` | Explains a concept at your level and suggests one safe next action. |
| `athanor-init` | Bootstraps the project files above without overwriting anything. |
| `athanor-audit` | Maturity and gap assessment, metadata only. |
| `athanor-organize` | Plan-first file reorganization: dry run, approval per row, backup, hash ledger, no deletes. |
| `athanor-chronicle` | Git, GitHub, LFS, backup, and preservation advice. |
| `athanor-team` | Designs agents by responsibility and risk, with explicit handoffs. |
| `athanor-integrate` | Compares manual, connector, no-code, API, and MCP options before you connect anything. |
| `athanor-maintain` | Memory distillation, drift checks, and append-only checkpoints. |

In Claude Code, plugin skills are namespaced: `/athanor:athanor-audit`,
`/athanor:athanor-organize`, and so on. Claude can also pick a module on its
own when your request matches its description.

## Core principle

Athanor does not reorganize, publish, connect services, send data, or spin up
an autonomous team blindly. It first makes the current state visible, proposes
a verifiable change, separates reversible actions from high-impact ones, and
only then executes what you authorized.

Safety is built into the architecture, not just the prompts:

- the audit never reads the content of files classified as secrets;
- organization is plan-first and dry-run by default, and the applier refuses
  overwrites, paths outside the root, and deletes;
- bootstrap never overwrites existing files;
- MCPs, APIs, and connectors are recommended only when a goal needs them, with
  prerequisites, cost, permissions, tests, and a fallback;
- publishing, spending, credentials, personal data, and external changes always
  keep a human approval step.

## Why not just a CLAUDE.md?

A hand-written `AGENTS.md` or `CLAUDE.md` is a good start, and Athanor keeps
yours. What it adds is the discipline around it: an audit before anyone writes,
separate files for decisions, tasks, and tools so they do not rot into one long
prompt, a deterministic and reversible way to move files, and checks that catch
drift later. See [Differentiation](docs/DIFFERENTIATION.md) for the full
positioning, including what Athanor is not.

## Requirements

- Claude Code, Codex, or Google Antigravity.
- Python 3.10 or newer for the deterministic helper scripts.
- Git is optional and only needed for the Chronicle module and updates.
- No MCP server, API key, or paid service is required.
- Dates and dated names use `YYYY-MM-DD`.

## Learn more

- [Handbook](docs/HANDBOOK.md): how the system works, without needing an AI to
  explain it.
- [Installation](docs/INSTALLATION.md): every runtime, link versus copy,
  updates, uninstall.
- [Anatomy](docs/ANATOMY.md): what lives beyond `SKILL.md` (references,
  templates, scripts, tests, manifests).
- [Architecture](docs/ARCHITECTURE.md), [Scenarios](docs/SCENARIOS.md),
  [Compatibility](docs/COMPATIBILITY.md).

The name comes from the alchemist's furnace that keeps a slow, steady fire.
The alchemy vocabulary (Scribe, Alchemist, Adept, Nigredo, Rubedo) is flavor
only; files and reports use plain names.

## Status

Version `0.3.0`: installation doctor, safe runtime refresh, independent
collaboration and assurance settings, checkpoints, knowledge distillation,
lightweight task dependencies, and a native Claude Code plugin. See the
[changelog](CHANGELOG.md).

## License

MIT, © 2026 Gustavo Costa (gusthx). See [LICENSE](LICENSE).
