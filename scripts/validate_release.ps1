$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$PythonServer = Join-Path $RepoRoot "python-server"
$AddinRoot = Join-Path $RepoRoot "arcgis-addin"
$SolutionFile = Join-Path $AddinRoot "ArcGisMcpAddin.sln"

function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [Parameter(Mandatory = $true)]
        [scriptblock]$Command
    )

    Write-Host "==> $Name" -ForegroundColor Cyan
    & $Command
}

function Invoke-Native {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$FilePath failed with exit code $LASTEXITCODE."
    }
}

function Remove-GeneratedArtifacts {
    $targets = @(
        "arcgis-addin\ArcGisMcpAddin\bin",
        "arcgis-addin\ArcGisMcpAddin\obj",
        "python-server\__pycache__",
        "python-server\tools\__pycache__",
        "python-server\resources\__pycache__",
        "python-server\prompts\__pycache__",
        "python-server\tests\__pycache__",
        "python-server\.pytest_cache",
        "python-server\.ruff_cache",
        ".pytest_cache"
    )

    foreach ($relativePath in $targets) {
        $path = Join-Path $RepoRoot $relativePath
        if (!(Test-Path -LiteralPath $path)) {
            continue
        }

        $resolvedPath = (Resolve-Path -LiteralPath $path).Path
        if (!$resolvedPath.StartsWith($RepoRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "Refusing to remove path outside repository: $resolvedPath"
        }

        Remove-Item -LiteralPath $resolvedPath -Recurse -Force
    }
}

try {
    Invoke-Step "Python lint" {
        Push-Location $PythonServer
        try {
            Invoke-Native "python" @("-m", "ruff", "check", ".", "--no-cache")
        }
        finally {
            Pop-Location
        }
    }

    Invoke-Step "Python format check" {
        Push-Location $PythonServer
        try {
            Invoke-Native "python" @("-m", "ruff", "format", ".", "--check", "--no-cache")
        }
        finally {
            Pop-Location
        }
    }

    Invoke-Step "Python tests" {
        Push-Location $PythonServer
        try {
            $env:PYTHONDONTWRITEBYTECODE = "1"
            Invoke-Native "python" @("-m", "pytest", "-q")
            Invoke-Native "python" @("-m", "unittest", "discover", "-s", "tests", "-v")
        }
        finally {
            Remove-Item Env:\PYTHONDONTWRITEBYTECODE -ErrorAction SilentlyContinue
            Pop-Location
        }
    }

    Invoke-Step "Python bytecode compile" {
        Invoke-Native "python" @("-m", "compileall", "-q", $PythonServer)
    }

    Invoke-Step "Add-In format check" {
        Push-Location $AddinRoot
        try {
            Invoke-Native "dotnet" @("format", $SolutionFile, "--verify-no-changes", "--verbosity", "minimal")
        }
        finally {
            Pop-Location
        }
    }

    Invoke-Step "Add-In build" {
        Push-Location $AddinRoot
        try {
            Invoke-Native "dotnet" @("build", $SolutionFile)
        }
        finally {
            Pop-Location
        }
    }

    Invoke-Step "Git whitespace check" {
        Push-Location $RepoRoot
        try {
            Invoke-Native "git" @("diff", "--check")
            Invoke-Native "git" @("diff", "--cached", "--check")
        }
        finally {
            Pop-Location
        }
    }
}
finally {
    Remove-GeneratedArtifacts
}

Invoke-Step "Generated artifact scan" {
    $patterns = @(
        "*.pyc",
        "*.pdb",
        "*.dll",
        "*.esriAddinX",
        "*.deps.json"
    )
    $excludedParts = @(
        ".git",
        ".venv",
        "venv"
    )

    $files = Get-ChildItem -LiteralPath $RepoRoot -Recurse -Force -File |
        Where-Object {
            $pathParts = $_.FullName.Substring($RepoRoot.Length).Split([IO.Path]::DirectorySeparatorChar)
            -not ($pathParts | Where-Object { $excludedParts -contains $_ })
        } |
        Where-Object {
            $name = $_.Name
            ($patterns | Where-Object { $name -like $_ }) -or
            ($_.FullName -match "\\(bin|obj|__pycache__|\.pytest_cache|\.ruff_cache)\\")
        }

    if ($files) {
        $files | ForEach-Object { Write-Error "Generated artifact found: $($_.FullName)" }
        throw "Generated artifacts remain in the repository."
    }
}
