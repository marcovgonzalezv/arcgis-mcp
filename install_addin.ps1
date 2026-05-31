# install_addin.ps1
# Automates the compilation and installation of the C# ArcGIS Pro Add-In

$ErrorActionPreference = "Stop"

$ProjectRoot = Get-Item $PSScriptRoot
$AddinDir = Join-Path $ProjectRoot.FullName "arcgis-addin"
$SolutionFile = Join-Path $AddinDir "ArcGisMcpAddin.sln"

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "  ArcGIS Pro MCP Bridge - Automated Installer" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan

# 1. Check for .NET SDK
Write-Host "Step 1: Verifying .NET SDK installation..." -ForegroundColor Yellow
if (!(Get-Command dotnet -ErrorAction SilentlyContinue)) {
    Write-Error "dotnet CLI was not found on your PATH. Please install the .NET SDK."
}
$dotnetVersion = dotnet --version
Write-Host "Found .NET SDK version: $dotnetVersion" -ForegroundColor Green

# 2. Compile C# solution
Write-Host "`nStep 2: Compiling ArcGIS Pro C# Add-In using MSBuild..." -ForegroundColor Yellow
Push-Location $AddinDir
try {
    dotnet build $SolutionFile --configuration Debug --nologo
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Compilation failed with exit code $LASTEXITCODE."
    }
}
finally {
    Pop-Location
}
Write-Host "Compilation completed successfully!" -ForegroundColor Green

# 3. Define target deployment path
Write-Host "`nStep 3: Deploying Add-In to ArcGIS Pro..." -ForegroundColor Yellow
$AddinGuid = "{d0b64d1f-827b-4b21-9875-cf65f5dfd2d3}"
$DocumentsFolder = [System.IO.Path]::Combine([Environment]::GetFolderPath("MyDocuments"), "ArcGIS", "AddIns", "ArcGISPro")
$TargetDir = Join-Path $DocumentsFolder $AddinGuid
$FallbackDocumentsFolder = Join-Path $env:USERPROFILE "Documents\ArcGIS\AddIns\ArcGISPro"

Write-Host "Primary Add-In directory: $DocumentsFolder" -ForegroundColor Blue

if (Test-Path $TargetDir) {
    Write-Host "Removing legacy extracted Add-In directory: $TargetDir" -ForegroundColor Gray
    Remove-Item -LiteralPath $TargetDir -Recurse -Force
}

# 4. Copy official MSBuild Add-In package
$BuildOutputDir = Join-Path $AddinDir "ArcGisMcpAddin\bin\Debug\win-x64"
$BuildPackagePath = Join-Path $BuildOutputDir "ArcGisMcpAddin.esriAddinX"

if (!(Test-Path $BuildOutputDir)) {
    Write-Error "Build output directory was not found: $BuildOutputDir"
}

if (!(Test-Path $BuildPackagePath)) {
    Write-Error "MSBuild Add-In package was not found: $BuildPackagePath"
}

New-Item -ItemType Directory -Path $DocumentsFolder -Force | Out-Null
$PrimaryPackagePath = Join-Path $DocumentsFolder "ArcGisMcpAddin.esriAddinX"

Write-Host "Copying official Add-In package from $BuildPackagePath..." -ForegroundColor Gray
Copy-Item -LiteralPath $BuildPackagePath -Destination $PrimaryPackagePath -Force

if ($FallbackDocumentsFolder -ne $DocumentsFolder) {
    New-Item -ItemType Directory -Path $FallbackDocumentsFolder -Force | Out-Null
    Copy-Item -LiteralPath $BuildPackagePath -Destination (Join-Path $FallbackDocumentsFolder "ArcGisMcpAddin.esriAddinX") -Force
}

Write-Host "SUCCESS: Add-In successfully installed!" -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "How to verify:" -ForegroundColor Yellow
Write-Host "1. Launch ArcGIS Pro." -ForegroundColor Gray
Write-Host "2. Go to 'Settings' -> 'Add-In Manager' and verify 'ArcGIS Pro MCP Server Bridge' is listed." -ForegroundColor Gray
Write-Host "3. Open a map. You will see an 'ArcGIS MCP' tab in the main ribbon." -ForegroundColor Gray
Write-Host "====================================================" -ForegroundColor Cyan
