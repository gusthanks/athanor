# Architecture

## One product, focused skills

Athanor is distributed as one plugin. Its skills remain separate so an agent
loads only the workflow relevant to the current task.

```text
athanor
├── route and explain
├── init
├── audit
├── organize
├── chronicle
├── team
├── integrate
└── maintain
```

## Five distinct layers

1. **Method** — reusable skills and references.
2. **Project operating system** — files generated inside each project.
3. **State** — decisions, tasks, integrations, risks, and memory that evolve.
4. **Runtime** — Codex, Claude, Maestri, or another compatible agent host.
5. **Capabilities** — filesystem tools, APIs, MCP servers, connectors, and
   automations available in the current environment.

Do not confuse these layers. A skill can guide MCP setup but does not create
authorization. An agent role can own a workflow but does not gain permission to
spend, publish, delete, or sign.

## Project-side layout

The default bootstrap creates:

```text
AGENTS.md
CLAUDE.md
athanor/
├── PROJECT.md
├── DECISIONS.md
├── TASKS.md
├── TOOLS.md
├── INTEGRATIONS.md
├── ROSTER.md
├── RISKS.md
├── ORGANIZATION-REVIEW.md
├── config.json
├── agents/
└── memory/
```

Existing files are never overwritten by default. In an established project,
the bootstrap creates only missing artifacts and emits a merge plan for any
entrypoint that already exists.

## Authority hierarchy

1. Current live evidence and authoritative external sources.
2. Canonical project documents and current code or assets.
3. Recorded human decisions.
4. Project operating-system summaries.
5. Agent specifications.
6. Agent-private memory.
7. Model recollection or inference.

Lower layers must not override higher layers.

## Safety model

Interaction mode controls how much the user participates. Risk gates control
what requires approval. These are independent.

- **Scribe** — guided, explanatory, proposal-only.
- **Alchemist** — collaborative; recommended default.
- **Adept** — minimal questions for reversible, in-scope actions.
- **Guardian** — high-assurance review for sensitive domains.

Guardian gates apply regardless of interaction mode to external publication,
spending, deletion, credentials, personal data, legal commitments, and
production changes.
