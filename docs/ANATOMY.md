# Anatomy of an Athanor Skill

A skill is not executable magic hidden inside a model. At minimum it is a
directory containing `SKILL.md`: YAML frontmatter tells an agent when to load
it, and the Markdown body defines the workflow and constraints.

Athanor adds layers around that minimum:

| Layer | Purpose |
| --- | --- |
| `SKILL.md` | Trigger, reasoning workflow, safety gates, and output contract |
| `references/` | Detailed knowledge loaded only when the task needs it |
| `assets/` | Templates copied or adapted into a project |
| `scripts/` | Deterministic operations that should not rely on improvisation |
| `agents/openai.yaml` | User-facing name, description, and starter prompt |
| `.codex-plugin/plugin.json` | Packages all modules as one installable product |
| `.agents/plugins/marketplace.json` | Makes the plugin discoverable from this repository |
| `tests/` | Proves core non-destructive and privacy properties |

## Why multiple skills under one plugin

One enormous instruction file is easy to trigger but costly to load and hard to
review. Athanor uses a router plus focused modules. Installation remains one
step, while the agent loads only the relevant procedure.

## What is persistent

The skill itself is reusable method. Project-specific memory is generated in
the target project under `athanor/`; it is not written back into the public
skill. This separation prevents knowledge from one brand leaking into another.

## What a skill cannot grant

A skill can explain that an API, MCP, connector, account, plan, OAuth grant, or
human review is required. It cannot manufacture authorization. Credentials and
external writes remain explicit setup and approval steps.
