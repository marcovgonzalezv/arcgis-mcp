from pipe_client import ArcGisPipeClient
from mcp.server.fastmcp import Context

client = ArcGisPipeClient()


def get_active_map(ctx: Context = None) -> str:
    """
    Returns the name of the active map and scene view in ArcGIS Pro.
    """
    if ctx:
        ctx.info("Requesting active map information...")
    resp = client.send_command("get_active_map")
    if resp.get("success"):
        data = resp.get("data", {})
        return f"Active Map: {data.get('map_name', 'None')}\nActive View Type: {data.get('view_type', 'None')}"
    else:
        return f"Error: {resp.get('error', 'Unknown error')}"


def list_layers(include_hidden: bool = True, ctx: Context = None) -> str:
    """
    Lists all layers in the active map, showing their names, types, visibility, and total features.
    """
    if ctx:
        ctx.info(f"Listing layers (include_hidden={include_hidden})...")
    resp = client.send_command("list_layers", {"include_hidden": include_hidden})
    if resp.get("success"):
        layers = resp.get("data", {}).get("layers", [])
        if not layers:
            return "No layers found in the active map."

        result = ["Layers in active map:"]
        for idx, layer in enumerate(layers, 1):
            visible_str = "Visible" if layer.get("visible") else "Hidden"
            count_str = (
                f"({layer.get('count')} features)"
                if layer.get("count") is not None
                else ""
            )
            result.append(
                f"{idx}. {layer.get('name')} [{layer.get('type')}] - {visible_str} {count_str}"
            )
        return "\n".join(result)
    else:
        return f"Error: {resp.get('error', 'Unknown error')}"


def zoom_to_layer(layer_name: str, ctx: Context = None) -> str:
    """
    Zooms the active map view to the spatial extent of a specific layer by name.
    """
    if ctx:
        ctx.info(f"Zooming to layer '{layer_name}'...")
    resp = client.send_command("zoom_to_layer", {"layer_name": layer_name})
    if resp.get("success"):
        return f"Successfully zoomed to layer '{layer_name}'."
    else:
        return f"Error zooming to layer '{layer_name}': {resp.get('error')}"


def toggle_layer_visibility(layer_name: str, visible: bool, ctx: Context = None) -> str:
    """
    Toggles the visibility of a layer in the active map by name.
    """
    state = "visible" if visible else "hidden"
    if ctx:
        ctx.info(f"Setting layer '{layer_name}' visibility to {state}...")
    resp = client.send_command(
        "toggle_layer_visibility", {"layer_name": layer_name, "visible": visible}
    )
    if resp.get("success"):
        return f"Layer '{layer_name}' is now {'visible' if visible else 'hidden'}."
    else:
        return (
            f"Error updating visibility for layer '{layer_name}': {resp.get('error')}"
        )


def set_map_extent(
    xmin: float,
    ymin: float,
    xmax: float,
    ymax: float,
    wkid: int = 4326,
    ctx: Context = None,
) -> str:
    """
    Sets the active map view extent to the specified bounding box coordinates.
    Default coordinate system is WGS84 (WKID 4326).
    """
    if ctx:
        ctx.info(
            f"Setting map extent to [{xmin}, {ymin}, {xmax}, {ymax}] (WKID: {wkid})..."
        )
    resp = client.send_command(
        "set_map_extent",
        {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax, "wkid": wkid},
    )
    if resp.get("success"):
        return f"Map view extent successfully set to: xmin={xmin}, ymin={ymin}, xmax={xmax}, ymax={ymax}."
    else:
        return f"Error setting map extent: {resp.get('error')}"


def add_layer_to_map(data_path: str, layer_name: str = "", ctx: Context = None) -> str:
    """
    Adds a dataset, layer file, or service URL to the active map.
    """
    if ctx:
        ctx.info(f"Adding layer from '{data_path}'...")
    resp = client.send_command(
        "add_layer_to_map", {"data_path": data_path, "layer_name": layer_name}
    )
    if resp.get("success"):
        data = resp.get("data", {})
        return f"Layer added to active map: {data.get('layer_name', data_path)}."
    return f"Error adding layer: {resp.get('error')}"


def set_layer_transparency(
    layer_name: str, transparency: float, ctx: Context = None
) -> str:
    """
    Sets layer transparency from 0 to 100.
    """
    if ctx:
        ctx.info(f"Setting transparency for '{layer_name}' to {transparency}...")
    resp = client.send_command(
        "set_layer_transparency",
        {"layer_name": layer_name, "transparency": transparency},
    )
    if resp.get("success"):
        return f"Layer '{layer_name}' transparency set to {transparency}."
    return f"Error setting layer transparency: {resp.get('error')}"


def set_definition_query(layer_name: str, sql_filter: str, ctx: Context = None) -> str:
    """
    Sets or clears a definition query on a feature layer.
    """
    if ctx:
        ctx.info(f"Setting definition query for '{layer_name}'...")
    resp = client.send_command(
        "set_definition_query", {"layer_name": layer_name, "sql_filter": sql_filter}
    )
    if resp.get("success"):
        return f"Definition query updated for layer '{layer_name}'."
    return f"Error setting definition query: {resp.get('error')}"


def clear_selection(layer_name: str = "", ctx: Context = None) -> str:
    """
    Clears selection in one feature layer or in the whole active map.
    """
    target = layer_name or "active map"
    if ctx:
        ctx.info(f"Clearing selection in {target}...")
    resp = client.send_command("clear_selection", {"layer_name": layer_name})
    if resp.get("success"):
        return f"Selection cleared in {target}."
    return f"Error clearing selection: {resp.get('error')}"


def save_project(ctx: Context = None) -> str:
    """
    Saves the current ArcGIS Pro project.
    """
    if ctx:
        ctx.info("Saving current ArcGIS Pro project...")
    resp = client.send_command("save_project")
    if resp.get("success"):
        return "Current ArcGIS Pro project saved."
    return f"Error saving project: {resp.get('error')}"
