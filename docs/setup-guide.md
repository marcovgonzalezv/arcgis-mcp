# Installation and configuration guide

This guide describes how to compile, install, configure, and test `arcgis-mcp` with ArcGIS Pro 3.7.

## Requirements

1. ArcGIS Pro 3.7 installed with an active license.
2. .NET 10 SDK.
3. Python 3.10 or higher.
4. Packages from `python-server/requirements.txt`.

## Compile and install the Add-In

Run PowerShell at the project root:

```powershell
cd C:\path\to\arcgis-mcp
.\install_addin.ps1
```

The installer:

- Compiles `arcgis-addin/ArcGisMcpAddin.sln`.
- Generates `ArcGisMcpAddin.esriAddinX`.
- Copies the package to the ArcGIS Pro Add-Ins folder.

After installation, close and reopen ArcGIS Pro to load the current Add-In version.

## Install Python dependencies

```powershell
cd C:\path\to\arcgis-mcp\python-server
pip install -r requirements-dev.txt
pip install -e .
```

You may use the ArcGIS Pro Python distribution or a dedicated virtual environment with `mcp` and `pywin32`.

The editable install (`pip install -e .`) registers the `arcgis-mcp-server` console script, so the server can be launched with `python -m arcgis_mcp` or directly as `arcgis-mcp-server`.

## Verify the Add-In

1. Open ArcGIS Pro 3.7.
2. Open or create a project with at least one map.
3. Go to `Settings > Add-In Manager`.
4. Verify that `ArcGIS Pro MCP Server Bridge` is listed.
5. Open a map view.
6. The `ArcGIS MCP` tab must appear on the ribbon.
7. Use `Show MCP Status` to confirm that the Named Pipe `\\.\pipe\ArcGisMcpBridge` is active.

## Test the connection

With ArcGIS Pro open:

```powershell
cd C:\path\to\arcgis-mcp\python-server
python test_connection.py
```

Expected output:

```text
SUCCESS: Connected to ArcGIS Pro MCP Bridge.
```

## Register the MCP server

Add the server to your MCP client configuration.

Installed entry point (after `pip install -e .` or `pip install arcgis-mcp-server`):

```json
{
  "mcpServers": {
    "arcgis-mcp": {
      "command": "C:/path/to/Scripts/arcgis-mcp-server.exe"
    }
  }
}
```

From source:

```json
{
  "mcpServers": {
    "arcgis-mcp": {
      "command": "python.exe",
      "args": ["-m", "arcgis_mcp"]
    }
  }
}
```

If `python.exe` is not on `PATH`, use the absolute path of the executable.

## Local tests

```powershell
cd C:\path\to\arcgis-mcp\python-server
python -m ruff check . --no-cache
python -m ruff format . --check --no-cache
python -m pytest -q
python -m unittest discover -s tests -v
```

```powershell
cd C:\path\to\arcgis-mcp\arcgis-addin
dotnet build .\ArcGisMcpAddin.sln
```
