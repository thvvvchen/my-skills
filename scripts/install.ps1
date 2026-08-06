[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [ValidateSet('all', 'claude', 'codex', 'cursor', 'kimi', 'trae')]
    [string]$Agent = 'all',

    [ValidateSet('auto', 'junction', 'copy')]
    [string]$Mode = 'auto',

    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$skillsRoot = Join-Path $repoRoot 'plugins\my-skills-czf\skills'
$skills = @(
    Get-ChildItem -LiteralPath $skillsRoot -Directory |
        Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'SKILL.md') }
)

if ($skills.Count -eq 0) {
    Write-Host 'No skills found. Create one with scripts/new_skill.py first.'
    exit 0
}

$targets = @()
if ($Agent -in @('all', 'claude')) {
    $targets += [PSCustomObject]@{
        Key = 'claude'; Name = 'Claude Code'; Path = Join-Path $env:USERPROFILE '.claude\skills'; DefaultMode = 'junction'
    }
}
if ($Agent -in @('all', 'codex')) {
    $targets += [PSCustomObject]@{
        Key = 'codex'; Name = 'Codex'; Path = Join-Path $env:USERPROFILE '.codex\skills'; DefaultMode = 'junction'
    }
}
if ($Agent -in @('all', 'cursor')) {
    $targets += [PSCustomObject]@{
        Key = 'cursor'; Name = 'Cursor'; Path = Join-Path $env:USERPROFILE '.cursor\skills'; DefaultMode = 'copy'
    }
}
if ($Agent -in @('all', 'kimi')) {
    $targets += [PSCustomObject]@{
        Key = 'kimi'; Name = 'Kimi Code CLI'; Path = Join-Path $env:USERPROFILE '.kimi\skills'; DefaultMode = 'junction'
    }
}
if ($Agent -in @('all', 'trae')) {
    $targets += [PSCustomObject]@{
        Key = 'trae'; Name = 'Trae'; Path = Join-Path $env:USERPROFILE '.trae\skills'; DefaultMode = 'junction'
    }
}

foreach ($target in $targets) {
    New-Item -ItemType Directory -Path $target.Path -Force | Out-Null
    foreach ($skill in $skills) {
        $effectiveMode = if ($Mode -eq 'auto') { $target.DefaultMode } else { $Mode }
        if ($target.Key -eq 'cursor' -and $effectiveMode -eq 'junction') {
            Write-Warning 'Cursor does not reliably discover linked skills; using copy mode.'
            $effectiveMode = 'copy'
        }
        $destination = Join-Path $target.Path $skill.Name
        if (Test-Path -LiteralPath $destination) {
            if (-not $Force) {
                throw "Destination exists: $destination. Re-run with -Force to replace it."
            }
            if ($PSCmdlet.ShouldProcess($destination, 'Remove existing skill')) {
                Remove-Item -LiteralPath $destination -Recurse -Force
            }
        }

        if ($PSCmdlet.ShouldProcess($destination, "Install $($skill.Name) for $($target.Name)")) {
            if ($effectiveMode -eq 'junction') {
                New-Item -ItemType Junction -Path $destination -Target $skill.FullName | Out-Null
            }
            else {
                Copy-Item -LiteralPath $skill.FullName -Destination $destination -Recurse
            }
            Write-Host "Installed $($skill.Name) -> $destination ($effectiveMode)"
        }
    }
}
