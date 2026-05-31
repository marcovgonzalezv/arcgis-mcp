# Security Policy

## Supported versions

Security fixes target the current `main` branch unless a release branch is
published later.

## Security model

`arcgis-mcp` exposes ArcGIS Pro operations through a local Windows Named Pipe.
The Python MCP server and the ArcGIS Pro Add-In are expected to run on the same
machine and under the same Windows user context.

Only connect trusted MCP clients to this server. A connected client can request
project, layer, editing, portal, geoprocessing, export, and file operations
inside the active ArcGIS Pro session.

## Reporting a vulnerability

Use GitHub Security Advisories when the repository is hosted on GitHub. If
private advisories are not enabled, open a minimal public issue that describes
the affected area without including exploit details.

Useful reports include:

- affected version or commit;
- operating system and ArcGIS Pro version;
- command or workflow involved;
- expected behavior;
- observed behavior;
- minimal reproduction steps.
