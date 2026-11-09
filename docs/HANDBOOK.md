# Athanor Handbook

**English** | [Português (Brasil)](HANDBOOK.pt-BR.md)

## Contents

1. [What it is](#what-it-is)
2. [Installation](#installation)
3. [Getting started](#getting-started)
4. [Collaboration and assurance](#collaboration-and-assurance)
5. [The phases of work](#the-phases-of-work)
6. [What Athanor diagnoses](#what-athanor-diagnoses)
7. [Safe organization](#safe-organization)
8. [Git, GitHub, and preservation](#git-github-and-preservation)
9. [Agents and memory](#agents-and-memory)
10. [Integrations](#integrations)
11. [Approvals and safety](#approvals-and-safety)
12. [Dates](#dates)
13. [Help](#help)
14. [Health, updates, and continuity](#health-updates-and-continuity)

## What it is

Athanor is a guidance and governance system for projects. It helps a person
and their AI agents answer:

- what this project is;
- where each source of truth lives;
- what already exists and what is still missing;
- who decides and who executes;
- which agents are actually needed;
- which tools and integrations are worth it;
- what should be versioned, stored, or protected;
- how to organize without losing files or context;
- how to keep the system correct over time.

It works from zero, but it can also audit a mature project. It does not assume
software, a company, a brand, a language, or an AI vendor.

## Installation

The package is a Codex and Claude Code plugin made of portable skills in the
`SKILL.md` format. In Claude Code, install it with
`/plugin marketplace add gusthanks/athanor` and
`/plugin install athanor@athanor-community`. Full instructions for every
runtime are in [`INSTALLATION.md`](INSTALLATION.md). No API or MCP connection is
required to install the core.

## Getting started

Invoke `$athanor` (Codex) or `/athanor:athanor` (Claude Code plugin) in the
directory you want to understand. The first pass is read-only. The system
identifies the kind of workspace, looks for existing instructions, and avoids
asking anything it can discover safely.

The first result should contain:

1. a summary of the current state;
2. verified facts and their sources;
3. gaps, without inference;
4. immediate risks;
5. a recommended next ritual;
6. actions that need a human decision.

## Collaboration and assurance

These are two independent controls.

### Collaboration style

#### Scribe

Explains concepts, shows options, and does not change the project without
confirmation.

#### Alchemist

Researches, recommends, and discusses structural choices with you. This is the
default.

#### Adept

Uses its best available judgment, asks few questions, and carries out local,
reversible changes. It does not skip risk gates.

### Assurance level

#### Lean

Keeps checks proportional for local, reversible, low-risk work.

#### Standard

Validates important assumptions and results. This is the default.

#### Guardian

Adds evidence, adversarial review, and an audit trail. It turns on
automatically for sensitive matters, whatever collaboration style is saved.

## The phases of work

- **Nigredo — diagnosis:** make the real state visible.
- **Albedo — structure:** separate sources of truth and reduce contradictions.
- **Citrinitas — intelligence:** define agents, handoffs, and capabilities.
- **Rubedo — operation:** execute, integrate, preserve, and maintain.

The names are an experience layer. Files and reports use plain names so they
stay readable by any person or AI.

## What Athanor diagnoses

Each domain gets a state:

- `unknown`
- `absent`
- `fragmented`
- `documented`
- `canonical`
- `operational`

A missing file does not prove a missing capability. A brand book may sit
inside a PDF that has not been inspected yet. Athanor records `unknown` or
`unverified` before it declares a gap.

Domains include identity, governance, brand, product or service, audience,
design system, operations, marketing, sales, support, legal and privacy,
finance, technology, data, documentation, preservation, tools, and
integrations.

Not every domain needs to reach the top level. Recommendations are
proportional to the project's stage, risk, and goal.

## Safe organization

The `Solve et Coagula` flow never starts by moving files:

1. inventory without reading secrets;
2. understand objects and dependencies;
3. propose a taxonomy;
4. generate a move manifest;
5. review ambiguities;
6. get approval;
7. execute with a deterministic script;
8. verify and record.

Vision, OCR, and text extraction are used progressively. Ambiguous files stay
where they are and go into `ORGANIZATION-REVIEW.md`.

The plan applier:

- simulates by default;
- refuses to overwrite;
- rejects paths outside the root;
- requires approval row by row;
- requires a backup confirmation;
- records hash, source, and destination;
- never deletes.

## Git, GitHub, and preservation

Git records history. GitHub hosts and enables collaboration. Git LFS references
large binaries. Backups make recovery possible. Asset storage holds
collections. Secret managers protect credentials.

Chronicle classifies files into:

- regular Git;
- Git LFS;
- asset storage;
- backup;
- ignored local files;
- secret manager;
- human review.

A private repository does not make a token, a personal document, or a database
safe to commit.

## Agents and memory

Agents are created by responsibility and risk, not from a fixed list of
departments. Each agent declares:

- role and triggers;
- sources, in order;
- verified tools;
- guidelines;
- guardrails;
- SOPs;
- delivery format;
- handoffs;
- human decisions;
- gaps.

Private memory is the weakest source. Shared facts move up to the canonical
source; decisions go into `DECISIONS.md`; work goes into `TASKS.md`; tool
capabilities go into `TOOLS.md`.

When significant work is done, Maintain distills what is left: a decision, a
canonical fact, tested tool behavior, an integration, a risk, future work, a
private lesson, or nothing. Routine activity does not become memory.

## Integrations

Athanor starts from the desired outcome and compares:

- an assisted manual process;
- a ready-made connector;
- no-code automation;
- a direct API;
- MCP;
- a plugin or app.

Each option includes benefit, prerequisites, cost, difficulty, authentication,
risk, testing, and a fallback. Vendor details are checked against current
official documentation at setup time.

The skill does not ship secretly connected to external accounts. When a goal
needs a missing capability, it must:

1. explain why the connection is or is not needed;
2. point out the accounts, plans, permissions, and app review required;
3. compare connector, no-code, API, and MCP options;
4. guide the setup in language that fits the user;
5. test reading before writing;
6. record only variable names and safe metadata;
7. document revocation and a manual fallback procedure.

## Approvals and safety

These require explicit human approval:

- publishing or external messages;
- spending, payments, or subscriptions;
- deleting or overwriting;
- contracts or legal commitments;
- credentials and expanded access;
- personal data or data about children;
- production changes;
- Git push or making a repository public, when not already authorized.

## Dates

Use `YYYY-MM-DD` in the interface, files, logs, and structured data.

## Help

Invoke `$athanor-help` (or `/athanor:athanor-help` in Claude Code) and say what
is confusing. The module should explain the concept at the user's level,
relate it to the current project, and suggest a single safe next action.

## Health, updates, and continuity

The Doctor aggregates the source version, Git branch and state, link or copy
integrity, installation registries, the Codex cache, and, optionally, a
Project OS validation. It does not produce a universal score.

An update has two separate stages:

1. update the canonical source after reviewing the Doctor report;
2. refresh each runtime's cache or copy.

Athanor refuses destructive automatic updates. Use fast-forward only on a
clean tree, review the changelog, and then run `refresh`. Copies get a backup;
links only renew their registry; Codex reinstalls its cache. Start a new
session afterward. Claude Code plugin installs update through
`/plugin marketplace update athanor-community` instead.

When context is interrupted, an append-only checkpoint records the goal, task
and decision IDs, verification, blockers, and next action. It points to the
current canonical sources; it does not replace Git or backups.
