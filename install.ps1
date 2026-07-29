[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("codex", "claude", "antigravity", "agents", "all")]
    [string]$Target,

    [ValidateSet("install", "status", "refresh", "doctor", "uninstall")]
    [string]$Action = "install",

    [ValidateSet("link", "copy")]
    [string]$Method = "link",

    [switch]$DryRun,
    [switch]$Yes,
    [string]$ProjectRoot,
    [switch]$CheckUpdates
)

$installer = Join-Path $PSScriptRoot "scripts\install_athanor.py"
$arguments = @(
    $installer,
    "--target", $Target,
    "--action", $Action,
    "--method", $Method,
    "--repo-root", $PSScriptRoot
)

if ($DryRun) {
    $arguments += "--dry-run"
}

if ($Yes) {
    $arguments += "--yes"
}

if ($ProjectRoot) {
    $arguments += @("--project-root", $ProjectRoot)
}

if ($CheckUpdates) {
    $arguments += "--check-updates"
}

& python @arguments
exit $LASTEXITCODE
