#!/usr/bin/env pwsh
[CmdletBinding()]
param(
    [switch]$Json,
    [string]$Base,
    [switch]$Help
)

$ErrorActionPreference = 'Stop'
$pyScript = Join-Path $PSScriptRoot '..\python\resolve_review_context.py'

$forwardArgs = @()
if ($Json) { $forwardArgs += '--json' }
if ($Base) { $forwardArgs += @('--base', $Base) }
if ($Help) { $forwardArgs += '--help' }

if ($env:SPECKIT_PYTHON_EXECUTABLE) {
    & $env:SPECKIT_PYTHON_EXECUTABLE $pyScript @forwardArgs
    exit $LASTEXITCODE
}

foreach ($candidate in @('python3', 'python')) {
    if (Get-Command $candidate -ErrorAction SilentlyContinue) {
        & $candidate $pyScript @forwardArgs
        exit $LASTEXITCODE
    }
}

Write-Error 'ERROR: Python 3 is required to run resolve_review_context.py.'
exit 1
