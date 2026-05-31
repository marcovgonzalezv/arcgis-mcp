from pipe_client import ArcGisPipeClient
from mcp.server.fastmcp import Context

client = ArcGisPipeClient()


def list_layouts(ctx: Context = None) -> str:
    """
    Lists all the layouts (print layouts/map layouts) defined in the current ArcGIS Pro project.
    """
    if ctx:
        ctx.info("Retrieving list of project layouts...")
    resp = client.send_command("list_layouts")
    if resp.get("success"):
        layouts = resp.get("data", {}).get("layouts", [])
        if not layouts:
            return "No layouts found in the current project."

        result = ["Layouts in current project:"]
        for idx, layout in enumerate(layouts, 1):
            result.append(f"{idx}. {layout}")
        return "\n".join(result)
    else:
        return f"Error listing layouts: {resp.get('error', 'Unknown error')}"


def export_layout(
    layout_name: str,
    output_path: str,
    format_type: str = "PDF",
    resolution_dpi: int = 300,
    ctx: Context = None,
) -> str:
    """
    Exports a print layout to the specified output file path.
    format_type can be: "PDF", "PNG", "JPEG". Resolution is specified in DPI (default 300).
    """
    if ctx:
        ctx.info(
            f"Exporting layout '{layout_name}' to '{output_path}' ({format_type} @ {resolution_dpi} DPI)..."
        )
    resp = client.send_command(
        "export_layout",
        {
            "layout_name": layout_name,
            "output_path": output_path,
            "format": format_type,
            "resolution": resolution_dpi,
        },
    )
    if resp.get("success"):
        return f"Layout '{layout_name}' successfully exported to '{output_path}' as {format_type}."
    else:
        return f"Error exporting layout '{layout_name}': {resp.get('error')}"


def create_basic_layout(
    layout_name: str,
    title: str,
    page_width: float = 11.0,
    page_height: float = 8.5,
    ctx: Context = None,
) -> str:
    """
    Creates a basic layout from the active map with map frame, title, legend, north arrow, and scale bar.
    """
    if ctx:
        ctx.info(f"Creating layout '{layout_name}'...")
    resp = client.send_command(
        "create_basic_layout",
        {
            "layout_name": layout_name,
            "title": title,
            "page_width": page_width,
            "page_height": page_height,
        },
        timeout_ms=15000,
    )
    if resp.get("success"):
        return f"Layout '{layout_name}' created."
    return f"Error creating layout '{layout_name}': {resp.get('error')}"


def export_active_map(
    output_path: str,
    format_type: str = "PNG",
    width: int = 1920,
    height: int = 1080,
    resolution_dpi: int = 150,
    ctx: Context = None,
) -> str:
    """
    Exports the active map view to an image file.
    """
    if ctx:
        ctx.info(f"Exporting active map to '{output_path}'...")
    resp = client.send_command(
        "export_active_map",
        {
            "output_path": output_path,
            "format": format_type,
            "width": width,
            "height": height,
            "resolution": resolution_dpi,
        },
        timeout_ms=15000,
    )
    if resp.get("success"):
        return f"Active map exported to '{output_path}' as {format_type}."
    return f"Error exporting active map: {resp.get('error')}"


def create_map_series(
    layout_name: str,
    map_frame_name: str,
    index_layer_name: str,
    name_field: str,
    ctx: Context = None,
) -> str:
    """
    Creates a spatial map series for a layout.
    """
    if ctx:
        ctx.info(f"Creating map series in layout '{layout_name}'...")
    resp = client.send_command(
        "create_map_series",
        {
            "layout_name": layout_name,
            "map_frame_name": map_frame_name,
            "index_layer_name": index_layer_name,
            "name_field": name_field,
        },
        timeout_ms=30000,
    )
    if resp.get("success"):
        return f"Map series created in layout '{layout_name}'."
    return f"Error creating map series: {resp.get('message') or resp.get('error')}"


def export_map_series(
    layout_name: str,
    output_path: str,
    format_type: str = "PDF",
    resolution_dpi: int = 300,
    ctx: Context = None,
) -> str:
    """
    Exports a configured map series.
    """
    if ctx:
        ctx.info(f"Exporting map series '{layout_name}'...")
    resp = client.send_command(
        "export_map_series",
        {
            "layout_name": layout_name,
            "output_path": output_path,
            "format": format_type,
            "resolution": resolution_dpi,
        },
        timeout_ms=120000,
        retries=0,
    )
    if resp.get("success"):
        return f"Map series '{layout_name}' exported to '{output_path}'."
    return f"Error exporting map series: {resp.get('message') or resp.get('error')}"


def add_dynamic_text(
    layout_name: str,
    text: str,
    x: float = 0.5,
    y: float = 0.5,
    width: float = 4.0,
    height: float = 0.5,
    element_name: str = "MCP Dynamic Text",
    ctx: Context = None,
) -> str:
    """
    Adds a text element to a layout. ArcGIS dynamic text tags are accepted.
    """
    if ctx:
        ctx.info(f"Adding dynamic text to layout '{layout_name}'...")
    resp = client.send_command(
        "add_dynamic_text",
        {
            "layout_name": layout_name,
            "text": text,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "element_name": element_name,
        },
        timeout_ms=30000,
    )
    if resp.get("success"):
        return f"Dynamic text added to '{layout_name}'."
    return f"Error adding dynamic text: {resp.get('message') or resp.get('error')}"


def update_layout_element(
    layout_name: str,
    element_name: str,
    text: str | None = None,
    visible: bool | None = None,
    ctx: Context = None,
) -> str:
    """
    Updates a layout element by name.
    """
    if ctx:
        ctx.info(f"Updating layout element '{element_name}'...")
    params = {"layout_name": layout_name, "element_name": element_name}
    if text is not None:
        params["text"] = text
    if visible is not None:
        params["visible"] = visible
    resp = client.send_command("update_layout_element", params, timeout_ms=30000)
    if resp.get("success"):
        return f"Layout element '{element_name}' updated."
    return f"Error updating layout element: {resp.get('message') or resp.get('error')}"
