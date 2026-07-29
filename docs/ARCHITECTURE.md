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
├── memory/
└── checkpoints/           # created only when a session checkpoint is saved
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

## Operating settings and safety

Collaboration style controls participation:

- **Scribe** — guided, explanatory, proposal-first.
- **Alchemist** — collaborative; recommended default.
- **Adept** — minimal questions for reversible, in-scope actions.

Assurance controls verification:

- **Lean** — proportional checks for low-risk reversible work.
- **Standard** — validate important assumptions and outcomes.
- **Guardian** — authoritative evidence, adversarial review, and auditability.

Risk gates control authority and remain independent of both axes. Sensitive
work elevates effective assurance to Guardian. External publication, spending,
deletion, credentials, personal data, legal commitments, and production
changes still require their exact approval gate.

Schema-v1 projects remain valid. The migration mapping is:

- Scribe, Alchemist, or Adept → the same collaboration style + Standard;
- Guardian → Alchemist + Guardian.
