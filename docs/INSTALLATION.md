# Installation

## Local Codex installation

Requirements:

- Codex with plugin support;
- Python 3.10 or newer for Athanor's deterministic utilities;
- Git only if Chronicle will initialize or inspect version history.

From a local copy of this repository:

```powershell
codex plugin marketplace add Q:\path\to\athanor
codex plugin add athanor@athanor-community
```

Start a new thread so the client loads the newly installed skills. Invoke:

```text
$athanor
```

To inspect installation state:

```powershell
codex plugin list
```

## Install from a future GitHub clone

```powershell
git clone <repository-url> athanor
codex plugin marketplace add <absolute-path-to-athanor>
codex plugin add athanor@athanor-community
```

The repository URL is intentionally left as a placeholder until an official
public remote exists.

## Other compatible agents

The reusable method lives in `plugins/athanor/skills/*/SKILL.md`, with adjacent
`references/`, `assets/`, and `scripts/`. An agent host that supports the
Agent Skills convention can load those directories directly, although plugin
installation commands and interface metadata are Codex-specific.

If a host only accepts one skill directory, start with
`plugins/athanor/skills/athanor` and make the sibling module paths available to
the same workspace. Do not concatenate all instructions into one permanent
prompt; focused skills reduce noise and make safety rules testable.

## Update during local development

Validate before reinstalling:

```powershell
python plugins\athanor\scripts\validate_all.py
python C:\path\to\plugin-creator\scripts\validate_plugin.py plugins\athanor
codex plugin add athanor@athanor-community
```

Open a new thread after reinstalling. Existing threads may retain the prior
skill snapshot.

## No mandatory MCP

Athanor intentionally ships without mandatory MCP servers or provider
credentials. `$athanor-integrate` discovers the desired outcome first and then
guides any necessary connector, API, OAuth, MCP, or automation setup. This keeps
the core portable and prevents unused access from becoming a hidden dependency.
