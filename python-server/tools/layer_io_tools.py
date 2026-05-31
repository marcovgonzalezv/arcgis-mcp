from mcp.server.fastmcp import Context
from pipe_client import ArcGisPipeClient

client = ArcGisPipeClient()


def save_layer_file(layer_name: str, output_path: str, ctx: Context = None) -> str:
    """
    Saves a layer from the active map to a .lyrx file.
    """
    if ctx:
        ctx.info(f"Saving layer '{layer_name}' to '{output_path}'...")
    resp = client.send_command(
        "save_layer_file",
        {"layer_name": layer_name, "output_path": output_path},
        timeout_ms=30000,
    )
    if resp.get("success"):
        return f"Layer file saved to '{output_path}'."
    return f"Error saving layer file: {resp.get('message') or resp.get('error')}"


def load_layer_file(layer_file_path: str, ctx: Context = None) -> str:
    """
    Loads a .lyrx file into the active map.
    """
    if ctx:
        ctx.info(f"Loading layer file '{layer_file_path}'...")
    resp = client.send_command(
        "load_layer_file", {"layer_file_path": layer_file_path}, timeout_ms=30000
    )
    if resp.get("success"):
        return f"Layer file loaded from '{layer_file_path}'."
    return f"Error loading layer file: {resp.get('message') or resp.get('error')}"


def export_layer(
    layer_name: str, output_path: str, where_clause: str = "", ctx: Context = None
) -> str:
    """
    Exports a feature layer to a feature class, shapefile, or geodatabase dataset.
    """
    if ctx:
        ctx.info(f"Exporting layer '{layer_name}' to '{output_path}'...")
    resp = client.send_command(
        "export_layer",
        {
            "layer_name": layer_name,
            "output_path": output_path,
            "where_clause": where_clause,
        },
        timeout_ms=120000,
        retries=0,
    )
    if resp.get("success"):
        return f"Layer '{layer_name}' exported to '{output_path}'."
    return f"Error exporting layer: {resp.get('message') or resp.get('error')}"


def remove_layer(layer_name: str, ctx: Context = None) -> str:
    """
    Removes a layer from the active map.
    """
    if ctx:
        ctx.info(f"Removing layer '{layer_name}'...")
    resp = client.send_command("remove_layer", {"layer_name": layer_name})
    if resp.get("success"):
        return f"Layer '{layer_name}' removed."
    return f"Error removing layer: {resp.get('message') or resp.get('error')}"
