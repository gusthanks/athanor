# Runtime Compatibility

## Support matrix

| Capability | Codex | Claude Code | Google Antigravity | Generic file-capable agent |
| --- | --- | --- | --- | --- |
| `SKILL.md` discovery | native | native | native | manual or host-dependent |
| Supporting references and assets | native | native | native | usually manual |
| Bundled Python scripts | native with shell | native with shell | native with shell | tool-dependent |
| Automatic semantic activation | yes | yes | yes | host-dependent |
| Direct invocation | `$skill` | `/skill` | mention by name | prompt-dependent |
| Athanor installer | plugin | global links | global links | not guaranteed |

## Portable core

The portable unit is each directory under:

```text
plugins/athanor/skills/
```

Every module contains a standard `SKILL.md` plus optional `references/`,
`assets/`, and `scripts/`. Machine-facing files avoid runtime-specific
frontmatter. Codex-only UI metadata lives in `agents/openai.yaml` and can be
ignored by other hosts.

## Runtime-specific layer

- Codex uses `.codex-plugin/plugin.json` and the repository marketplace.
- Claude Code discovers global skills under `~/.claude/skills/`.
- Antigravity discovers global skills under `~/.gemini/config/skills/`.

The installers adapt discovery only. They do not rewrite Athanor's workflow,
copy project knowledge between brands, or grant tools and permissions a runtime
does not already possess.

## Generic AI limitation

An AI that can only receive chat messages can read an uploaded `SKILL.md`, but
it cannot automatically discover sibling modules, execute scripts, persist
project files, or enforce approval gates without a suitable agent host.

Therefore Athanor's methodology is broadly readable, while full operational
compatibility requires filesystem access, tool execution, and Agent Skills
discovery.
