from typing import Any

from mcp.server.fastmcp import Context
from pipe_client import ArcGisPipeClient

client = ArcGisPipeClient()


def update_attributes(
    layer_name: str, object_id: int, attributes: dict[str, Any], ctx: Context = None
) -> str:
    """
    Updates attributes for a feature by ObjectID.
    """
    if ctx:
        ctx.info(f"Updating feature {object_id} in '{layer_name}'...")
    resp = client.send_command(
        "update_attributes",
        {"layer_name": layer_name, "object_id": object_id, "attributes": attributes},
        timeout_ms=30000,
    )
    if resp.get("success"):
        return f"Attributes updated for ObjectID {object_id} in '{layer_name}'."
    return f"Error updating attributes: {resp.get('message') or resp.get('error')}"


def create_feature(
    layer_name: str,
    x: float,
    y: float,
    wkid: int = 4326,
    attributes: dict[str, Any] | None = None,
    ctx: Context = None,
) -> str:
    """
    Creates a point feature in a feature layer.
    """
    if ctx:
        ctx.info(f"Creating point feature in '{layer_name}'...")
    resp = client.send_command(
        "create_feature",
        {
            "layer_name": layer_name,
            "x": x,
            "y": y,
            "wkid": wkid,
            "attributes": attributes or {},
        },
        timeout_ms=30000,
    )
    if resp.get("success"):
        return f"Feature created in '{layer_name}'."
    return f"Error creating feature: {resp.get('message') or resp.get('error')}"


def delete_selected_features(layer_name: str, ctx: Context = None) -> str:
    """
    Deletes selected features from a feature layer.
    """
    if ctx:
        ctx.info(f"Deleting selected features from '{layer_name}'...")
    resp = client.send_command(
        "delete_selected_features", {"layer_name": layer_name}, timeout_ms=30000
    )
    if resp.get("success"):
        data = resp.get("data", {})
        return f"Deleted {data.get('deleted_count', 0)} selected features from '{layer_name}'."
    return (
        f"Error deleting selected features: {resp.get('message') or resp.get('error')}"
    )


def undo_last_edit(ctx: Context = None) -> str:
    """
    Undoes the last edit operation created through this MCP Add-in.
    """
    if ctx:
        ctx.info("Undoing last MCP edit operation...")
    resp = client.send_command("undo_last_edit", timeout_ms=30000)
    if resp.get("success"):
        return "Last MCP edit operation undone."
    return f"Error undoing last edit: {resp.get('message') or resp.get('error')}"
