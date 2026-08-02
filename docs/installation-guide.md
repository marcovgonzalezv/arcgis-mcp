# Step-by-step installation guide

This guide explains how to install `arcgis-mcp` from scratch. It is divided into two tracks:

- **Track A (non-technical users):** automatic installation with a single command.
- **Track B (technical users):** manual compilation, development environment, MCP server registration, and testing.

Choose one track and follow the steps in order.

> This guide is also available in Spanish: `installation-guide.es.md`.

---

## Quick path: release distribution (all users)

If you downloaded the release artifacts (`ArcGisMcpAddin.esriAddinX`, the `arcgis_mcp_server-*.whl`, and `setup.ps1`), place the three files in the same folder and run:

```powershell
.\setup.ps1
```

`setup.ps1` locates Python (ArcGIS Pro conda or system Python), creates an isolated virtual environment, installs the wheel, registers the Add-In in ArcGIS Pro, and prints the ready-to-paste MCP client configuration. No build toolchain required.

After it finishes: open ArcGIS Pro 3.7, confirm the **ArcGIS MCP** tab, and restart your MCP client. The tracks below are only needed when building from source.

---

## What this project does

`arcgis-mcp` connects ArcGIS Pro 3.7 with a Model Context Protocol (MCP) compatible client. An MCP client is a program that can invoke ArcGIS Pro tools (open maps, count features, export layouts, run geoprocessing, and so on) through a secure local bridge.

The system has three components:

1. **ArcGIS Pro Add-In (C#):** an add-in loaded inside ArcGIS Pro that opens a local communication channel (Named Pipe).
2. **MCP server (Python):** exposes the public tools and communicates with the Add-In.
3. **MCP client:** your program or assistant that consumes the tools.

---

## Common requirements (both tracks)

Before starting, you need the following installed on Windows:

| Requirement | Version | How to verify |
|---|---|---|
| Windows 10 or 11 (64-bit) | - | Settings > System > About |
| ArcGIS Pro | 3.7 | Help > About ArcGIS Pro |
| .NET SDK | 10 | `dotnet --version` in PowerShell |
| Python | 3.10 or higher | `python --version` in PowerShell |
| Git (optional, to clone) | any | `git --version` |

You also need:

- The `arcgis-mcp` project code downloaded to a folder, for example `C:\path\to\arcgis-mcp`.
- An MCP-compatible client where you want to use the tools.

> Important: ArcGIS Pro should be closed during the Add-In installation. Open it afterwards, at the end.

---

## Track A: Automatic installation (non-technical users)

This track uses the automatic installer. You only need to run one command and follow the ArcGIS Pro prompts.

### Step A1. Open PowerShell

1. Press the `Windows` key.
2. Type `PowerShell`.
3. Click **Windows PowerShell** (administrator is not required, unless ArcGIS Pro itself runs as administrator).

### Step A2. Navigate to the project folder

In the PowerShell window, type `cd` followed by the folder path and press Enter:

```powershell
cd C:\path\to\arcgis-mcp
```

Replace `C:\path\to\arcgis-mcp` with the actual path where you downloaded the project.

### Step A3. Run the installer

Run the following command and press Enter:

```powershell
.\install_addin.ps1
```

The installer performs three actions automatically:

1. Verifies that the .NET SDK is installed.
2. Compiles the Add-In and produces the `ArcGisMcpAddin.esriAddinX` package.
3. Copies the package to the ArcGIS Pro Add-Ins folder.

On success you will see the message:

```text
SUCCESS: Add-In successfully installed!
```

### Step A4. Install the Python dependencies

In the same PowerShell window, switch to the server folder and install the packages:

```powershell
cd C:\path\to\arcgis-mcp\python-server
python -m pip install -r requirements.txt
```

Wait for the installation to finish.

### Step A5. Open ArcGIS Pro and verify

1. Open ArcGIS Pro.
2. Open or create a project with at least one map.
3. Go to **Settings > Add-In Manager**.
4. Confirm that **ArcGIS Pro MCP Server Bridge** appears in the list. The author is Marco Gonzalez Valdiviezo.
5. Open a map view.
6. The **ArcGIS MCP** tab must appear on the ribbon.
7. Click **Show MCP Status**. It should report that the server is active.

### Step A6. Test the connection

With ArcGIS Pro open and a map visible, run in PowerShell:

```powershell
cd C:\path\to\arcgis-mcp\python-server
python test_connection.py
```

Expected result:

```text
SUCCESS: Connected to ArcGIS Pro MCP Bridge.
```

If you see this message, the installation is complete. You can skip to [Register the MCP server in your client](#register-the-mcp-server-in-your-client).

---

## Track B: Technical installation (developers)

This track covers manual compilation, development environment setup, MCP client configuration, and test execution.

### Step B1. Verify the development tools

Open PowerShell and confirm the versions:

```powershell
dotnet --version
python --version
git --version
```

You need .NET 10 SDK, Python 3.10+, and Git. Compiling the Add-In also requires the ArcGIS Pro SDK assemblies, referenced locally from `C:\Program Files\ArcGIS\Pro\bin\`.

### Step B2. (Optional) Clone the repository

If you start from Git:

```powershell
cd C:\projects
git clone <repository-url> arcgis-mcp
cd arcgis-mcp
```

If you already have the project folder, skip this step.

### Step B3. Create and activate a Python virtual environment

An isolated environment is recommended. Replace the path with your preferred location:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If you prefer conda:

```powershell
conda create -n gis python=3.13
conda activate gis
```

### Step B4. Install the development dependencies

These include the runtime packages plus the testing tools (pytest, ruff):

```powershell
cd C:\path\to\arcgis-mcp\python-server
python -m pip install -r requirements-dev.txt
```

### Step B5. Compile the Add-In manually

```powershell
cd C:\path\to\arcgis-mcp\arcgis-addin
dotnet build .\ArcGisMcpAddin.sln --configuration Debug
```

Expected output: `0 Errors`. The package is generated at:

```text
arcgis-addin\ArcGisMcpAddin\bin\Debug\win-x64\ArcGisMcpAddin.esriAddinX
```

### Step B6. Deploy the Add-In

You can use the installer (`.\install_addin.ps1` from the project root) or copy the package manually to:

```text
%USERPROFILE%\Documents\ArcGIS\AddIns\ArcGISPro\ArcGisMcpAddin.esriAddinX
```

Then close and reopen ArcGIS Pro so it loads the new DLL.

### Step B7. Verify the Add-In load

1. Open ArcGIS Pro 3.7.
2. Open a project with a map.
3. Go to **Settings > Add-In Manager** and confirm that **ArcGIS Pro MCP Server Bridge** is listed.
4. Open the map view and locate the **ArcGIS MCP** tab on the ribbon.
5. Click **Show MCP Status** to confirm that the Named Pipe `\\.\pipe\ArcGisMcpBridge` is active.

### Step B8. Run the connection test

```powershell
cd C:\path\to\arcgis-mcp\python-server
python test_connection.py
```

Expected output:

```text
SUCCESS: Connected to ArcGIS Pro MCP Bridge.
```

### Step B9. Run the validation suite

To confirm that the code satisfies every contract (linting, formatting, tests, compilation):

```powershell
cd C:\path\to\arcgis-mcp
.\scripts\validate_release.ps1
```

Run the Python checks individually if you prefer:

```powershell
cd C:\path\to\arcgis-mcp\python-server
python -m ruff check . --no-cache
python -m ruff format . --check --no-cache
python -m pytest -q
python -m unittest discover -s tests -v
```

### Step B10. Register the MCP server in your client

Edit your MCP client configuration file and add the server (from-source invocation):

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

If `python.exe` is not on `PATH`, use the absolute path of the executable (for example, the virtual environment one). Restart the MCP client after saving the configuration.

---

## Register the MCP server in your client

This section applies to both tracks once everything is installed.

The MCP server runs with `python -m arcgis_mcp`, or as the `arcgis-mcp-server` console script after `pip install`. Register it in your MCP client with the configuration above. Examples of compatible clients: desktop applications with MCP support, code editors with an MCP extension, or any client that implements the protocol.

Recommendations:

- Always use the absolute path of the script and the Python executable.
- If you use a virtual environment or conda, point to its `python.exe` so it finds `mcp`, `pywin32`, and `pydantic`.
- ArcGIS Pro must be open with the Add-In loaded for the tools that require the bridge to work.

---

## Troubleshooting

### The Add-In does not appear in ArcGIS Pro

- Close ArcGIS Pro completely and reopen it.
- Verify that the `ArcGisMcpAddin.esriAddinX` file is in `%USERPROFILE%\Documents\ArcGIS\AddIns\ArcGISPro\`.
- Run `.\install_addin.ps1` again from the project root.

### Error: "dotnet CLI was not found"

The .NET 10 SDK is missing. Download and install it from the official .NET site. Close and reopen PowerShell after installing.

### Add-In compilation error

- Confirm that ArcGIS Pro 3.7 is installed at `C:\Program Files\ArcGIS\Pro`.
- Verify that the DLLs exist in `C:\Program Files\ArcGIS\Pro\bin` and that the `Esri.ProApp.SDK.Desktop.targets` file is present.
- Run `dotnet build` from the `arcgis-addin` folder and review the error messages.

### `python test_connection.py` reports CONNECTION TIMEOUT

- Confirm that ArcGIS Pro is open with an active map.
- Confirm that the **ArcGIS MCP** tab is visible on the ribbon.
- If ArcGIS Pro runs as administrator, run the test as administrator too.

### `python test_connection.py` reports "Access denied" (Code 5)

The client and ArcGIS Pro run at different permission levels. Solutions:

1. Close ArcGIS Pro and reopen it normally (without administrator).
2. Run the connection test without administrator.
3. If you need administrator for ArcGIS Pro, run the MCP client as administrator too.

### Error: No module named 'mcp' (or 'pywin32' or 'pydantic')

The Python dependencies are not installed in the active environment:

```powershell
cd C:\path\to\arcgis-mcp\python-server
python -m pip install -r requirements.txt
```

If you use a virtual environment or conda, activate it before installing.

### The MCP client cannot find the tools

- Verify that the script path in the configuration is absolute and correct.
- Confirm that you point to the `python.exe` of the environment where you installed the dependencies.
- Restart the MCP client after changing the configuration.

---

## Security model

- The Add-In accepts commands through a local Named Pipe and executes them inside the active ArcGIS Pro session.
- Run ArcGIS Pro and the MCP client under the same Windows user.
- Connect only trusted MCP clients: the tools can inspect, edit, export, publish, and geoprocess data from the active project.
- See `SECURITY.md` for more details.

---

## Quick summary

| Step | Track A | Track B |
|---|---|---|
| Open PowerShell | A1 | B1 |
| Compile Add-In | A3 (automatic) | B5 (manual) |
| Install Python packages | A4 | B4 |
| Load Add-In in ArcGIS Pro | A5 | B7 |
| Test connection | A6 | B8 |
| Register MCP client | final | B10 |
| Full validation | optional | B9 |
