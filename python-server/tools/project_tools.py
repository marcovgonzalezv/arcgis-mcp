from mcp.server.fastmcp import Context
from pipe_client import ArcGisPipeClient

client = ArcGisPipeClient()


def _format_list(title: str, items: list, formatter) -> str:
    if not items:
        return f"No {title.lower()} found."
    lines = [f"{title}:"]
    lines.extend(formatter(item) for item in items)
    return "\n".join(lines)


def list_maps(ctx: Context = None) -> str:
    """
    Lists maps in the current ArcGIS Pro project.
    """
    if ctx:
        ctx.info("Listing project maps...")
    resp = client.send_command("list_maps")
    if not resp.get("success"):
        return f"Error listing maps: {resp.get('message') or resp.get('error')}"
    return _format_list(
        "Project maps",
        resp.get("data", {}).get("maps", []),
        lambda i: f"- {i.get('name')}",
    )


def open_map(map_name: str, ctx: Context = None) -> str:
    """
    Opens a map by name in ArcGIS Pro.
    """
    if ctx:
        ctx.info(f"Opening map '{map_name}'...")
    resp = client.send_command("open_map", {"map_name": map_name}, timeout_ms=10000)
    if resp.get("success"):
        return f"Map '{map_name}' opened."
    return f"Error opening map: {resp.get('message') or resp.get('error')}"


def save_project_as(
    output_path: str, overwrite: bool = False, ctx: Context = None
) -> str:
    """
    Saves the current ArcGIS Pro project to a new APRX path.
    """
    if ctx:
        ctx.info(f"Saving project as '{output_path}'...")
    resp = client.send_command(
        "save_project_as",
        {"output_path": output_path, "overwrite": overwrite},
        timeout_ms=30000,
    )
    if resp.get("success"):
        return f"Project saved as '{output_path}'."
    return f"Error saving project as: {resp.get('message') or resp.get('error')}"


def list_project_items(ctx: Context = None) -> str:
    """
    Lists maps, layouts, databases, toolboxes, and style items in the project.
    """
    if ctx:
        ctx.info("Listing project items...")
    resp = client.send_command("list_project_items")
    if not resp.get("success"):
        return (
            f"Error listing project items: {resp.get('message') or resp.get('error')}"
        )
    items = resp.get("data", {}).get("items", [])
    return _format_list(
        "Project items",
        items,
        lambda i: f"- {i.get('type')}: {i.get('name')} | {i.get('path', '')}",
    )


def list_bookmarks(map_name: str = "", ctx: Context = None) -> str:
    """
    Lists bookmarks for the active map or a named map.
    """
    if ctx:
        ctx.info("Listing map bookmarks...")
    resp = client.send_command("list_bookmarks", {"map_name": map_name})
    if not resp.get("success"):
        return f"Error listing bookmarks: {resp.get('message') or resp.get('error')}"
    bookmarks = resp.get("data", {}).get("bookmarks", [])
    return _format_list("Bookmarks", bookmarks, lambda i: f"- {i.get('name')}")
