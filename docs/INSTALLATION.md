# Installation

## Requirements

- Python 3.10 or newer;
- a supported runtime: Codex, Claude Code, or Google Antigravity;
- Git only for cloning, updating, or Chronicle workflows.

The repository remains the canonical source. Linked installations point at the
current checkout; start a new agent session after it changes.

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

Run the richer read-only doctor:

```powershell
.\install.ps1 -Target all -Action doctor
```

Include a project-OS validation:

```powershell
.\install.ps1 -Target all -Action doctor -ProjectRoot Q:\path\to\project
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

Doctor:

```bash
./install.sh all doctor
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

Refresh runtimes from the current checkout:

```powershell
.\install.ps1 -Target all -Action refresh -DryRun
.\install.ps1 -Target all -Action refresh
```

Linked skills remain in place and their registry is refreshed. Copied skills
are staged, fingerprint-checked, backed up, and replaced. Athanor refuses to
overwrite a copied skill changed after installation. Codex reinstalls its
cached plugin. Start new sessions afterward.

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

An Athanor update has two separate stages:

1. update the canonical Git checkout;
2. refresh each runtime from that checkout.

Fetch current remote metadata and inspect the Doctor report:

```powershell
.\install.ps1 -Target all -Action doctor -CheckUpdates
```

The report shows the branch, dirty state, upstream, ahead/behind counts and
candidate version. Athanor does not run a destructive reset or silently replace
the source. If the checkout is clean, not diverged, and only behind, review the
changelog and update by fast-forward:

```powershell
git pull --ff-only
.\install.ps1 -Target all -Action refresh -DryRun
.\install.ps1 -Target all -Action refresh
```

If the checkout is dirty or diverged, preserve the work and resolve it
deliberately before updating. Never use an update command that discards local
changes. The refresh step preserves copied-skill backups and refuses
unregistered collisions.

The installation registry records source version, commit, plugin-manifest hash,
and per-skill fingerprints. Registries created by Athanor 0.2 remain readable;
refreshing a legacy copied installation requires review because it lacks
content fingerprints.

## No mandatory MCP

Athanor ships without mandatory MCP servers or provider credentials.
`athanor-integrate` discovers the desired outcome first and then guides any
necessary connector, API, OAuth, MCP, or automation setup.
