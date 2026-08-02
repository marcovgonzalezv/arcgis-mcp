# setup.ps1
# Bootstrap installer for end users of arcgis-mcp.
#
# What it does:
#   1. Locates a usable Python interpreter (ArcGIS Pro, system, or Conda).
#   2. Creates a dedicated virtual environment at %LOCALAPPDATA%\arcgis-mcp\env.
#   3. Installs the arcgis-mcp-server wheel found next to this script (or from PyPI).
#   4. Registers the .esriAddinX in the ArcGIS Pro Add-Ins folder if present.
#   5. Prints the MCP client configuration with the correct absolute paths.
#
# Usage (place setup.ps1, the .whl and the .esriAddinX in the same folder):
#   .\setup.ps1
#
# Optional flags:
#   -WheelPath <path>    Explicit path to the .whl file.
#   -AddInPath <path>    Explicit path to the .esriAddinX file.
#   -SkipAddIn           Do not install the C# Add-In.
#   -PyPI                Install from PyPI instead of a local wheel.

[CmdletBinding()]
param(
    [string]$WheelPath,
    [string]$AddInPath,
    [switch]$SkipAddIn,
    [switch]$PyPI
)

$ErrorActionPreference = "Stop"

$ScriptDir   = Get-Item $PSScriptRoot
$InstallRoot = Join-Path $env:LOCALAPPDATA "arcgis-mcp"
$EnvDir      = Join-Path $InstallRoot "env"

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
function Write-Step($msg) { Write-Host "[arcgis-mcp] $msg" -ForegroundColor Yellow }
function Write-Ok($msg)   { Write-Host "[arcgis-mcp] $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "[arcgis-mcp] $msg" -ForegroundColor DarkYellow }

function Find-Python {
    $candidates = @()

    $arcgisPython = Join-Path $env:PROGRAMFILES "ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"
    if (Test-Path $arcgisPython) { $candidates += $arcgisPython }

    $condaExe = @(
        (Get-Command conda.exe -ErrorAction SilentlyContinue).Source,
        (Join-Path $env:PROGRAMFILES "ArcGIS\Pro\bin\Python\Scripts\conda.exe")
    ) | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1
    if ($condaExe) {
        try {
            $condaBase = (& $condaExe info --base 2>$null).Trim()
            if ($condaBase -and (Test-Path $condaBase)) {
                $condaPy = Join-Path $condaBase "python.exe"
                if (Test-Path $condaPy) { $candidates += $condaPy }
            }
        } catch { }
    }
    foreach ($p in @(
        "$env:USERPROFILE\anaconda3\python.exe",
        "$env:USERPROFILE\miniconda3\python.exe",
        "$env:USERPROFILE\miniforge3\python.exe",
        "$env:USERPROFILE\mambaforge\python.exe"
    )) {
        if (Test-Path $p) { $candidates += $p }
    }

    foreach ($pyName in @("python.exe", "py.exe")) {
        $g = Get-Command $pyName -ErrorAction SilentlyContinue
        if ($g) { $candidates += $g.Source }
    }

    foreach ($c in $candidates) {
        if (-not (Test-Path $c)) { continue }
        try {
            $ver = & $c -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
            if ($LASTEXITCODE -eq 0 -and $ver) {
                $parts = $ver.Split('.')
                if ([int]$parts[0] -ge 3 -and [int]$parts[1] -ge 10) {
                    return $c
                }
            }
        } catch { }
    }
    return $null
}

# ------------------------------------------------------------------
# Banner
# ------------------------------------------------------------------
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "  arcgis-mcp installer" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "Install root: $InstallRoot"
Write-Host ""

# ------------------------------------------------------------------
# Step 1: Locate Python
# ------------------------------------------------------------------
Write-Step "Locating Python 3.10+..."
$python = Find-Python
if (-not $python) {
    Write-Host ""
    Write-Host "ERROR: No suitable Python 3.10+ was found." -ForegroundColor Red
    Write-Host "Install Python 3.10+ from https://www.python.org/ and rerun this script," -ForegroundColor Red
    Write-Host "or use the ArcGIS Pro conda Python at:" -ForegroundColor Red
    Write-Host "  %PROGRAMFILES%\ArcGIS\Pro\bin\Python\Scripts\proswap.bat" -ForegroundColor Red
    exit 1
}
Write-Ok "Found Python: $python"

# ------------------------------------------------------------------
# Step 2: Create the virtual environment
# ------------------------------------------------------------------
Write-Step "Creating virtual environment at $EnvDir..."
if (Test-Path $EnvDir) {
    Write-Warn "Existing environment found; recreating to keep it clean."
    Remove-Item -Recurse -Force $EnvDir
}
& $python -m venv $EnvDir
if ($LASTEXITCODE -ne 0) { throw "Failed to create virtual environment." }

$EnvPython = Join-Path $EnvDir "Scripts\python.exe"
Write-Ok "Virtual environment created."

Write-Step "Upgrading pip..."
& $EnvPython -m pip install --upgrade pip --quiet
Write-Ok "pip ready."

# ------------------------------------------------------------------
# Step 3: Install the wheel (or from PyPI)
# ------------------------------------------------------------------
if ($PyPI) {
    Write-Step "Installing arcgis-mcp-server from PyPI..."
    & $EnvPython -m pip install arcgis-mcp-server
    if ($LASTEXITCODE -ne 0) { throw "PyPI install failed." }
}
else {
    if (-not $WheelPath) {
        $WheelPath = (Get-ChildItem -Path $ScriptDir.FullName -Filter "arcgis_mcp_server-*.whl" |
            Sort-Object Name -Descending | Select-Object -First 1).FullName
    }
    if (-not $WheelPath -or -not (Test-Path $WheelPath)) {
        Write-Host ""
        Write-Host "ERROR: No wheel file found." -ForegroundColor Red
        Write-Host "Place arcgis_mcp_server-<version>-py3-none-any.whl next to setup.ps1," -ForegroundColor Red
        Write-Host "pass -WheelPath <path>, or use -PyPI to install from the public index." -ForegroundColor Red
        exit 1
    }
    Write-Step "Installing wheel: $WheelPath"
    & $EnvPython -m pip install $WheelPath
    if ($LASTEXITCODE -ne 0) { throw "Wheel install failed." }
}
Write-Ok "arcgis-mcp-server installed."

$ServerExe = Join-Path $EnvDir "Scripts\arcgis-mcp-server.exe"
if (-not (Test-Path $ServerExe)) {
    throw "Expected entry point not found: $ServerExe"
}

# ------------------------------------------------------------------
# Step 4: Register the ArcGIS Pro Add-In
# ------------------------------------------------------------------
if (-not $SkipAddIn) {
    if (-not $AddInPath) {
        $AddInPath = (Get-ChildItem -Path $ScriptDir.FullName -Filter "ArcGisMcpAddin.esriAddinX" |
            Select-Object -First 1).FullName
    }

    if ($AddInPath -and (Test-Path $AddInPath)) {
        $addinsFolder = Join-Path ([Environment]::GetFolderPath("MyDocuments")) "ArcGIS\AddIns\ArcGISPro"
        $targetPkg = Join-Path $addinsFolder "ArcGisMcpAddin.esriAddinX"
        Write-Step "Installing Add-In: $AddInPath"
        New-Item -ItemType Directory -Path $addinsFolder -Force | Out-Null
        Copy-Item -LiteralPath $AddInPath -Destination $targetPkg -Force
        Write-Ok "Add-In copied to: $targetPkg"
        Write-Warn "Close and reopen ArcGIS Pro to load the Add-In."
    }
    else {
        Write-Warn "No .esriAddinX found next to setup.ps1; skipping Add-In install."
        Write-Warn "Install it separately or rerun with -AddInPath <path>."
    }
}
else {
    Write-Warn "Add-In install skipped (-SkipAddIn)."
}

# ------------------------------------------------------------------
# Step 5: Print the MCP client configuration
# ------------------------------------------------------------------
Write-Host ""
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "  Installation complete" -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Add this block to your MCP client configuration:" -ForegroundColor White
Write-Host ""
$config = @{
    mcpServers = @{
        "arcgis-mcp" = @{
            command = $ServerExe
        }
    }
} | ConvertTo-Json -Depth 5
Write-Host $config -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Open ArcGIS Pro 3.7 and load a project with a map." -ForegroundColor Gray
Write-Host "  2. Confirm the 'ArcGIS MCP' tab is visible on the ribbon." -ForegroundColor Gray
Write-Host "  3. Restart your MCP client so it picks up the configuration." -ForegroundColor Gray
Write-Host "  4. Use 'Show MCP Status' in ArcGIS Pro to verify the bridge." -ForegroundColor Gray
Write-Host ""
