# Installation

## Requirements

- Python 3.10 or newer;
- a supported runtime: Codex, Claude Code, or Google Antigravity;
- Git only for cloning, updating, or Chronicle workflows.

The repository remains the canonical source. Linked installations update as
soon as this checkout changes.

## Windows quick start

From the repository root:

```powershell
.\install.ps1 -Target codex
.\install.ps1 -Target claude
.\install.ps1 -Target antigravity
```

Install all supported runtimes:

```powershell
.\install.ps1 -Target all
```

Preview without changing runtime configuration:

```powershell
.\install.ps1 -Target all -DryRun
```

Check status:

```powershell
.\install.ps1 -Target all -Action status
```

## macOS and Linux quick start

```bash
./install.sh codex
./install.sh claude
./install.sh antigravity
```

Or:

```bash
./install.sh all
```

## Codex

The installer performs:

```powershell
codex plugin marketplace add Q:\path\to\athanor
codex plugin add athanor@athanor-community
```

The first command registers this repository as a local plugin catalog. Codex
reads `.agents/plugins/marketplace.json` to discover the marketplace named
`athanor-community`.

The second command installs the plugin named `athanor` from that marketplace.
The `@` separates the plugin name from the marketplace name. Codex validates
and caches the bundle; it does not upload the project being inspected.

Start a new Codex conversation after installation and invoke:

```text
$athanor
```

## Claude Code

The default linked installation exposes every Athanor skill under:

```text
~/.claude/skills/
```

On Windows, directory junctions point to the canonical checkout. Start Claude
Code inside a project and invoke:

```text
/athanor
```

Claude may also activate a module automatically when its description matches
the request.

## Google Antigravity

The default linked installation exposes every Athanor skill under:

```text
~/.gemini/config/skills/
```

Open the target workspace and ask the agent to use `athanor`, or describe a
matching outcome and allow automatic activation.

## Link versus copy

`link` is the default and recommended method:

- one canonical source;
- Git updates become immediately visible;
- no duplicated skill folders;
- uninstall removes links, not source files.

Use a copy only when links are unavailable:

```powershell
.\install.ps1 -Target claude -Method copy
```

Copied installations do not update automatically. Uninstall moves copied skills
to a timestamped `.athanor-backups/` directory instead of deleting them.

## Collision and uninstall safety

The installer refuses to overwrite an existing skill directory it cannot
verify as Athanor. Inspect before resolving a collision.

Preview uninstall:

```powershell
.\install.ps1 -Target claude -Action uninstall -DryRun
```

Apply uninstall:

```powershell
.\install.ps1 -Target claude -Action uninstall -Yes
```

For Codex, uninstall removes the installed plugin but preserves the configured
marketplace:

```powershell
.\install.ps1 -Target codex -Action uninstall -Yes
```

## Clone and update

```powershell
git clone https://github.com/gusthanks/athanor.git
cd athanor
.\install.ps1 -Target all
```

Update:

```powershell
git pull
```

Claude and Antigravity linked installations see the update immediately. Codex
plugins are cached, so reinstall the updated plugin and start a new conversation:

```powershell
codex plugin add athanor@athanor-community
```

## No mandatory MCP

Athanor ships without mandatory MCP servers or provider credentials.
`athanor-integrate` discovers the desired outcome first and then guides any
necessary connector, API, OAuth, MCP, or automation setup.
