from pipe_client import ArcGisPipeClient
from mcp.server.fastmcp import Context

client = ArcGisPipeClient()


def apply_graduated_symbology(
    layer_name: str,
    field_name: str,
    break_count: int = 5,
    classification_method: str = "NaturalBreaks",
    color_ramp: str = "Yellow-Orange-Red",
    ctx: Context = None,
) -> str:
    """
    Applies graduated color symbology to a feature layer.
    """
    if ctx:
        ctx.info(f"Applying graduated symbology to '{layer_name}'...")
    resp = client.send_command(
        "apply_graduated_symbology",
        {
            "layer_name": layer_name,
            "field_name": field_name,
            "break_count": break_count,
            "classification_method": classification_method,
            "color_ramp": color_ramp,
        },
    )
    if resp.get("success"):
        return f"Graduated symbology applied to '{layer_name}' using '{field_name}'."
    return f"Error applying graduated symbology: {resp.get('error')}"


def apply_unique_value_symbology(
    layer_name: str,
    field_name: str,
    color_ramp: str = "Default",
    values_limit: int = 100,
    ctx: Context = None,
) -> str:
    """
    Applies unique value symbology to a feature layer.
    """
    if ctx:
        ctx.info(f"Applying unique value symbology to '{layer_name}'...")
    resp = client.send_command(
        "apply_unique_value_symbology",
        {
            "layer_name": layer_name,
            "field_name": field_name,
            "color_ramp": color_ramp,
            "values_limit": values_limit,
        },
    )
    if resp.get("success"):
        return f"Unique value symbology applied to '{layer_name}' using '{field_name}'."
    return f"Error applying unique value symbology: {resp.get('error')}"


def apply_symbology_from_layer(
    target_layer: str, symbology_layer: str, ctx: Context = None
) -> str:
    """
    Applies symbology from a layer or layer file using ArcGIS geoprocessing.
    """
    if ctx:
        ctx.info(f"Applying symbology from '{symbology_layer}' to '{target_layer}'...")
    resp = client.send_command(
        "apply_symbology_from_layer",
        {"target_layer": target_layer, "symbology_layer": symbology_layer},
    )
    if resp.get("success"):
        return f"Symbology from '{symbology_layer}' applied to '{target_layer}'."
    return f"Error applying symbology from layer: {resp.get('error')}"


def label_layer(
    layer_name: str,
    field_name: str,
    visible: bool = True,
    expression_engine: str = "Arcade",
    ctx: Context = None,
) -> str:
    """
    Enables labels on a feature layer using a field-based expression.
    """
    if ctx:
        ctx.info(f"Configuring labels for '{layer_name}'...")
    resp = client.send_command(
        "label_layer",
        {
            "layer_name": layer_name,
            "field_name": field_name,
            "visible": visible,
            "expression_engine": expression_engine,
        },
    )
    if resp.get("success"):
        state = "enabled" if visible else "disabled"
        return f"Labels {state} for '{layer_name}' using '{field_name}'."
    return f"Error configuring labels: {resp.get('error')}"


def get_layer_symbology(layer_name: str, ctx: Context = None) -> str:
    """
    Returns renderer metadata for a layer.
    """
    if ctx:
        ctx.info(f"Getting symbology for '{layer_name}'...")
    resp = client.send_command("get_layer_symbology", {"layer_name": layer_name})
    if not resp.get("success"):
        return (
            f"Error getting layer symbology: {resp.get('message') or resp.get('error')}"
        )
    data = resp.get("data", {})
    return "\n".join(
        [
            f"Layer: {data.get('layer_name', layer_name)}",
            f"Renderer: {data.get('renderer_type', 'unknown')}",
            f"Definition: {data.get('renderer_json', '')}",
        ]
    )


def update_class_breaks(
    layer_name: str,
    field_name: str,
    break_count: int = 5,
    classification_method: str = "NaturalBreaks",
    color_ramp: str = "Yellow-Orange-Red",
    ctx: Context = None,
) -> str:
    """
    Updates class breaks by rebuilding graduated symbology.
    """
    return apply_graduated_symbology(
        layer_name, field_name, break_count, classification_method, color_ramp, ctx
    )


def save_layer_file(layer_name: str, output_path: str, ctx: Context = None) -> str:
    """
    Saves a layer to a .lyrx file.
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


def apply_raster_colorizer(
    raster_layer: str,
    symbology_layer: str = "",
    color_ramp: str = "Default",
    ctx: Context = None,
) -> str:
    """
    Applies raster symbology. A .lyrx symbology layer is preferred.
    """
    if ctx:
        ctx.info(f"Applying raster colorizer to '{raster_layer}'...")
    resp = client.send_command(
        "apply_raster_colorizer",
        {
            "raster_layer": raster_layer,
            "symbology_layer": symbology_layer,
            "color_ramp": color_ramp,
        },
        timeout_ms=30000,
    )
    if resp.get("success"):
        return f"Raster colorizer applied to '{raster_layer}'."
    return (
        f"Error applying raster colorizer: {resp.get('message') or resp.get('error')}"
    )
