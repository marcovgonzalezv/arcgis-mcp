# Release checklist

Use this list before creating a public release of the repository.

## Source code

- The tree does not contain `bin/`, `obj/`, `__pycache__/`, `.pytest_cache/`, `.vs/`, or generated `.esriAddinX` packages.
- No local paths, usernames, personal folders, or development environment markers exist in public files.
- `spatial_join` is exposed exactly once as an MCP tool.
- The public contract maintains 68 MCP tools, 2 MCP resources, and 2 prompt templates.
- `stage_service_definition` is exposed to convert `.sddraft` to `.sd` before publishing.
- The Add-In maintains 57 internal commands; `ping` is an internal IPC command only.
- `CONTRIBUTING.md` and `SECURITY.md` are up to date.

## Local validation

Run from the repository root:

```powershell
.\scripts\validate_release.ps1
```

Or run the checks individually:

```powershell
python -m pip install -r requirements-dev.txt
python -m ruff check . --no-cache
python -m ruff format . --check --no-cache
python -m pytest -q
python -m unittest discover -s tests -v
```

Run from `arcgis-addin/`:

```powershell
dotnet build .\ArcGisMcpAddin.sln
```

With ArcGIS Pro open and the Add-In loaded:

```powershell
python test_connection.py
```

## GitHub publication

- Create the local Git repository only after cleaning generated artifacts.
- Confirm that `.gitignore`, `.gitattributes`, and `.editorconfig` are included.
- Choose a license before marking the project as open source.
- Confirm `git diff --cached --check` before the first commit.
- Enable GitHub Actions and verify that the `Python checks` workflow completes without errors.
- Document the supported ArcGIS Pro, .NET SDK, and Python versions in the first release.
