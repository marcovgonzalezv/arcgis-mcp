from pipe_client import ArcGisPipeClient
from mcp.server.fastmcp import Context

client = ArcGisPipeClient()


def health_check(ctx: Context = None) -> str:
    """
    Checks MCP, Add-in, ArcGIS Pro, project, map, and IPC status.
    """
    if ctx:
        ctx.info("Running ArcGIS MCP health check...")
    resp = client.send_command("health_check", timeout_ms=3000, retries=1)
    if not resp.get("success"):
        return (
            "Health check failed.\n"
            f"Error code: {resp.get('error_code', 'UNKNOWN')}\n"
            f"Message: {resp.get('message') or resp.get('error')}"
        )
    data = resp.get("data", {})
    lines = ["ArcGIS MCP health check:"]
    for key, value in data.items():
        lines.append(f"- {key}: {value}")
    lines.append(f"- elapsed_ms: {resp.get('elapsed_ms')}")
    return "\n".join(lines)


def get_capabilities(ctx: Context = None) -> str:
    """
    Lists Add-in and MCP command capabilities currently exposed.
    """
    if ctx:
        ctx.info("Retrieving ArcGIS MCP capabilities...")
    resp = client.send_command("get_capabilities", timeout_ms=3000, retries=1)
    if not resp.get("success"):
        return (
            f"Error retrieving capabilities: {resp.get('message') or resp.get('error')}"
        )
    data = resp.get("data", {})
    mcp_tools = data.get("mcp_tools") or data.get("commands", [])
    addin_commands = data.get("addin_commands", [])
    lines = [
        f"MCP version: {data.get('mcp_version', 'unknown')}",
        f"Add-in version: {data.get('addin_version', 'unknown')}",
        f"MCP tools ({data.get('mcp_tool_count', len(mcp_tools))}):",
    ]
    lines.extend(f"- {tool}" for tool in mcp_tools)
    if addin_commands:
        lines.append(
            f"Add-in commands ({data.get('addin_command_count', len(addin_commands))}):"
        )
        lines.extend(f"- {command}" for command in addin_commands)
    return "\n".join(lines)
