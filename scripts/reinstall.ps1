<#
.SYNOPSIS
    Remove japanese-date-converter from a virtualenv and install it again.

.DESCRIPTION
    Uninstalls every trace of the package (including the old
    `japanese_date_converter` underscore spelling and any stale .egg-link or
    .pth left behind by an editable install), then reinstalls from this
    source tree.

.PARAMETER Venv
    Path to the virtualenv. Defaults to .venv beside the package.

.PARAMETER Editable
    Install with `pip install -e .` so code edits take effect immediately.

.PARAMETER Test
    Run the test suite after installing.

.EXAMPLE
    .\scripts\reinstall.ps1
    .\scripts\reinstall.ps1 -Venv C:\projects\myapp\.venv -Editable -Test
#>
[CmdletBinding()]
param(
    [string]$Venv = "",
    [switch]$Editable,
    [switch]$Test,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$PackageRoot = Split-Path -Parent $PSScriptRoot
$DistName    = "japanese-date-converter"
$ModuleName  = "japanese_date_converter"

if (-not $Venv) { $Venv = Join-Path $PackageRoot ".venv" }

# --- locate the interpreter -------------------------------------------------
$PythonExe = Join-Path $Venv "Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    $PythonExe = Join-Path $Venv "bin/python"   # venv created under Git Bash / WSL
}
if (-not (Test-Path $PythonExe)) {
    if (-not $Force) {
        Write-Error "No virtualenv found at '$Venv'. Create one with 'python -m venv $Venv', or pass -Force to create it now."
    }
    Write-Host "Creating virtualenv at $Venv ..." -ForegroundColor Cyan
    python -m venv $Venv
    $PythonExe = Join-Path $Venv "Scripts\python.exe"
}

# Resolve to an absolute path. The verify step changes directory, and a
# relative path would stop resolving once it does -- PowerShell would then
# treat it as a command name rather than a file.
$PythonExe = (Resolve-Path $PythonExe).Path

Write-Host "Interpreter : $PythonExe" -ForegroundColor DarkGray
Write-Host "Source tree : $PackageRoot" -ForegroundColor DarkGray
Write-Host ""

# --- uninstall --------------------------------------------------------------
Write-Host "==> Removing any existing install" -ForegroundColor Cyan
foreach ($name in @($DistName, $ModuleName)) {
    # -y so it never blocks on a prompt; a package that is not installed is
    # fine here and pip still exits 0.
    #
    # Deliberately NOT piping through 2>&1: in Windows PowerShell 5.1 that wraps
    # each native stderr line in an ErrorRecord, which under
    # $ErrorActionPreference = "Stop" aborts the script on pip's harmless
    # "Skipping ... not installed" warning.
    & $PythonExe -m pip uninstall -y $name
}

# Editable installs leave a .pth or __editable__ finder behind that keeps the
# old source tree importable even after the metadata is gone. Clear those too.
$SitePackages = & $PythonExe -c "import sysconfig; print(sysconfig.get_paths()['purelib'])"
if (Test-Path $SitePackages) {
    Get-ChildItem -Path $SitePackages -Force -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match "japanese[-_]date[-_]converter|__editable__.*japanese" } |
        ForEach-Object {
            Write-Host "    removing leftover $($_.Name)" -ForegroundColor DarkYellow
            Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
        }
}

# Verify it is really gone before reinstalling.
$stillThere = & $PythonExe -c "import importlib.util,sys; sys.stdout.write('yes' if importlib.util.find_spec('$ModuleName') else 'no')"
if ($stillThere -eq "yes") {
    Write-Warning "$ModuleName is still importable. Something outside site-packages (a PYTHONPATH entry, or the current directory) is shadowing it."
}

# --- reinstall --------------------------------------------------------------
Write-Host ""
Write-Host "==> Installing from source" -ForegroundColor Cyan
Push-Location $PackageRoot
try {
    if ($Editable) {
        & $PythonExe -m pip install -e .
    } else {
        # --no-cache-dir so a rebuilt wheel with the same version number is not
        # served from pip's cache, which is the usual reason a reinstall looks
        # like it did nothing.
        & $PythonExe -m pip install --no-cache-dir --force-reinstall .
    }
    if ($LASTEXITCODE -ne 0) { throw "pip install failed with exit code $LASTEXITCODE" }
} finally {
    Pop-Location
}

# --- verify -----------------------------------------------------------------
Write-Host ""
Write-Host "==> Verifying" -ForegroundColor Cyan
# Run from a neutral directory: the source tree shadows site-packages when it
# is the working directory, which would make any install look successful.
Push-Location ([System.IO.Path]::GetTempPath())
try {
& $PythonExe -c @"
import japanese_date_converter as j
print('  version   ', j.__version__)
print('  location  ', j.__file__)
print('  2019-04-30', j.to_japanese('2019-04-30', use_full_width=False))
print('  2019-05-01', j.to_japanese('2019-05-01', use_full_width=False))
print('  R5.12.15  ', j.to_standard('R5.12.15', output_format='%Y-%m-%d'))
"@
} finally { Pop-Location }
if ($LASTEXITCODE -ne 0) { throw "Import check failed." }

if ($Test) {
    Write-Host ""
    Write-Host "==> Running tests" -ForegroundColor Cyan
    & $PythonExe -m pip install -q pytest
    Push-Location $PackageRoot
    try { & $PythonExe -m pytest -q } finally { Pop-Location }
}

Write-Host ""
Write-Host "Done." -ForegroundColor Green
