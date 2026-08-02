# build_release.ps1
# Builds the distributable artifacts for an arcgis-mcp release:
#   1. ArcGisMcpAddin.esriAddinX  (ArcGIS Pro Add-In, requires ArcGIS Pro SDK)
#   2. arcgis_mcp_server wheel    (pip-installable Python server)
#   3. SHA256 checksums
#
# Output: <repo-root>\dist\
#
# Usage (from repository root):
#   .\packaging\build_release.ps1 [-Configuration Release]

[CmdletBinding()]
param(
    [ValidateSet("Debug", "Release")]
    [string]$Configuration = "Release"
)

$ErrorActionPreference = "Stop"

$RepoRoot    = Get-Item (Join-Path $PSScriptRoot "..")
$AddinDir    = Join-Path $RepoRoot.FullName "arcgis-addin"
$Solution    = Join-Path $AddinDir "ArcGisMcpAddin.sln"
$PythonDir   = Join-Path $RepoRoot.FullName "python-server"
$DistDir     = Join-Path $RepoRoot.FullName "dist"

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "  arcgis-mcp release builder" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "Repository : $($RepoRoot.FullName)"
Write-Host "Output     : $DistDir"
Write-Host "Config     : $Configuration"
Write-Host ""

New-Item -ItemType Directory -Path $DistDir -Force | Out-Null

# ------------------------------------------------------------------
# Step 1: Compile the ArcGIS Pro Add-In and collect the .esriAddinX
# ------------------------------------------------------------------
Write-Host "[1/3] Compiling ArcGIS Pro Add-In..." -ForegroundColor Yellow
Push-Location $AddinDir
try {
    dotnet build $Solution --configuration $Configuration --nologo
    if ($LASTEXITCODE -ne 0) {
        throw "Add-In compilation failed (exit code $LASTEXITCODE)."
    }
}
finally { Pop-Location }

$BuildOut  = Join-Path $AddinDir "ArcGisMcpAddin\bin\$Configuration\win-x64"
$AddinPkg  = Join-Path $BuildOut "ArcGisMcpAddin.esriAddinX"
if (-not (Test-Path $AddinPkg)) {
    throw "Add-In package not found at $AddinPkg."
}
Copy-Item -LiteralPath $AddinPkg -Destination $DistDir -Force
Write-Host "  -> ArcGisMcpAddin.esriAddinX copied." -ForegroundColor Green

# ------------------------------------------------------------------
# Step 2: Build the Python wheel
# ------------------------------------------------------------------
Write-Host "[2/3] Building Python wheel..." -ForegroundColor Yellow
Push-Location $PythonDir
try {
    $wheelCache = Join-Path $env:TEMP "arcgis-mcp-wheel"
    New-Item -ItemType Directory -Path $wheelCache -Force | Out-Null
    python -m pip wheel . --no-deps --no-build-isolation -w $wheelCache
    if ($LASTEXITCODE -ne 0) {
        throw "Wheel build failed (exit code $LASTEXITCODE)."
    }
    Get-ChildItem -Path $wheelCache -Filter "arcgis_mcp_server-*.whl" |
        Copy-Item -Destination $DistDir -Force
    Remove-Item -Recurse -Force $wheelCache
}
finally { Pop-Location }
Write-Host "  -> wheel copied." -ForegroundColor Green

# ------------------------------------------------------------------
# Step 3: Generate SHA256 checksums
# ------------------------------------------------------------------
Write-Host "[3/3] Generating checksums..." -ForegroundColor Yellow
$checksumsPath = Join-Path $DistDir "checksums.txt"
Set-Content -Path $checksumsPath -Value "" -Encoding ascii
foreach ($file in (Get-ChildItem -Path $DistDir -File | Where-Object { $_.Name -ne "checksums.txt" })) {
    $hash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
    Add-Content -Path $checksumsPath -Value "$($hash.ToLower())  $($file.Name)" -Encoding ascii
}
Write-Host "  -> checksums.txt written." -ForegroundColor Green

# ------------------------------------------------------------------
# Summary
# ------------------------------------------------------------------
Write-Host ""
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "  Release artifacts ready in: $DistDir" -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Cyan
Get-ChildItem -Path $DistDir -File |
    ForEach-Object { Write-Host ("  {0,12:N0} bytes  {1}" -f $_.Length, $_.Name) -ForegroundColor Gray }
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Sign the .esriAddinX with signtool if you have a certificate." -ForegroundColor Gray
Write-Host "  2. Upload the contents of dist\ to a GitHub Release." -ForegroundColor Gray
Write-Host "  3. (Optional) publish the wheel to PyPI with 'twine upload'." -ForegroundColor Gray
