from mcp.server.fastmcp import FastMCP, Context
import tools
import resources
import prompts

# Initialize FastMCP Server
mcp = FastMCP("arcgis-mcp")

# =====================================================================
# 0. IPC CORE AND PROJECT TOOLS
# =====================================================================


@mcp.tool()
def health_check(ctx: Context = None) -> str:
    """
    Checks MCP/Add-in/ArcGIS Pro pipe health and active project state.
    """
    return tools.health_check(ctx)


@mcp.tool()
def get_capabilities(ctx: Context = None) -> str:
    """
    Lists available Add-in command capabilities.
    """
    return tools.get_capabilities(ctx)


@mcp.tool()
def list_maps(ctx: Context = None) -> str:
    """
    Lists maps in the current ArcGIS Pro project.
    """
    return tools.list_maps(ctx)


@mcp.tool()
def open_map(map_name: str, ctx: Context = None) -> str:
    """
    Opens a map in ArcGIS Pro by name.
    """
    return tools.open_map(map_name, ctx)


@mcp.tool()
def save_project_as(
    output_path: str, overwrite: bool = False, ctx: Context = None
) -> str:
    """
    Saves the current ArcGIS Pro project to a new APRX path.
    """
    return tools.save_project_as(output_path, overwrite, ctx)


@mcp.tool()
def list_project_items(ctx: Context = None) -> str:
    """
    Lists main project items in the current ArcGIS Pro project.
    """
    return tools.list_project_items(ctx)


@mcp.tool()
def list_bookmarks(map_name: str = "", ctx: Context = None) -> str:
    """
    Lists bookmarks for the active map or a named map.
    """
    return tools.list_bookmarks(map_name, ctx)


# =====================================================================
# 1. MAP CONTROL TOOLS
# =====================================================================


@mcp.tool()
def get_active_map(ctx: Context = None) -> str:
    """
    Returns the name of the active map and scene view in ArcGIS Pro.
    """
    return tools.get_active_map(ctx)


@mcp.tool()
def list_layers(include_hidden: bool = True, ctx: Context = None) -> str:
    """
    Lists all layers in the active map, showing their names, types, visibility, and total features.
    """
    return tools.list_layers(include_hidden, ctx)


@mcp.tool()
def zoom_to_layer(layer_name: str, ctx: Context = None) -> str:
    """
    Zooms the active map view to the spatial extent of a specific layer by name.
    """
    return tools.zoom_to_layer(layer_name, ctx)


@mcp.tool()
def toggle_layer_visibility(layer_name: str, visible: bool, ctx: Context = None) -> str:
    """
    Toggles the visibility of a layer in the active map by name.
    """
    return tools.toggle_layer_visibility(layer_name, visible, ctx)


@mcp.tool()
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
    return tools.set_map_extent(xmin, ymin, xmax, ymax, wkid, ctx)


@mcp.tool()
def add_layer_to_map(data_path: str, layer_name: str = "", ctx: Context = None) -> str:
    """
    Adds a dataset, layer file, or service URL to the active map.
    """
    return tools.add_layer_to_map(data_path, layer_name, ctx)


@mcp.tool()
def set_layer_transparency(
    layer_name: str, transparency: float, ctx: Context = None
) -> str:
    """
    Sets layer transparency from 0 to 100.
    """
    return tools.set_layer_transparency(layer_name, transparency, ctx)


@mcp.tool()
def set_definition_query(layer_name: str, sql_filter: str, ctx: Context = None) -> str:
    """
    Sets or clears a definition query on a feature layer.
    """
    return tools.set_definition_query(layer_name, sql_filter, ctx)


@mcp.tool()
def clear_selection(layer_name: str = "", ctx: Context = None) -> str:
    """
    Clears selection in one feature layer or in the whole active map.
    """
    return tools.clear_selection(layer_name, ctx)


@mcp.tool()
def save_project(ctx: Context = None) -> str:
    """
    Saves the current ArcGIS Pro project.
    """
    return tools.save_project(ctx)


# =====================================================================
# 2. DATA AND QUERY TOOLS
# =====================================================================


@mcp.tool()
def count_features(layer_name: str, sql_filter: str = "", ctx: Context = None) -> str:
    """
    Counts the number of features in a specified layer.
    Allows an optional SQL filter (definition query format, e.g., "POPULATION > 100000").
    """
    return tools.count_features(layer_name, sql_filter, ctx)


@mcp.tool()
def select_features(
    layer_name: str,
    sql_filter: str,
    selection_combination: str = "NEW",
    ctx: Context = None,
) -> str:
    """
    Selects features in a specified layer using a SQL attribute query.
    selection_combination can be: "NEW", "ADD", "REMOVE", "SUBTRACT", "XOR".
    """
    return tools.select_features(layer_name, sql_filter, selection_combination, ctx)


@mcp.tool()
def get_selected_features(
    layer_name: str, max_features: int = 100, ctx: Context = None
) -> str:
    """
    Retrieves the attribute records for the currently selected features in a layer.
    Returns data as a formatted list (capped by max_features to prevent huge payloads).
    """
    return tools.get_selected_features(layer_name, max_features, ctx)


@mcp.tool()
def get_layer_fields(layer_name: str, ctx: Context = None) -> str:
    """
    Gets the schema/fields of a layer, listing names, aliases, and data types of all attributes.
    """
    return tools.get_layer_fields(layer_name, ctx)


# =====================================================================
# 2B. SYMBOLOGY AND LABELING TOOLS
# =====================================================================


@mcp.tool()
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
    return tools.apply_graduated_symbology(
        layer_name, field_name, break_count, classification_method, color_ramp, ctx
    )


@mcp.tool()
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
    return tools.apply_unique_value_symbology(
        layer_name, field_name, color_ramp, values_limit, ctx
    )


@mcp.tool()
def apply_symbology_from_layer(
    target_layer: str, symbology_layer: str, ctx: Context = None
) -> str:
    """
    Applies symbology from an existing layer or .lyrx file.
    """
    return tools.apply_symbology_from_layer(target_layer, symbology_layer, ctx)


@mcp.tool()
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
    return tools.label_layer(layer_name, field_name, visible, expression_engine, ctx)


@mcp.tool()
def get_layer_symbology(layer_name: str, ctx: Context = None) -> str:
    """
    Returns renderer metadata for a layer.
    """
    return tools.get_layer_symbology(layer_name, ctx)


@mcp.tool()
def update_class_breaks(
    layer_name: str,
    field_name: str,
    break_count: int = 5,
    classification_method: str = "NaturalBreaks",
    color_ramp: str = "Yellow-Orange-Red",
    ctx: Context = None,
) -> str:
    """
    Rebuilds graduated class breaks for a feature layer.
    """
    return tools.update_class_breaks(
        layer_name, field_name, break_count, classification_method, color_ramp, ctx
    )


@mcp.tool()
def apply_raster_colorizer(
    raster_layer: str,
    symbology_layer: str = "",
    color_ramp: str = "Default",
    ctx: Context = None,
) -> str:
    """
    Applies raster symbology from a layer file or existing layer.
    """
    return tools.apply_raster_colorizer(raster_layer, symbology_layer, color_ramp, ctx)


# =====================================================================
# 2C. LAYER IO AND EDITING TOOLS
# =====================================================================


@mcp.tool()
def save_layer_file(layer_name: str, output_path: str, ctx: Context = None) -> str:
    """
    Saves an active-map layer to a .lyrx file.
    """
    return tools.save_layer_file(layer_name, output_path, ctx)


@mcp.tool()
def load_layer_file(layer_file_path: str, ctx: Context = None) -> str:
    """
    Loads a .lyrx file into the active map.
    """
    return tools.load_layer_file(layer_file_path, ctx)


@mcp.tool()
def export_layer(
    layer_name: str, output_path: str, where_clause: str = "", ctx: Context = None
) -> str:
    """
    Exports a feature layer to a dataset path.
    """
    return tools.export_layer(layer_name, output_path, where_clause, ctx)


@mcp.tool()
def remove_layer(layer_name: str, ctx: Context = None) -> str:
    """
    Removes a layer from the active map.
    """
    return tools.remove_layer(layer_name, ctx)


@mcp.tool()
def update_attributes(
    layer_name: str, object_id: int, attributes: dict, ctx: Context = None
) -> str:
    """
    Updates attributes for a feature by ObjectID.
    """
    return tools.update_attributes(layer_name, object_id, attributes, ctx)


@mcp.tool()
def create_feature(
    layer_name: str,
    x: float,
    y: float,
    wkid: int = 4326,
    attributes: dict | None = None,
    ctx: Context = None,
) -> str:
    """
    Creates a point feature in a feature layer.
    """
    return tools.create_feature(layer_name, x, y, wkid, attributes or {}, ctx)


@mcp.tool()
def delete_selected_features(layer_name: str, ctx: Context = None) -> str:
    """
    Deletes selected features from a feature layer.
    """
    return tools.delete_selected_features(layer_name, ctx)


@mcp.tool()
def undo_last_edit(ctx: Context = None) -> str:
    """
    Undoes the last MCP edit operation.
    """
    return tools.undo_last_edit(ctx)


# =====================================================================
# 3. GEOPROCESSING TOOLS
# =====================================================================


@mcp.tool()
def run_gp_tool(tool_name: str, parameters: list, ctx: Context = None) -> str:
    """
    Executes any ArcGIS Pro geoprocessing tool by name with list of parameters.
    Example: tool_name="Buffer_analysis", parameters=["Roads", "Roads_Buffer", "100 Meters"]
    """
    return tools.run_gp_tool(tool_name, parameters, ctx)


@mcp.tool()
def buffer_analysis(
    input_features: str,
    output_feature_class: str,
    buffer_distance: str,
    ctx: Context = None,
) -> str:
    """
    Creates buffer polygons around input features to a specified distance.
    Example: buffer_distance="100 Meters" or "10 Feet".
    """
    return tools.buffer_analysis(
        input_features, output_feature_class, buffer_distance, ctx
    )


@mcp.tool()
def clip_analysis(
    input_features: str,
    clip_features: str,
    output_feature_class: str,
    ctx: Context = None,
) -> str:
    """
    Clips/extracts input features that overlay clip features.
    """
    return tools.clip_analysis(input_features, clip_features, output_feature_class, ctx)


@mcp.tool()
def spatial_join(
    target_features: str,
    join_features: str,
    output_feature_class: str,
    join_operation: str = "JOIN_ONE_TO_ONE",
    join_type: str = "KEEP_ALL",
    match_option: str = "INTERSECT",
    ctx: Context = None,
) -> str:
    """
    Joins attributes from one feature class to another based on spatial relationship.
    join_operation: "JOIN_ONE_TO_ONE" or "JOIN_ONE_TO_MANY"
    match_option: "INTERSECT", "WITHIN", "CONTAINS", "CLOSEST", etc.
    """
    return tools.spatial_join(
        target_features,
        join_features,
        output_feature_class,
        join_operation,
        join_type,
        match_option,
        ctx,
    )


# =====================================================================
# 3B. GEODATABASE TOOLS
# =====================================================================


@mcp.tool()
def list_feature_classes(workspace_path: str, ctx: Context = None) -> str:
    """
    Lists feature classes in a file geodatabase.
    """
    return tools.list_feature_classes(workspace_path, ctx)


@mcp.tool()
def list_domains(workspace_path: str, ctx: Context = None) -> str:
    """
    Lists geodatabase domains.
    """
    return tools.list_domains(workspace_path, ctx)


@mcp.tool()
def create_domain(
    workspace_path: str,
    domain_name: str,
    field_type: str = "TEXT",
    domain_type: str = "CODED",
    description: str = "",
    ctx: Context = None,
) -> str:
    """
    Creates a geodatabase domain.
    """
    return tools.create_domain(
        workspace_path, domain_name, field_type, domain_type, description, ctx
    )


@mcp.tool()
def describe_dataset(dataset_path: str, ctx: Context = None) -> str:
    """
    Describes an active-map layer or geodatabase dataset.
    """
    return tools.describe_dataset(dataset_path, ctx)


# =====================================================================
# 3C. PORTAL AND FEATURE SERVICE TOOLS
# =====================================================================


@mcp.tool()
def connect_portal(portal_url: str, token: str = "", ctx: Context = None) -> str:
    """
    Sets the MCP REST portal URL and optional token.
    """
    return tools.connect_portal(portal_url, token, ctx)


@mcp.tool()
def get_active_portal(ctx: Context = None) -> str:
    """
    Returns the active ArcGIS Pro portal and MCP REST portal.
    """
    return tools.get_active_portal(ctx)


@mcp.tool()
def search_portal_items(
    query: str,
    max_items: int = 10,
    portal_url: str = "",
    token: str = "",
    ctx: Context = None,
) -> str:
    """
    Searches ArcGIS Online or ArcGIS Enterprise portal items.
    """
    return tools.search_portal_items(query, max_items, portal_url, token, ctx)


@mcp.tool()
def describe_portal_item(
    item_id: str, portal_url: str = "", token: str = "", ctx: Context = None
) -> str:
    """
    Describes an ArcGIS portal item.
    """
    return tools.describe_portal_item(item_id, portal_url, token, ctx)


@mcp.tool()
def publish_web_layer(
    service_definition_path: str,
    server_connection: str = "My Hosted Services",
    service_name: str = "",
    folder_type: str = "",
    folder: str = "",
    startup_type: str = "",
    override_definition: str = "",
    my_contents: str = "",
    public_share: str = "",
    organization: str = "",
    groups: str = "",
    ctx: Context = None,
) -> str:
    """
    Publishes an ArcGIS .sd file or stages and publishes an .sddraft file.
    """
    return tools.publish_web_layer(
        service_definition_path,
        server_connection,
        service_name,
        folder_type,
        folder,
        startup_type,
        override_definition,
        my_contents,
        public_share,
        organization,
        groups,
        ctx,
    )


@mcp.tool()
def stage_service_definition(
    service_draft_path: str,
    output_service_definition_path: str = "",
    ctx: Context = None,
) -> str:
    """
    Stages an ArcGIS service definition draft (.sddraft) into a service definition (.sd).
    """
    return tools.stage_service_definition(
        service_draft_path,
        output_service_definition_path,
        ctx,
    )


@mcp.tool()
def get_service_layers(service_url: str, token: str = "", ctx: Context = None) -> str:
    """
    Lists layers and tables exposed by a REST service.
    """
    return tools.get_service_layers(service_url, token, ctx)


@mcp.tool()
def get_layer_schema(layer_url: str, token: str = "", ctx: Context = None) -> str:
    """
    Returns schema metadata for a REST feature layer.
    """
    return tools.get_layer_schema(layer_url, token, ctx)


@mcp.tool()
def query_feature_service(
    layer_url: str,
    where: str = "1=1",
    out_fields: str = "*",
    max_records: int = 100,
    token: str = "",
    ctx: Context = None,
) -> str:
    """
    Queries a REST feature layer.
    """
    return tools.query_feature_service(
        layer_url, where, out_fields, max_records, token, ctx
    )


@mcp.tool()
def export_service_geojson(
    layer_url: str,
    output_path: str,
    where: str = "1=1",
    out_fields: str = "*",
    max_records: int = 2000,
    token: str = "",
    ctx: Context = None,
) -> str:
    """
    Exports a REST feature layer query result to GeoJSON.
    """
    return tools.export_service_geojson(
        layer_url, output_path, where, out_fields, max_records, token, ctx
    )


# =====================================================================
# 4. LAYOUT AND PRINT TOOLS
# =====================================================================


@mcp.tool()
def list_layouts(ctx: Context = None) -> str:
    """
    Lists all the layouts (print layouts/map layouts) defined in the current ArcGIS Pro project.
    """
    return tools.list_layouts(ctx)


@mcp.tool()
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
    return tools.export_layout(
        layout_name, output_path, format_type, resolution_dpi, ctx
    )


@mcp.tool()
def create_basic_layout(
    layout_name: str,
    title: str,
    page_width: float = 11.0,
    page_height: float = 8.5,
    ctx: Context = None,
) -> str:
    """
    Creates a basic layout from the active map with map frame and cartographic surrounds.
    """
    return tools.create_basic_layout(layout_name, title, page_width, page_height, ctx)


@mcp.tool()
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
    return tools.export_active_map(
        output_path, format_type, width, height, resolution_dpi, ctx
    )


@mcp.tool()
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
    return tools.create_map_series(
        layout_name, map_frame_name, index_layer_name, name_field, ctx
    )


@mcp.tool()
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
    return tools.export_map_series(
        layout_name, output_path, format_type, resolution_dpi, ctx
    )


@mcp.tool()
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
    return tools.add_dynamic_text(
        layout_name, text, x, y, width, height, element_name, ctx
    )


@mcp.tool()
def update_layout_element(
    layout_name: str,
    element_name: str,
    text: str | None = None,
    visible: bool | None = None,
    ctx: Context = None,
) -> str:
    """
    Updates text or visibility of a layout element.
    """
    return tools.update_layout_element(layout_name, element_name, text, visible, ctx)


# =====================================================================
# 4B. DOCUMENTATION TOOLS
# =====================================================================


@mcp.tool()
def search_arcgis_docs(query: str, max_results: int = 10, ctx: Context = None) -> str:
    """
    Searches local SDK docs and returns official online documentation links.
    """
    return tools.search_arcgis_docs(query, max_results, ctx)


# =====================================================================
# 5. SDK RESOURCES
# =====================================================================


@mcp.resource("config://sdk/arcpy-reference")
def get_arcpy_resource() -> str:
    """
    Returns reference documentation and code snippets for Esri ArcPy scripting.
    """
    return resources.get_arcpy_reference()


@mcp.resource("config://sdk/addin-csharp-reference")
def get_addin_csharp_resource() -> str:
    """
    Returns reference documentation and code snippets for ArcGIS Pro SDK Add-Ins (C#).
    """
    return resources.get_addin_csharp_reference()


# =====================================================================
# 6. CODING PROMPTS
# =====================================================================


@mcp.prompt()
def generate_arcpy_script(task_description: str) -> str:
    """
    Generates a prompt template for writing a high-quality ArcPy script.
    """
    return prompts.arcpy_script(task_description)


@mcp.prompt()
def generate_addin_button(button_action: str) -> str:
    """
    Generates a prompt template for building a custom C# Add-In button.
    """
    return prompts.addin_button(button_action)


# =====================================================================
# RUN SERVER
# =====================================================================
if __name__ == "__main__":
    mcp.run()
