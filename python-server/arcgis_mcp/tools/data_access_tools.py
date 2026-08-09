"""
Bulk data-access and bookmark wrappers.

These wrap the Add-In DataAccessCommands (arcpy.da-style batch edits) and
BookmarkCommands so the caller can perform high-throughput inserts/updates and
manage spatial bookmarks.
"""

from mcp.server.fastmcp import Context

from ..pipe_client import ArcGisPipeClient

client = ArcGisPipeClient()


def _send(command: str, params: dict, ctx: Context = None, info: str = "") -> str:
    if ctx and info:
        ctx.info(info)
    resp = client.send_command(command, params, timeout_ms=120000)
    if resp.get("success"):
        data = resp.get("data", {}) or {}
        return f"{command} succeeded: {data}"
    error = resp.get("message") or resp.get("error")
    return f"Error in {command}: {error}"


def insert_features(layer_name: str, features: list, ctx: Context = None) -> str:
    """
    Inserts multiple point features in a single edit operation (arcpy.da-style
    batch insert).
    features: list of {"x": float, "y": float, "wkid": int=4326, "attributes": {...}}.
    """
    return _send(
        "insert_features",
        {"layer_name": layer_name, "features": features},
        ctx,
        f"Inserting {len(features)} features into '{layer_name}'...",
    )


def update_features(layer_name: str, updates: list, ctx: Context = None) -> str:
    """
    Updates multiple features by ObjectID in a single edit operation.
    updates: list of {"objectid": int, "attributes": {...}}.
    """
    return _send(
        "update_features",
        {"layer_name": layer_name, "updates": updates},
        ctx,
        f"Updating {len(updates)} features in '{layer_name}'...",
    )


def delete_features(layer_name: str, object_ids: list, ctx: Context = None) -> str:
    """
    Deletes features identified by the given ObjectIDs.
    """
    return _send(
        "delete_features",
        {"layer_name": layer_name, "object_ids": object_ids},
        ctx,
        f"Deleting {len(object_ids)} features from '{layer_name}'...",
    )


def create_bookmark(name: str, ctx: Context = None) -> str:
    """
    Creates a spatial bookmark from the current active map view extent.
    """
    return _send(
        "create_bookmark",
        {"name": name},
        ctx,
        f"Creating bookmark '{name}'...",
    )


def zoom_to_bookmark(name: str, ctx: Context = None) -> str:
    """
    Zooms the active map to a named bookmark.
    """
    return _send(
        "zoom_to_bookmark",
        {"name": name},
        ctx,
        f"Zooming to bookmark '{name}'...",
    )


def delete_bookmark(name: str, ctx: Context = None) -> str:
    """
    Deletes a bookmark by name from the active map.
    """
    return _send(
        "delete_bookmark",
        {"name": name},
        ctx,
        f"Deleting bookmark '{name}'...",
    )
