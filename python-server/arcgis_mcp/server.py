from mcp.server.fastmcp import Context, FastMCP

from . import prompts, resources, tools

# Initialize FastMCP Server
mcp = FastMCP("arcgis-mcp")

# =====================================================================
# 0. IPC CORE AND PROJECT TOOLS
# =====================================================================


@mcp.tool()
def health_check(ctx: Context = None) -> str:
    """Checks MCP/Add-in/ArcGIS Pro pipe health and active project state."""
    return tools.health_check(ctx)


@mcp.tool()
def get_capabilities(ctx: Context = None) -> str:
    """Lists available Add-in command capabilities."""
    return tools.get_capabilities(ctx)


@mcp.tool()
def list_maps(ctx: Context = None) -> str:
    """Lists maps in the current ArcGIS Pro project."""
    return tools.list_maps(ctx)


@mcp.tool()
def open_map(map_name: str, ctx: Context = None) -> str:
    """Opens a map in ArcGIS Pro by name."""
    return tools.open_map(map_name, ctx)


@mcp.tool()
def save_project_as(
    output_path: str, overwrite: bool = False, ctx: Context = None
) -> str:
    """Saves the current ArcGIS Pro project to a new APRX path."""
    return tools.save_project_as(output_path, overwrite, ctx)


@mcp.tool()
def list_project_items(ctx: Context = None) -> str:
    """Lists main project items in the current ArcGIS Pro project."""
    return tools.list_project_items(ctx)


@mcp.tool()
def list_bookmarks(map_name: str = "", ctx: Context = None) -> str:
    """Lists bookmarks for the active map or a named map."""
    return tools.list_bookmarks(map_name, ctx)


# =====================================================================
# 1. MAP CONTROL TOOLS
# =====================================================================


@mcp.tool()
def get_active_map(ctx: Context = None) -> str:
    """Returns the name of the active map and scene view in ArcGIS Pro."""
    return tools.get_active_map(ctx)


@mcp.tool()
def list_layers(include_hidden: bool = True, ctx: Context = None) -> str:
    """Lists all layers in the active map, showing names, types, visibility, and total features."""
    return tools.list_layers(include_hidden, ctx)


@mcp.tool()
def zoom_to_layer(layer_name: str, ctx: Context = None) -> str:
    """Zooms the active map view to the spatial extent of a specific layer by name."""
    return tools.zoom_to_layer(layer_name, ctx)


@mcp.tool()
def toggle_layer_visibility(layer_name: str, visible: bool, ctx: Context = None) -> str:
    """Toggles the visibility of a layer in the active map by name."""
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
    """Sets the active map view extent to the specified bounding box coordinates (default WKID 4326)."""
    return tools.set_map_extent(xmin, ymin, xmax, ymax, wkid, ctx)


@mcp.tool()
def add_layer_to_map(data_path: str, layer_name: str = "", ctx: Context = None) -> str:
    """Adds a dataset, layer file, or service URL to the active map."""
    return tools.add_layer_to_map(data_path, layer_name, ctx)


@mcp.tool()
def create_group_layer(
    group_name: str, layer_names: list | None = None, ctx: Context = None
) -> str:
    """Creates a group layer in the active map, optionally moving existing layers into it."""
    return tools.create_group_layer(group_name, layer_names, ctx)


@mcp.tool()
def add_layer_to_group(group_name: str, layer_names: list, ctx: Context = None) -> str:
    """Moves existing layers into an existing group layer in the active map."""
    return tools.add_layer_to_group(group_name, layer_names, ctx)


@mcp.tool()
def set_layer_transparency(
    layer_name: str, transparency: float, ctx: Context = None
) -> str:
    """Sets layer transparency from 0 to 100."""
    return tools.set_layer_transparency(layer_name, transparency, ctx)


@mcp.tool()
def set_definition_query(layer_name: str, sql_filter: str, ctx: Context = None) -> str:
    """Sets or clears a definition query on a feature layer."""
    return tools.set_definition_query(layer_name, sql_filter, ctx)


@mcp.tool()
def clear_selection(layer_name: str = "", ctx: Context = None) -> str:
    """Clears selection in one feature layer or in the whole active map."""
    return tools.clear_selection(layer_name, ctx)


@mcp.tool()
def save_project(ctx: Context = None) -> str:
    """Saves the current ArcGIS Pro project."""
    return tools.save_project(ctx)


# =====================================================================
# 2. DATA AND QUERY TOOLS
# =====================================================================


@mcp.tool()
def count_features(layer_name: str, sql_filter: str = "", ctx: Context = None) -> str:
    """Counts the number of features in a specified layer. Optional SQL filter (e.g. "POPULATION > 100000")."""
    return tools.count_features(layer_name, sql_filter, ctx)


@mcp.tool()
def select_features(
    layer_name: str,
    sql_filter: str,
    selection_combination: str = "NEW",
    ctx: Context = None,
) -> str:
    """Selects features in a layer using a SQL attribute query. combination: NEW, ADD, REMOVE, SUBTRACT, XOR."""
    return tools.select_features(layer_name, sql_filter, selection_combination, ctx)


@mcp.tool()
def get_selected_features(
    layer_name: str, max_features: int = 100, ctx: Context = None
) -> str:
    """Retrieves the attribute records for the currently selected features in a layer."""
    return tools.get_selected_features(layer_name, max_features, ctx)


@mcp.tool()
def get_layer_fields(layer_name: str, ctx: Context = None) -> str:
    """Gets the schema/fields of a layer, listing names, aliases, and data types of all attributes."""
    return tools.get_layer_fields(layer_name, ctx)


@mcp.tool()
def query_layer(
    layer_name: str,
    where_clause: str = "1=1",
    fields: str = "*",
    limit: int = 100,
    include_geometry: bool = False,
    ctx: Context = None,
) -> str:
    """Queries attribute rows from an active-map feature layer."""
    return tools.query_layer(
        layer_name, where_clause, fields, limit, include_geometry, ctx
    )


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
    """Applies graduated color symbology to a feature layer."""
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
    """Applies unique value symbology to a feature layer."""
    return tools.apply_unique_value_symbology(
        layer_name, field_name, color_ramp, values_limit, ctx
    )


@mcp.tool()
def apply_symbology_from_layer(
    target_layer: str, symbology_layer: str, ctx: Context = None
) -> str:
    """Applies symbology from an existing layer or .lyrx file."""
    return tools.apply_symbology_from_layer(target_layer, symbology_layer, ctx)


@mcp.tool()
def set_layer_symbol(
    layer_name: str,
    r: int,
    g: int,
    b: int,
    width: float = 0,
    alpha: float = 100,
    ctx: Context = None,
) -> str:
    """Sets the color (RGB 0-255) and optionally the width of a feature layer's simple renderer via direct CIM manipulation."""
    return tools.set_layer_symbol(layer_name, r, g, b, width, alpha, ctx)


@mcp.tool()
def label_layer(
    layer_name: str,
    field_name: str,
    visible: bool = True,
    expression_engine: str = "Arcade",
    halo_size: float = 0,
    halo_color: str = "#FFFFFF",
    ctx: Context = None,
) -> str:
    """Enables labels on a feature layer using a field-based expression. Optionally applies a text halo."""
    return tools.label_layer(
        layer_name, field_name, visible, expression_engine, halo_size, halo_color, ctx
    )


@mcp.tool()
def get_layer_symbology(layer_name: str, ctx: Context = None) -> str:
    """Returns renderer metadata for a layer."""
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
    """Rebuilds graduated class breaks for a feature layer."""
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
    """Applies raster symbology from a layer file or existing layer."""
    return tools.apply_raster_colorizer(raster_layer, symbology_layer, color_ramp, ctx)


# =====================================================================
# 2C. LAYER IO AND EDITING TOOLS
# =====================================================================


@mcp.tool()
def save_layer_file(layer_name: str, output_path: str, ctx: Context = None) -> str:
    """Saves an active-map layer to a .lyrx file."""
    return tools.save_layer_file(layer_name, output_path, ctx)


@mcp.tool()
def load_layer_file(layer_file_path: str, ctx: Context = None) -> str:
    """Loads a .lyrx file into the active map."""
    return tools.load_layer_file(layer_file_path, ctx)


@mcp.tool()
def export_layer(
    layer_name: str, output_path: str, where_clause: str = "", ctx: Context = None
) -> str:
    """Exports a feature layer to a dataset path."""
    return tools.export_layer(layer_name, output_path, where_clause, ctx)


@mcp.tool()
def remove_layer(layer_name: str, ctx: Context = None) -> str:
    """Removes a layer from the active map."""
    return tools.remove_layer(layer_name, ctx)


@mcp.tool()
def update_attributes(
    layer_name: str, object_id: int, attributes: dict, ctx: Context = None
) -> str:
    """Updates attributes for a feature by ObjectID."""
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
    """Creates a point feature in a feature layer."""
    return tools.create_feature(layer_name, x, y, wkid, attributes or {}, ctx)


@mcp.tool()
def delete_selected_features(layer_name: str, ctx: Context = None) -> str:
    """Deletes selected features from a feature layer."""
    return tools.delete_selected_features(layer_name, ctx)


@mcp.tool()
def undo_last_edit(ctx: Context = None) -> str:
    """Undoes the last MCP edit operation."""
    return tools.undo_last_edit(ctx)


# =====================================================================
# 3. GEOPROCESSING TOOLS
# =====================================================================


@mcp.tool()
def run_gp_tool(
    tool_name: str,
    parameters: list,
    add_outputs_to_map: bool = False,
    allow_delete: bool = False,
    ctx: Context = None,
) -> str:
    """Executes any ArcGIS Pro geoprocessing tool by name with list of parameters.
    Example: tool_name="Buffer_analysis", parameters=["Roads", "Roads_Buffer", "100 Meters"]"""
    return tools.run_gp_tool(
        tool_name, parameters, ctx, add_outputs_to_map, allow_delete
    )


@mcp.tool()
def buffer_analysis(
    input_features: str,
    output_feature_class: str,
    buffer_distance: str,
    ctx: Context = None,
) -> str:
    """Creates buffer polygons around input features to a specified distance. Example: "100 Meters"."""
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
    """Clips/extracts input features that overlay clip features."""
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
    """Joins attributes from one feature class to another based on spatial relationship.
    match_option: INTERSECT, WITHIN, CONTAINS, CLOSEST, etc."""
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
    """Lists feature classes in a file geodatabase."""
    return tools.list_feature_classes(workspace_path, ctx)


@mcp.tool()
def list_domains(workspace_path: str, ctx: Context = None) -> str:
    """Lists geodatabase domains."""
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
    """Creates a geodatabase domain."""
    return tools.create_domain(
        workspace_path, domain_name, field_type, domain_type, description, ctx
    )


@mcp.tool()
def describe_dataset(dataset_path: str, ctx: Context = None) -> str:
    """Describes an active-map layer or geodatabase dataset."""
    return tools.describe_dataset(dataset_path, ctx)


# =====================================================================
# 3C. PORTAL AND FEATURE SERVICE TOOLS
# =====================================================================


@mcp.tool()
def connect_portal(portal_url: str, token: str = "", ctx: Context = None) -> str:
    """Sets the MCP REST portal URL and optional token."""
    return tools.connect_portal(portal_url, token, ctx)


@mcp.tool()
def get_active_portal(ctx: Context = None) -> str:
    """Returns the active ArcGIS Pro portal and MCP REST portal."""
    return tools.get_active_portal(ctx)


@mcp.tool()
def search_portal_items(
    query: str,
    max_items: int = 10,
    portal_url: str = "",
    token: str = "",
    ctx: Context = None,
) -> str:
    """Searches ArcGIS Online or ArcGIS Enterprise portal items."""
    return tools.search_portal_items(query, max_items, portal_url, token, ctx)


@mcp.tool()
def describe_portal_item(
    item_id: str, portal_url: str = "", token: str = "", ctx: Context = None
) -> str:
    """Describes an ArcGIS portal item."""
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
    """Publishes an ArcGIS .sd file or stages and publishes an .sddraft file."""
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
    """Stages an ArcGIS service definition draft (.sddraft) into a service definition (.sd)."""
    return tools.stage_service_definition(
        service_draft_path,
        output_service_definition_path,
        ctx,
    )


@mcp.tool()
def get_service_layers(service_url: str, token: str = "", ctx: Context = None) -> str:
    """Lists layers and tables exposed by a REST service."""
    return tools.get_service_layers(service_url, token, ctx)


@mcp.tool()
def get_layer_schema(layer_url: str, token: str = "", ctx: Context = None) -> str:
    """Returns schema metadata for a REST feature layer."""
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
    """Queries a REST feature layer."""
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
    """Exports a REST feature layer query result to GeoJSON."""
    return tools.export_service_geojson(
        layer_url, output_path, where, out_fields, max_records, token, ctx
    )


# =====================================================================
# 4. LAYOUT AND PRINT TOOLS
# =====================================================================


@mcp.tool()
def list_layouts(ctx: Context = None) -> str:
    """Lists all the layouts (print layouts/map layouts) defined in the current ArcGIS Pro project."""
    return tools.list_layouts(ctx)


@mcp.tool()
def export_layout(
    layout_name: str,
    output_path: str,
    format_type: str = "PDF",
    resolution_dpi: int = 300,
    ctx: Context = None,
) -> str:
    """Exports a print layout to the specified output file path. format_type: PDF, PNG, JPEG. Resolution in DPI."""
    return tools.export_layout(
        layout_name, output_path, format_type, resolution_dpi, ctx
    )


@mcp.tool()
def export_all_layouts(
    output_directory: str,
    format_type: str = "PDF",
    resolution_dpi: int = 300,
    include_map_series: bool = True,
    ctx: Context = None,
) -> str:
    """Exports every layout in the active ArcGIS Pro project to one output directory."""
    return tools.export_all_layouts(
        output_directory, format_type, resolution_dpi, include_map_series, ctx
    )


@mcp.tool()
def create_basic_layout(
    layout_name: str,
    title: str,
    page_width: float = 11.0,
    page_height: float = 8.5,
    ctx: Context = None,
) -> str:
    """Creates a basic layout from the active map with map frame and cartographic surrounds."""
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
    """Exports the active map view to an image file."""
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
    """Creates a spatial map series for a layout."""
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
    """Exports a configured map series."""
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
    """Adds a text element to a layout. ArcGIS dynamic text tags are accepted."""
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
    """Updates text or visibility of a layout element."""
    return tools.update_layout_element(layout_name, element_name, text, visible, ctx)


# =====================================================================
# 4B. DOCUMENTATION TOOLS
# =====================================================================


@mcp.tool()
def search_arcgis_docs(query: str, max_results: int = 10, ctx: Context = None) -> str:
    """Searches local SDK docs and returns official online documentation links."""
    return tools.search_arcgis_docs(query, max_results, ctx)


# =====================================================================
# 5. SDK RESOURCES
# =====================================================================


@mcp.resource("config://sdk/arcpy-reference")
def get_arcpy_resource() -> str:
    """Returns reference documentation and code snippets for Esri ArcPy scripting."""
    return resources.get_arcpy_reference()


@mcp.resource("config://sdk/addin-csharp-reference")
def get_addin_csharp_resource() -> str:
    """Returns reference documentation and code snippets for ArcGIS Pro SDK Add-Ins (C#)."""
    return resources.get_addin_csharp_reference()


# =====================================================================
# 6. CODING PROMPTS
# =====================================================================


@mcp.prompt()
def generate_arcpy_script(task_description: str) -> str:
    """Generates a prompt template for writing a high-quality ArcPy script."""
    return prompts.arcpy_script(task_description)


@mcp.prompt()
def generate_addin_button(button_action: str) -> str:
    """Generates a prompt template for building a custom C# Add-In button."""
    return prompts.addin_button(button_action)


# =====================================================================
# 7. CONVERSION TOOLS
# =====================================================================


@mcp.tool()
def excel_to_table(
    input_excel_file: str,
    output_table: str,
    sheet: str = "",
    cell_range: str = "",
    ctx: Context = None,
) -> str:
    """Imports an Excel workbook (.xlsx/.xls) into a geodatabase table or dBASE."""
    return tools.excel_to_table(input_excel_file, output_table, sheet, cell_range, ctx)


@mcp.tool()
def table_to_excel(
    input_table: str,
    output_excel_file: str,
    use_field_alias_as_header: bool = False,
    use_domain_and_subtype_description: bool = False,
    ctx: Context = None,
) -> str:
    """Exports a table or feature class attribute table to Excel (.xlsx)."""
    return tools.table_to_excel(
        input_table,
        output_excel_file,
        use_field_alias_as_header,
        use_domain_and_subtype_description,
        ctx,
    )


@mcp.tool()
def kml_to_layer(input_kml: str, output_folder: str, ctx: Context = None) -> str:
    """Converts a KML/KMZ file into a feature class and layer file in a file geodatabase."""
    return tools.kml_to_layer(input_kml, output_folder, ctx)


@mcp.tool()
def layer_to_kml(
    layer: str, output_kmz: str, output_scale: int = 0, ctx: Context = None
) -> str:
    """Converts a map layer, layer file or feature class to a KMZ file."""
    return tools.layer_to_kml(layer, output_kmz, output_scale, ctx)


@mcp.tool()
def features_to_json(
    in_features: str,
    out_json_file: str,
    format_json: bool = False,
    include_geometry: bool = True,
    ctx: Context = None,
) -> str:
    """Converts features to ArcGIS JSON or GeoJSON."""
    return tools.features_to_json(
        in_features, out_json_file, format_json, include_geometry, ctx
    )


@mcp.tool()
def json_to_features(
    in_json_file: str,
    out_features: str,
    geometry_type: str = "",
    ctx: Context = None,
) -> str:
    """Creates a feature class from Esri JSON or GeoJSON."""
    return tools.json_to_features(in_json_file, out_features, geometry_type, ctx)


@mcp.tool()
def raster_to_polygon(
    in_raster: str,
    out_polygon_features: str,
    simplify: bool = True,
    raster_field: str = "Value",
    ctx: Context = None,
) -> str:
    """Converts a raster dataset to polygon features."""
    return tools.raster_to_polygon(
        in_raster, out_polygon_features, simplify, raster_field, ctx
    )


@mcp.tool()
def polygon_to_raster(
    in_features: str,
    value_field: str,
    out_raster_dataset: str,
    cell_assignment: str = "CELL_CENTER",
    priority_field: str = "",
    cellsize: str = "",
    ctx: Context = None,
) -> str:
    """Converts polygon features to a raster dataset."""
    return tools.polygon_to_raster(
        in_features,
        value_field,
        out_raster_dataset,
        cell_assignment,
        priority_field,
        cellsize,
        ctx,
    )


@mcp.tool()
def point_to_raster(
    in_features: str,
    value_field: str,
    out_raster_dataset: str,
    cell_assignment: str = "MOST_FREQUENT",
    priority_field: str = "",
    cellsize: str = "",
    ctx: Context = None,
) -> str:
    """Converts point features to a raster dataset."""
    return tools.point_to_raster(
        in_features,
        value_field,
        out_raster_dataset,
        cell_assignment,
        priority_field,
        cellsize,
        ctx,
    )


@mcp.tool()
def export_features(
    in_features: str,
    out_features: str,
    where_clause: str = "",
    use_field_alias_as_name: bool = False,
    ctx: Context = None,
) -> str:
    """Exports a feature class or layer to a new feature class (shapefile, file geodatabase, etc.)."""
    return tools.export_features(
        in_features, out_features, where_clause, use_field_alias_as_name, ctx
    )


@mcp.tool()
def export_table(
    in_table: str,
    out_table: str,
    where_clause: str = "",
    use_field_alias_as_name: bool = False,
    ctx: Context = None,
) -> str:
    """Exports a table or attribute table to a new standalone table."""
    return tools.export_table(
        in_table, out_table, where_clause, use_field_alias_as_name, ctx
    )


@mcp.tool()
def feature_class_to_shapefile(
    input_features: list, output_folder: str, ctx: Context = None
) -> str:
    """Converts one or more feature classes to shapefiles in a folder."""
    return tools.feature_class_to_shapefile(input_features, output_folder, ctx)


@mcp.tool()
def cad_to_geodatabase(
    input_cad: str,
    output_geodatabase: str,
    reference_scale: str = "",
    spatial_reference: str = "",
    ctx: Context = None,
) -> str:
    """Converts CAD data (.dwg/.dgn/.dxf) into feature classes in a geodatabase."""
    return tools.cad_to_geodatabase(
        input_cad, output_geodatabase, reference_scale, spatial_reference, ctx
    )


@mcp.tool()
def bim_to_geodatabase(
    input_bim: str,
    output_geodatabase: str,
    include_features: bool = True,
    spatial_reference: str = "",
    ctx: Context = None,
) -> str:
    """Converts Revit/BIM data (.rvt/.ifc/.dgn) into feature classes."""
    return tools.bim_to_geodatabase(
        input_bim, output_geodatabase, include_features, spatial_reference, ctx
    )


# =====================================================================
# 8. VECTOR ANALYSIS TOOLS
# =====================================================================


@mcp.tool()
def dissolve(
    in_features: str,
    out_feature_class: str,
    dissolve_fields: list | None = None,
    statistics_fields: list | None = None,
    multi_part: str = "MULTI_PART",
    unsplit_lines: str = "DISSOLVE_LINES",
    ctx: Context = None,
) -> str:
    """Aggregates features based on specified attributes."""
    return tools.dissolve(
        in_features,
        out_feature_class,
        dissolve_fields,
        statistics_fields,
        multi_part,
        unsplit_lines,
        ctx,
    )


@mcp.tool()
def intersect(
    in_features: list,
    out_feature_class: str,
    join_attributes: str = "ALL",
    cluster_tolerance: str = "",
    output_type: str = "INPUT",
    ctx: Context = None,
) -> str:
    """Computes the geometric intersection of feature classes. output_type: INPUT, LINE, POINT."""
    return tools.intersect(
        in_features,
        out_feature_class,
        join_attributes,
        cluster_tolerance,
        output_type,
        ctx,
    )


@mcp.tool()
def union(
    in_features: list,
    out_feature_class: str,
    join_attributes: str = "ALL",
    gaps: str = "GAPS",
    cluster_tolerance: str = "",
    ctx: Context = None,
) -> str:
    """Computes the geometric union of polygon feature classes."""
    return tools.union(
        in_features, out_feature_class, join_attributes, gaps, cluster_tolerance, ctx
    )


@mcp.tool()
def erase(
    in_features: str,
    erase_features: str,
    out_feature_class: str,
    cluster_tolerance: str = "",
    ctx: Context = None,
) -> str:
    """Removes features (and portions of features) that overlap the erase features."""
    return tools.erase(
        in_features, erase_features, out_feature_class, cluster_tolerance, ctx
    )


@mcp.tool()
def merge(inputs: list, output: str, field_map: str = "", ctx: Context = None) -> str:
    """Combines multiple input datasets into a new output dataset."""
    return tools.merge(inputs, output, field_map, ctx)


@mcp.tool()
def append(
    inputs: list,
    target: str,
    schema_type: str = "TEST",
    field_map: str = "",
    subtype: str = "",
    ctx: Context = None,
) -> str:
    """Appends multiple input datasets into an existing target dataset. schema_type: TEST or NO_TEST."""
    return tools.append(inputs, target, schema_type, field_map, subtype, ctx)


@mcp.tool()
def near(
    in_features: str,
    near_features: str,
    search_radius: str = "",
    location: bool = False,
    angle: bool = False,
    method: str = "PLANAR",
    ctx: Context = None,
) -> str:
    """Adds distance, location and angle from in_features to the nearest near_features."""
    return tools.near(
        in_features, near_features, search_radius, location, angle, method, ctx
    )


@mcp.tool()
def generate_near_table(
    in_features: str,
    near_features: list,
    out_table: str,
    search_radius: str = "",
    location: bool = False,
    angle: bool = False,
    closest: str = "ALL",
    closest_count: int = 1,
    method: str = "PLANAR",
    ctx: Context = None,
) -> str:
    """Produces a table of distances between input and near features."""
    return tools.generate_near_table(
        in_features,
        near_features,
        out_table,
        search_radius,
        location,
        angle,
        closest,
        closest_count,
        method,
        ctx,
    )


@mcp.tool()
def select_layer_by_location(
    in_layer: str,
    overlap_type: str = "INTERSECT",
    select_features: str = "",
    search_distance: str = "",
    selection_type: str = "NEW_SELECTION",
    invert_spatial_relationship: str = "NOT_INVERT",
    ctx: Context = None,
) -> str:
    """Selects features in a layer based on their spatial relationship to features in another layer."""
    return tools.select_layer_by_location(
        in_layer,
        overlap_type,
        select_features,
        search_distance,
        selection_type,
        invert_spatial_relationship,
        ctx,
    )


@mcp.tool()
def summary_statistics(
    in_table: str,
    out_table: str,
    statistics_fields: list,
    case_fields: list | None = None,
    ctx: Context = None,
) -> str:
    """Computes summary statistics for fields in a table."""
    return tools.summary_statistics(
        in_table, out_table, statistics_fields, case_fields, ctx
    )


@mcp.tool()
def frequency(
    in_table: str,
    out_table: str,
    frequency_fields: list,
    summary_fields: list | None = None,
    ctx: Context = None,
) -> str:
    """Reads a table and produces a new table containing unique field values and their counts."""
    return tools.frequency(in_table, out_table, frequency_fields, summary_fields, ctx)


@mcp.tool()
def multiple_ring_buffer(
    input_features: str,
    output_feature_class: str,
    distances: list,
    buffer_unit: str = "Meters",
    field_name: str = "distance",
    dissolve_option: str = "ALL",
    outside_polygons_only: bool = False,
    ctx: Context = None,
) -> str:
    """Creates multiple buffers at specified distances around inputs."""
    return tools.multiple_ring_buffer(
        input_features,
        output_feature_class,
        distances,
        buffer_unit,
        field_name,
        dissolve_option,
        outside_polygons_only,
        ctx,
    )


@mcp.tool()
def split(
    in_features: str,
    split_features: str,
    split_field: str,
    out_workspace: str,
    ctx: Context = None,
) -> str:
    """Splits input features into many feature classes by the unique values of a split field."""
    return tools.split(in_features, split_features, split_field, out_workspace, ctx)


@mcp.tool()
def select(
    in_features: str,
    out_feature_class: str,
    where_clause: str = "",
    ctx: Context = None,
) -> str:
    """Extracts features from input based on a SQL expression."""
    return tools.select(in_features, out_feature_class, where_clause, ctx)


@mcp.tool()
def table_select(
    in_table: str, out_table: str, where_clause: str = "", ctx: Context = None
) -> str:
    """Extracts rows from a table based on an expression."""
    return tools.table_select(in_table, out_table, where_clause, ctx)


# =====================================================================
# 9. DATA MANAGEMENT TOOLS
# =====================================================================


@mcp.tool()
def calculate_field(
    in_table: str,
    field: str,
    expression: str,
    expression_type: str = "PYTHON3",
    code_block: str = "",
    field_type: str = "",
    ctx: Context = None,
) -> str:
    """Performs field calculations on feature classes or tables. expression_type: PYTHON3, ARCADE, SQL, VB."""
    return tools.calculate_field(
        in_table, field, expression, expression_type, code_block, field_type, ctx
    )


@mcp.tool()
def add_field(
    in_table: str,
    field_name: str,
    field_type: str,
    field_precision: int = 0,
    field_scale: int = 0,
    field_length: int = 50,
    field_alias: str = "",
    field_is_nullable: str = "NULLABLE",
    field_is_required: str = "NON_REQUIRED",
    field_domain: str = "",
    ctx: Context = None,
) -> str:
    """Adds a new field to a table or feature class. field_type: TEXT, LONG, SHORT, DOUBLE, FLOAT, DATE, BLOB."""
    return tools.add_field(
        in_table,
        field_name,
        field_type,
        field_precision,
        field_scale,
        field_length,
        field_alias,
        field_is_nullable,
        field_is_required,
        field_domain,
        ctx,
    )


@mcp.tool()
def delete_field(in_table: str, fields, ctx: Context = None) -> str:
    """Deletes one or more fields from a table or feature class."""
    return tools.delete_field(in_table, fields, ctx)


@mcp.tool()
def project(
    in_dataset: str,
    out_dataset: str,
    out_coor_system: str,
    transform_method: str = "",
    in_coor_system: str = "",
    preserve_shape: str = "NO_PRESERVE_SHAPE",
    max_deviation: str = "",
    vertical: str = "NO_VERTICAL",
    ctx: Context = None,
) -> str:
    """Projects spatial data from one coordinate system to another."""
    return tools.project(
        in_dataset,
        out_dataset,
        out_coor_system,
        transform_method,
        in_coor_system,
        preserve_shape,
        max_deviation,
        vertical,
        ctx,
    )


@mcp.tool()
def define_projection(in_dataset: str, coor_system: str, ctx: Context = None) -> str:
    """Defines the projection of a dataset without transforming its coordinates."""
    return tools.define_projection(in_dataset, coor_system, ctx)


@mcp.tool()
def copy_features(in_features: str, out_feature_class: str, ctx: Context = None) -> str:
    """Copies features to a new feature class."""
    return tools.copy_features(in_features, out_feature_class, ctx)


@mcp.tool()
def copy_rows(in_rows: str, out_table: str, ctx: Context = None) -> str:
    """Copies the rows of a table, table view or feature class to a new table."""
    return tools.copy_rows(in_rows, out_table, ctx)


@mcp.tool()
def get_count(in_features: str, ctx: Context = None) -> str:
    """Returns the total number of rows for a feature class, table or layer."""
    return tools.get_count(in_features, ctx)


@mcp.tool()
def delete(in_data: str, data_type: str = "", ctx: Context = None) -> str:
    """Permanently deletes a dataset."""
    return tools.delete(in_data, data_type, ctx)


@mcp.tool()
def rename(
    in_data: str, out_data: str, data_type: str = "", ctx: Context = None
) -> str:
    """Renames a dataset."""
    return tools.rename(in_data, out_data, data_type, ctx)


@mcp.tool()
def create_feature_class(
    out_path: str,
    out_name: str,
    geometry_type: str = "POINT",
    template: str = "",
    has_m: str = "DISABLED",
    has_z: str = "DISABLED",
    spatial_reference: str = "",
    ctx: Context = None,
) -> str:
    """Creates an empty feature class in a geodatabase or folder. geometry_type: POINT, MULTIPOINT, POLYLINE, POLYGON."""
    return tools.create_feature_class(
        out_path,
        out_name,
        geometry_type,
        template,
        has_m,
        has_z,
        spatial_reference,
        ctx,
    )


@mcp.tool()
def create_table(out_path: str, out_name: str, ctx: Context = None) -> str:
    """Creates an empty table in a geodatabase or dBASE workspace."""
    return tools.create_table(out_path, out_name, ctx)


@mcp.tool()
def repair_geometry(
    in_features: str, delete_null: bool = False, ctx: Context = None
) -> str:
    """Repairs problematic geometry errors in a feature class."""
    return tools.repair_geometry(in_features, delete_null, ctx)


@mcp.tool()
def check_geometry(in_features: list, out_table: str, ctx: Context = None) -> str:
    """Produces a report of geometry problems in a feature class."""
    return tools.check_geometry(in_features, out_table, ctx)


@mcp.tool()
def find_identical(
    in_dataset: str,
    out_dataset: str,
    fields: list,
    xy_tolerance: str = "",
    z_tolerance: str = "",
    output_record_option: str = "ALL",
    ctx: Context = None,
) -> str:
    """Reports records with identical values in a list of fields."""
    return tools.find_identical(
        in_dataset,
        out_dataset,
        fields,
        xy_tolerance,
        z_tolerance,
        output_record_option,
        ctx,
    )


@mcp.tool()
def make_feature_layer(
    in_features: str, out_layer: str, where_clause: str = "", ctx: Context = None
) -> str:
    """Creates a feature layer from an input feature class or layer file."""
    return tools.make_feature_layer(in_features, out_layer, where_clause, ctx)


@mcp.tool()
def make_table_view(
    in_table: str,
    out_view: str,
    where_clause: str = "",
    workspace: str = "",
    ctx: Context = None,
) -> str:
    """Creates a table view from an input table or feature class."""
    return tools.make_table_view(in_table, out_view, where_clause, workspace, ctx)


@mcp.tool()
def add_join(
    in_layer_or_view: str,
    in_field: str,
    join_table: str,
    join_field: str,
    join_type: str = "KEEP_ALL",
    ctx: Context = None,
) -> str:
    """Joins a table to a layer or table view based on a common field."""
    return tools.add_join(
        in_layer_or_view, in_field, join_table, join_field, join_type, ctx
    )


@mcp.tool()
def remove_join(in_layer_or_view: str, join_name: str = "", ctx: Context = None) -> str:
    """Removes a join from a feature layer or table view."""
    return tools.remove_join(in_layer_or_view, join_name, ctx)


@mcp.tool()
def create_file_gdb(out_folder_path: str, out_name: str, ctx: Context = None) -> str:
    """Creates a file geodatabase in the specified folder."""
    return tools.create_file_gdb(out_folder_path, out_name, ctx)


@mcp.tool()
def add_subtypes(
    in_table: str,
    field: str,
    subtype_code: int = 0,
    subtype_description: str = "",
    ctx: Context = None,
) -> str:
    """Adds a subtype to a subtype definition."""
    return tools.add_subtypes(in_table, field, subtype_code, subtype_description, ctx)


# =====================================================================
# 10. BULK DATA ACCESS, TOPOLOGY, BOOKMARKS
# =====================================================================


@mcp.tool()
def insert_features(layer_name: str, features: list, ctx: Context = None) -> str:
    """Inserts multiple point features in a single edit operation (arcpy.da-style batch).
    features: list of {"x", "y", "wkid"=4326, "attributes"={...}}."""
    return tools.insert_features(layer_name, features, ctx)


@mcp.tool()
def update_features(layer_name: str, updates: list, ctx: Context = None) -> str:
    """Updates multiple features by ObjectID in a single edit operation.
    updates: list of {"objectid", "attributes"={...}}."""
    return tools.update_features(layer_name, updates, ctx)


@mcp.tool()
def delete_features(layer_name: str, object_ids: list, ctx: Context = None) -> str:
    """Deletes features identified by the given ObjectIDs."""
    return tools.delete_features(layer_name, object_ids, ctx)


@mcp.tool()
def create_bookmark(name: str, ctx: Context = None) -> str:
    """Creates a spatial bookmark from the current active map view extent."""
    return tools.create_bookmark(name, ctx)


@mcp.tool()
def zoom_to_bookmark(name: str, ctx: Context = None) -> str:
    """Zooms the active map to a named bookmark."""
    return tools.zoom_to_bookmark(name, ctx)


@mcp.tool()
def delete_bookmark(name: str, ctx: Context = None) -> str:
    """Deletes a bookmark by name from the active map."""
    return tools.delete_bookmark(name, ctx)


@mcp.tool()
def create_topology(
    in_dataset: str,
    out_name: str,
    cluster_tolerance: str = "",
    ctx: Context = None,
) -> str:
    """Creates a new topology in a feature dataset."""
    return tools.create_topology(in_dataset, out_name, cluster_tolerance, ctx)


@mcp.tool()
def add_feature_class_to_topology(
    in_topology: str,
    in_feature_class: str,
    xy_rank: int = 1,
    z_rank: int = 1,
    ctx: Context = None,
) -> str:
    """Adds a feature class to a topology."""
    return tools.add_feature_class_to_topology(
        in_topology, in_feature_class, xy_rank, z_rank, ctx
    )


@mcp.tool()
def add_rule_to_topology(
    in_topology: str,
    rule_type: str,
    in_featureclass: str,
    in_subtype: str = "",
    in_featureclass2: str = "",
    in_subtype2: str = "",
    ctx: Context = None,
) -> str:
    """Adds a rule to a topology. rule_type: e.g. "Must Not Overlap", "Must Be Inside"."""
    return tools.add_rule_to_topology(
        in_topology,
        rule_type,
        in_featureclass,
        in_subtype,
        in_featureclass2,
        in_subtype2,
        ctx,
    )


@mcp.tool()
def validate_topology(
    in_topology: str,
    in_area: str = "FULL_EXTENT",
    visible_only: bool = False,
    ctx: Context = None,
) -> str:
    """Validates the specified topology."""
    return tools.validate_topology(in_topology, in_area, visible_only, ctx)


# =====================================================================
# 11. NETWORK ANALYST (REQUIRES EXTENSION)
# =====================================================================


@mcp.tool()
def find_routes(
    input_stops: str,
    output_routes: str,
    route_shape: str = "TRUE_LINES_WITH_MEASURES",
    travel_mode: str = "",
    ctx: Context = None,
) -> str:
    """Finds the best route through ordered stops (Network Analyst). Requires Network Analyst extension."""
    return tools.find_routes(input_stops, output_routes, route_shape, travel_mode, ctx)


@mcp.tool()
def generate_service_areas(
    input_facilities: str,
    output_breaks: str,
    break_values: str = "10",
    break_units: str = "Minutes",
    travel_mode: str = "",
    ctx: Context = None,
) -> str:
    """Generates travel-time/distance service areas (isochrones). Requires Network Analyst extension."""
    return tools.generate_service_areas(
        input_facilities, output_breaks, break_values, break_units, travel_mode, ctx
    )


@mcp.tool()
def find_closest_facilities(
    incidents: str,
    facilities: str,
    output_closest_facility: str,
    number_of_facilities: int = 1,
    travel_mode: str = "",
    ctx: Context = None,
) -> str:
    """Finds the closest facility(ies) for each incident. Requires Network Analyst extension."""
    return tools.find_closest_facilities(
        incidents,
        facilities,
        output_closest_facility,
        number_of_facilities,
        travel_mode,
        ctx,
    )


@mcp.tool()
def generate_od_cost_matrix(
    origins: str,
    destinations: str,
    output_lines: str,
    number_of_destinations: int = 1,
    travel_mode: str = "",
    ctx: Context = None,
) -> str:
    """Generates an Origin-Destination cost matrix. Requires Network Analyst extension."""
    return tools.generate_od_cost_matrix(
        origins,
        destinations,
        output_lines,
        number_of_destinations,
        travel_mode,
        ctx,
    )


# =====================================================================
# 12. SPATIAL ANALYST (REQUIRES EXTENSION)
# =====================================================================


@mcp.tool()
def slope(
    in_raster: str,
    out_raster: str,
    output_measurement: str = "DEGREE",
    z_factor: float = 1.0,
    method: str = "PLANAR",
    z_unit: str = "",
    ctx: Context = None,
) -> str:
    """Derives slope from a surface raster. Requires Spatial Analyst extension."""
    return tools.slope(
        in_raster, out_raster, output_measurement, z_factor, method, z_unit, ctx
    )


@mcp.tool()
def aspect(
    in_raster: str, out_raster: str, method: str = "PLANAR", ctx: Context = None
) -> str:
    """Derives aspect (compass direction of slope) from a surface raster. Requires Spatial Analyst extension."""
    return tools.aspect(in_raster, out_raster, method, ctx)


@mcp.tool()
def hillshade(
    in_raster: str,
    out_raster: str,
    azimuth: float = 315,
    altitude: float = 45,
    shadows: bool = False,
    z_factor: float = 1.0,
    method: str = "PLANAR",
    ctx: Context = None,
) -> str:
    """Generates a hillshade from a surface raster. Requires Spatial Analyst extension."""
    return tools.hillshade(
        in_raster, out_raster, azimuth, altitude, shadows, z_factor, method, ctx
    )


@mcp.tool()
def reclassify(
    in_raster: str,
    reclass_field: str,
    remap: str,
    out_raster: str,
    missing_values: str = "NODATA",
    ctx: Context = None,
) -> str:
    """Reclassifies values in a raster. Requires Spatial Analyst extension."""
    return tools.reclassify(
        in_raster, reclass_field, remap, out_raster, missing_values, ctx
    )


@mcp.tool()
def raster_calculator(expression: str, output_raster: str, ctx: Context = None) -> str:
    """Builds and executes a Map Algebra expression (Raster Calculator). Requires Spatial Analyst extension."""
    return tools.raster_calculator(expression, output_raster, ctx)


@mcp.tool()
def kernel_density(
    in_features: str,
    population_field: str,
    out_raster: str,
    search_radius: str = "",
    area_units: str = "SQUARE_MAP_UNITS",
    method: str = "PLANAR",
    ctx: Context = None,
) -> str:
    """Calculates kernel density from point/polyline features. Requires Spatial Analyst extension."""
    return tools.kernel_density(
        in_features,
        population_field,
        out_raster,
        search_radius,
        area_units,
        method,
        ctx,
    )


@mcp.tool()
def extract_by_mask(
    in_raster: str,
    in_mask_data: str,
    out_raster: str,
    extraction_area: str = "INSIDE",
    ctx: Context = None,
) -> str:
    """Extracts the cells of a raster corresponding to mask features. Requires Spatial Analyst extension."""
    return tools.extract_by_mask(
        in_raster, in_mask_data, out_raster, extraction_area, ctx
    )


@mcp.tool()
def weighted_overlay(
    weighted_overlay_table: str,
    out_raster: str,
    evaluation_scale: str = "1 9 1",
    ctx: Context = None,
) -> str:
    """Overlays several rasters using a common scale and weights. Requires Spatial Analyst extension."""
    return tools.weighted_overlay(
        weighted_overlay_table, out_raster, evaluation_scale, ctx
    )


# =====================================================================
# 13. SPATIAL STATISTICS
# =====================================================================


@mcp.tool()
def hot_spot_analysis(
    input_features: str,
    input_field: str,
    output_features: str,
    conceptualization_of_spatial_relationships: str = "INVERSE_DISTANCE",
    distance_method: str = "EUCLIDEAN_DISTANCE",
    standardization: str = "NONE",
    distance_band_or_threshold_distance: str = "",
    ctx: Context = None,
) -> str:
    """Identifies statistically significant hot/cold spots using Getis-Ord Gi*."""
    return tools.hot_spot_analysis(
        input_features,
        input_field,
        output_features,
        conceptualization_of_spatial_relationships,
        distance_method,
        standardization,
        distance_band_or_threshold_distance,
        ctx,
    )


@mcp.tool()
def cluster_and_outlier_analysis(
    input_features: str,
    input_field: str,
    output_features: str,
    conceptualization_of_spatial_relationships: str = "INVERSE_DISTANCE",
    distance_method: str = "EUCLIDEAN_DISTANCE",
    standardization: str = "NONE",
    distance_band_or_threshold_distance: str = "",
    ctx: Context = None,
) -> str:
    """Identifies clusters and outliers using Anselin Local Moran's I."""
    return tools.cluster_and_outlier_analysis(
        input_features,
        input_field,
        output_features,
        conceptualization_of_spatial_relationships,
        distance_method,
        standardization,
        distance_band_or_threshold_distance,
        ctx,
    )


@mcp.tool()
def optimized_hot_spot_analysis(
    input_features: str,
    output_features: str,
    analysis_field: str = "",
    ctx: Context = None,
) -> str:
    """Creates a map of statistically significant hot/cold trends, choosing parameters automatically."""
    return tools.optimized_hot_spot_analysis(
        input_features, output_features, analysis_field, ctx
    )


@mcp.tool()
def emerging_hot_spot_analysis(
    in_cube: str,
    analysis_variable: str,
    output_features: str,
    neighborhood_distance: str = "",
    neighborhood_time_step: int = 1,
    ctx: Context = None,
) -> str:
    """Identifies trends in spatial clustering from a space-time cube."""
    return tools.emerging_hot_spot_analysis(
        in_cube,
        analysis_variable,
        output_features,
        neighborhood_distance,
        neighborhood_time_step,
        ctx,
    )


@mcp.tool()
def geographically_weighted_regression(
    in_features: str,
    dependent_variable: str,
    explanatory_variables: list,
    out_featureclass: str,
    kernel_type: str = "ADAPTIVE",
    bandwidth_method: str = "AICc",
    ctx: Context = None,
) -> str:
    """Performs Geographically Weighted Regression (GWR) to model spatially varying relationships."""
    return tools.geographically_weighted_regression(
        in_features,
        dependent_variable,
        explanatory_variables,
        out_featureclass,
        kernel_type,
        bandwidth_method,
        ctx,
    )


@mcp.tool()
def generalized_linear_regression(
    in_features: str,
    dependent_variable: str,
    model_type: str = "CONTINUOUS",
    explanatory_variables: list | None = None,
    out_featureclass: str = "",
    ctx: Context = None,
) -> str:
    """Performs Generalized Linear Regression (GLR). model_type: CONTINUOUS, BINARY, COUNT."""
    return tools.generalized_linear_regression(
        in_features,
        dependent_variable,
        model_type,
        explanatory_variables,
        out_featureclass,
        ctx,
    )


@mcp.tool()
def spatial_autocorrelation(
    input_features: str,
    input_field: str,
    conceptualization_of_spatial_relationships: str = "INVERSE_DISTANCE",
    distance_method: str = "EUCLIDEAN_DISTANCE",
    standardization: str = "NONE",
    distance_band_or_threshold_distance: str = "",
    ctx: Context = None,
) -> str:
    """Measures spatial autocorrelation (Global Moran's I)."""
    return tools.spatial_autocorrelation(
        input_features,
        input_field,
        conceptualization_of_spatial_relationships,
        distance_method,
        standardization,
        distance_band_or_threshold_distance,
        ctx,
    )


# =====================================================================
# 14. DIRECT GEOMETRY ENGINE + 3D CAMERA
# =====================================================================


@mcp.tool()
def measure_distance(layer_a: str, layer_b: str, ctx: Context = None) -> str:
    """Geodesic distance (meters) between the first selected feature of each layer."""
    return tools.measure_distance(layer_a, layer_b, ctx)


@mcp.tool()
def geometry_contains(layer_a: str, layer_b: str, ctx: Context = None) -> str:
    """Returns True if the selected feature of layer_a contains that of layer_b."""
    return tools.geometry_contains(layer_a, layer_b, ctx)


@mcp.tool()
def geometry_intersects(layer_a: str, layer_b: str, ctx: Context = None) -> str:
    """Returns True if the two selected geometries intersect."""
    return tools.geometry_intersects(layer_a, layer_b, ctx)


@mcp.tool()
def geometry_within_distance(
    layer_a: str, layer_b: str, distance: float, ctx: Context = None
) -> str:
    """Returns True if the two selected geometries are within a distance of each other."""
    return tools.geometry_within_distance(layer_a, layer_b, distance, ctx)


@mcp.tool()
def geometry_area(layer_name: str, ctx: Context = None) -> str:
    """Returns the area of the first selected polygon feature in the layer."""
    return tools.geometry_area(layer_name, ctx)


@mcp.tool()
def geometry_length(layer_name: str, ctx: Context = None) -> str:
    """Returns the length of the first selected polyline feature in the layer."""
    return tools.geometry_length(layer_name, ctx)


@mcp.tool()
def set_camera_3d(
    heading: float,
    pitch: float,
    roll: float = 0,
    scale: float = 0,
    ctx: Context = None,
) -> str:
    """Sets the camera orientation of the active view (3D scenes). heading 0-360, pitch -90 to 90."""
    return tools.set_camera_3d(heading, pitch, roll, scale, ctx)


# =====================================================================
# 15. PACKAGING, SHARING, GEOCODING
# =====================================================================


@mcp.tool()
def package_map(
    in_map: str,
    output_file: str,
    convert_data: str = "CONVERT",
    convert_arcsddata: str = "CONVERT_ARCSDE",
    extent: str = "",
    apply_extent_to_arcsde: str = "ALL",
    ctx: Context = None,
) -> str:
    """Consolidates a map and all referenced data sources into a .mpkx package."""
    return tools.package_map(
        in_map,
        output_file,
        convert_data,
        convert_arcsddata,
        extent,
        apply_extent_to_arcsde,
        ctx,
    )


@mcp.tool()
def package_project(
    in_project: str,
    output_file: str,
    external_data: str = "EMBED",
    convert_to_arcgispro: str = "CONVERT_TO_ARGISPRO",
    ctx: Context = None,
) -> str:
    """Consolidates a project (.aprx) and its data into a portable .ppkx package."""
    return tools.package_project(
        in_project, output_file, external_data, convert_to_arcgispro, ctx
    )


@mcp.tool()
def package_layer(
    in_layer: str,
    output_file: str,
    convert_data: str = "CONVERT",
    convert_arcsddata: str = "CONVERT_ARCSDE",
    extent: str = "",
    package_version: str = "",
    ctx: Context = None,
) -> str:
    """Packages a layer and its data into a single compressed .lpkx file."""
    return tools.package_layer(
        in_layer,
        output_file,
        convert_data,
        convert_arcsddata,
        extent,
        package_version,
        ctx,
    )


@mcp.tool()
def create_mobile_map_package(
    in_map: list,
    output_file: str,
    in_location: list | None = None,
    area_of_interest: str = "",
    extent: str = "",
    ctx: Context = None,
) -> str:
    """Packages maps for offline use in Field Maps / Navigator apps into a .mmpk file."""
    return tools.create_mobile_map_package(
        in_map, output_file, in_location, area_of_interest, extent, ctx
    )


@mcp.tool()
def create_vector_tile_package(
    in_map: str,
    output_file: str,
    service_type: str = "EXISTING",
    tiling_scheme: str = "",
    ctx: Context = None,
) -> str:
    """Creates a vector tile package (.vtpk) from a map."""
    return tools.create_vector_tile_package(
        in_map, output_file, service_type, tiling_scheme, ctx
    )


@mcp.tool()
def share_package(
    package_path: str, summary: str = "", tags: list | None = None, ctx: Context = None
) -> str:
    """Shares a package (.mpkx, .lpkx, .ppkx, .mmpk, .vtpk) to ArcGIS Online or Enterprise."""
    return tools.share_package(package_path, summary, tags, ctx)


@mcp.tool()
def consolidate_project(
    in_project: str,
    output_folder: str,
    external_data: str = "EMBED",
    convert_to_arcgispro: str = "CONVERT_TO_ARGISPRO",
    ctx: Context = None,
) -> str:
    """Consolidates a project and its data into a folder (no compression)."""
    return tools.consolidate_project(
        in_project, output_folder, external_data, convert_to_arcgispro, ctx
    )


@mcp.tool()
def replace_web_layer(
    in_sd_file: str,
    replace_layers: str = "REPLACE_ALL",
    edit_properties: str = "REPLACE",
    ctx: Context = None,
) -> str:
    """Replaces the layers and data of an existing web layer with an updated .sd file."""
    return tools.replace_web_layer(in_sd_file, replace_layers, edit_properties, ctx)


@mcp.tool()
def geocode_addresses(
    in_table: str,
    address_fields: dict,
    in_address_locator: str,
    out_feature_class: str,
    out_relationship_type: str = "STATIC",
    ctx: Context = None,
) -> str:
    """Geocodes a table of addresses using a locator."""
    return tools.geocode_addresses(
        in_table,
        address_fields,
        in_address_locator,
        out_feature_class,
        out_relationship_type,
        ctx,
    )


@mcp.tool()
def reverse_geocode(
    in_features: str,
    in_address_locator: str,
    out_feature_class: str,
    address_type: str = "ADDRESS",
    ctx: Context = None,
) -> str:
    """Creates addresses from point locations (reverse geocoding)."""
    return tools.reverse_geocode(
        in_features, in_address_locator, out_feature_class, address_type, ctx
    )


@mcp.tool()
def create_locator(
    reference_data: list,
    primary_table_info: dict,
    in_address_fields: dict,
    out_locator: str,
    language_code: str = "",
    ctx: Context = None,
) -> str:
    """Creates a geocoding locator from reference data."""
    return tools.create_locator(
        reference_data,
        primary_table_info,
        in_address_fields,
        out_locator,
        language_code,
        ctx,
    )


@mcp.tool()
def rematch_addresses(
    in_geocoded_feature_class: str,
    in_address_locator: str,
    geocoding_options: str = "",
    ctx: Context = None,
) -> str:
    """Re-matches addresses in a geocoded feature class."""
    return tools.rematch_addresses(
        in_geocoded_feature_class, in_address_locator, geocoding_options, ctx
    )


# =====================================================================
# 16. LICENSING
# =====================================================================


@mcp.tool()
def check_license(ctx: Context = None) -> str:
    """Returns the current ArcGIS Pro license level and the list of licensed extensions."""
    return tools.get_license_status(ctx)


# =====================================================================
# RUN SERVER
# =====================================================================
def main():
    mcp.run()


if __name__ == "__main__":
    main()
