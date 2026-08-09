"""
Format conversion wrappers.

These wrap the ArcGIS Conversion toolbox tools so the caller can move data
between Excel, KML, CAD/BIM, raster/vector and JSON formats without having to
remember the exact ``run_gp_tool`` parameter order. Each wrapper delegates to
:func:`run_gp_tool`, so no Add-In change is required.
"""

from mcp.server.fastmcp import Context

from .geoprocessing_tools import run_gp_tool


def excel_to_table(
    input_excel_file: str,
    output_table: str,
    sheet: str = "",
    cell_range: str = "",
    ctx: Context = None,
) -> str:
    """
    Imports an Excel workbook (.xlsx/.xls) into a geodatabase table or dBASE.
    sheet: optional sheet name; cell_range: e.g. "A1:G100".
    """
    params = [input_excel_file, output_table]
    if sheet:
        params.append(sheet)
    if cell_range:
        if not sheet:
            params.append("")
        params.append(cell_range)
    return run_gp_tool("ExcelToTable_conversion", params, ctx, add_outputs_to_map=False)


def table_to_excel(
    input_table: str,
    output_excel_file: str,
    use_field_alias_as_header: bool = False,
    use_domain_and_subtype_description: bool = False,
    ctx: Context = None,
) -> str:
    """
    Exports a table or feature class attribute table to Excel (.xlsx).
    """
    params = [
        input_table,
        output_excel_file,
        use_field_alias_as_header,
        use_domain_and_subtype_description,
    ]
    return run_gp_tool("TableToExcel_conversion", params, ctx, add_outputs_to_map=False)


def kml_to_layer(input_kml: str, output_folder: str, ctx: Context = None) -> str:
    """
    Converts a KML/KMZ file into a feature class and layer file inside a file
    geodatabase in ``output_folder``.
    """
    return run_gp_tool(
        "KMLToLayer_conversion",
        [input_kml, output_folder],
        ctx,
        add_outputs_to_map=False,
    )


def layer_to_kml(
    layer: str,
    output_kmz: str,
    output_scale: int = 0,
    ctx: Context = None,
) -> str:
    """
    Converts a map layer, layer file or feature class to a KMZ file.
    output_scale: 0 for no scale dependency (all features), otherwise the
    reference scale.
    """
    return run_gp_tool(
        "LayerToKML_conversion",
        [layer, output_kmz, output_scale],
        ctx,
        add_outputs_to_map=False,
    )


def features_to_json(
    in_features: str,
    out_json_file: str,
    format_json: bool = False,
    include_geometry: bool = True,
    ctx: Context = None,
) -> str:
    """
    Converts features to ArcGIS JSON or GeoJSON. include_geometry=False yields
    a JSON table.
    """
    params = [in_features, out_json_file, format_json, include_geometry]
    return run_gp_tool(
        "FeaturesToJSON_conversion", params, ctx, add_outputs_to_map=False
    )


def json_to_features(
    in_json_file: str,
    out_features: str,
    geometry_type: str = "",
    ctx: Context = None,
) -> str:
    """
    Creates a feature class from Esri JSON or GeoJSON.
    geometry_type: "POINT", "POLYLINE" or "POLYGON" (required for GeoJSON).
    """
    params = [in_json_file, out_features]
    if geometry_type:
        params.append(geometry_type)
    return run_gp_tool(
        "JSONToFeatures_conversion", params, ctx, add_outputs_to_map=True
    )


def raster_to_polygon(
    in_raster: str,
    out_polygon_features: str,
    simplify: bool = True,
    raster_field: str = "Value",
    ctx: Context = None,
) -> str:
    """
    Converts a raster dataset to polygon features.
    """
    return run_gp_tool(
        "RasterToPolygon_conversion",
        [in_raster, out_polygon_features, simplify, raster_field],
        ctx,
        add_outputs_to_map=True,
    )


def polygon_to_raster(
    in_features: str,
    value_field: str,
    out_raster_dataset: str,
    cell_assignment: str = "CELL_CENTER",
    priority_field: str = "",
    cellsize: str = "",
    ctx: Context = None,
) -> str:
    """
    Converts polygon features to a raster dataset.
    cell_assignment: "CELL_CENTER", "MAXIMUM_AREA", "MAXIMUM_COMBINED_AREA".
    """
    params = [in_features, value_field, out_raster_dataset, cell_assignment]
    if priority_field:
        params.append(priority_field)
    if cellsize:
        params.append(cellsize)
    return run_gp_tool(
        "PolygonToRaster_conversion", params, ctx, add_outputs_to_map=True
    )


def point_to_raster(
    in_features: str,
    value_field: str,
    out_raster_dataset: str,
    cell_assignment: str = "MOST_FREQUENT",
    priority_field: str = "",
    cellsize: str = "",
    ctx: Context = None,
) -> str:
    """
    Converts point features to a raster dataset.
    cell_assignment: "MOST_FREQUENT", "SUM", "MEAN", "MINIMUM", "MAXIMUM".
    """
    params = [in_features, value_field, out_raster_dataset, cell_assignment]
    if priority_field:
        params.append(priority_field)
    if cellsize:
        params.append(cellsize)
    return run_gp_tool("PointToRaster_conversion", params, ctx, add_outputs_to_map=True)


def export_features(
    in_features: str,
    out_features: str,
    where_clause: str = "",
    use_field_alias_as_name: bool = False,
    ctx: Context = None,
) -> str:
    """
    Exports a feature class or layer to a new feature class (shapefile,
    file geodatabase, etc.). Equivalent to the geoprocessing "Export Features".
    """
    params = [in_features, out_features]
    if where_clause:
        params.append(where_clause)
    if use_field_alias_as_name:
        if not where_clause:
            params.append("")
        params.append(use_field_alias_as_name)
    return run_gp_tool(
        "ExportFeatures_conversion", params, ctx, add_outputs_to_map=True
    )


def export_table(
    in_table: str,
    out_table: str,
    where_clause: str = "",
    use_field_alias_as_name: bool = False,
    ctx: Context = None,
) -> str:
    """
    Exports a table or attribute table to a new standalone table.
    """
    params = [in_table, out_table]
    if where_clause:
        params.append(where_clause)
    if use_field_alias_as_name:
        if not where_clause:
            params.append("")
        params.append(use_field_alias_as_name)
    return run_gp_tool("ExportTable_conversion", params, ctx, add_outputs_to_map=False)


def feature_class_to_shapefile(
    input_features: list, output_folder: str, ctx: Context = None
) -> str:
    """
    Converts one or more feature classes to shapefiles in a folder.
    """
    return run_gp_tool(
        "FeatureClassToShapefile_conversion",
        [input_features, output_folder],
        ctx,
        add_outputs_to_map=False,
    )


def cad_to_geodatabase(
    input_cad: str,
    output_geodatabase: str,
    reference_scale: str = "",
    spatial_reference: str = "",
    ctx: Context = None,
) -> str:
    """
    Converts CAD data (.dwg/.dgn/.dxf) into feature classes in a geodatabase.
    """
    params = [input_cad, output_geodatabase]
    if reference_scale:
        params.append(reference_scale)
    if spatial_reference:
        params.append(spatial_reference)
    return run_gp_tool(
        "CADToGeodatabase_conversion", params, ctx, add_outputs_to_map=False
    )


def bim_to_geodatabase(
    input_bim: str,
    output_geodatabase: str,
    include_features: bool = True,
    spatial_reference: str = "",
    ctx: Context = None,
) -> str:
    """
    Converts Revit/BIM data (.rvt/.ifc/.dgn) into feature classes.
    """
    params = [
        input_bim,
        output_geodatabase,
        "INCLUDE_FEATURES" if include_features else "EXCLUDE_FEATURES",
    ]
    if spatial_reference:
        params.append(spatial_reference)
    return run_gp_tool(
        "BIMFileToGeodatabase_conversion", params, ctx, add_outputs_to_map=False
    )
