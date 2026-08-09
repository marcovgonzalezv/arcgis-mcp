"""
Vector analysis wrappers.

Higher-level wrappers around the Analysis toolbox so the caller does not have to
build raw parameter arrays. All delegate to :func:`run_gp_tool`.
"""

from mcp.server.fastmcp import Context

from .geoprocessing_tools import run_gp_tool


def dissolve(
    in_features: str,
    out_feature_class: str,
    dissolve_fields: list | None = None,
    statistics_fields: list | None = None,
    multi_part: str = "MULTI_PART",
    unsplit_lines: str = "DISSOLVE_LINES",
    ctx: Context = None,
) -> str:
    """
    Aggregates features based on specified attributes.
    dissolve_fields: optional list of field names.
    statistics_fields: optional list like ["POP SUM", "AREA MIN"].
    multi_part: "MULTI_PART" or "SINGLE_PART".
    """
    params = [in_features, out_feature_class]
    params.append(dissolve_fields or [])
    params.append(statistics_fields or [])
    params.append(multi_part)
    params.append(unsplit_lines)
    return run_gp_tool("Dissolve_management", params, ctx, add_outputs_to_map=True)


def intersect(
    in_features: list,
    out_feature_class: str,
    join_attributes: str = "ALL",
    cluster_tolerance: str = "",
    output_type: str = "INPUT",
    ctx: Context = None,
) -> str:
    """
    Computes the geometric intersection of feature classes.
    in_features: e.g. ["Roads", "Parcels"].
    output_type: "INPUT", "LINE", "POINT".
    """
    params = [in_features, out_feature_class, join_attributes]
    if cluster_tolerance:
        params.append(cluster_tolerance)
        params.append(output_type)
    return run_gp_tool("Intersect_analysis", params, ctx, add_outputs_to_map=True)


def union(
    in_features: list,
    out_feature_class: str,
    join_attributes: str = "ALL",
    gaps: str = "GAPS",
    cluster_tolerance: str = "",
    ctx: Context = None,
) -> str:
    """
    Computes the geometric union of polygon feature classes.
    gaps: "GAPS" (no sliver) or "NO_GAPS".
    """
    params = [in_features, out_feature_class, join_attributes, gaps]
    if cluster_tolerance:
        params.append(cluster_tolerance)
    return run_gp_tool("Union_analysis", params, ctx, add_outputs_to_map=True)


def erase(
    in_features: str,
    erase_features: str,
    out_feature_class: str,
    cluster_tolerance: str = "",
    ctx: Context = None,
) -> str:
    """
    Removes features (and portions of features) that overlap the erase features.
    """
    params = [in_features, erase_features, out_feature_class]
    if cluster_tolerance:
        params.append(cluster_tolerance)
    return run_gp_tool("Erase_analysis", params, ctx, add_outputs_to_map=True)


def merge(
    inputs: list,
    output: str,
    field_map: str = "",
    ctx: Context = None,
) -> str:
    """
    Combines multiple input datasets into a new output dataset.
    inputs: list of layer/feature-class paths.
    """
    params = [inputs, output]
    if field_map:
        params.append(field_map)
    return run_gp_tool("Merge_management", params, ctx, add_outputs_to_map=True)


def append(
    inputs: list,
    target: str,
    schema_type: str = "TEST",
    field_map: str = "",
    subtype: str = "",
    ctx: Context = None,
) -> str:
    """
    Appends multiple input datasets into an existing target dataset.
    schema_type: "TEST" (must match) or "NO_TEST".
    """
    params = [inputs, target, schema_type]
    if field_map:
        params.append(field_map)
    if subtype:
        params.append(subtype)
    return run_gp_tool("Append_management", params, ctx, add_outputs_to_map=False)


def near(
    in_features: str,
    near_features: str,
    search_radius: str = "",
    location: bool = False,
    angle: bool = False,
    method: str = "PLANAR",
    ctx: Context = None,
) -> str:
    """
    Adds distance, location and angle from ``in_features`` to the nearest
    ``near_features``.
    """
    params = [in_features, near_features]
    if search_radius:
        params.append(search_radius)
        params.append(location)
        params.append(angle)
        params.append(method)
    return run_gp_tool("Near_analysis", params, ctx, add_outputs_to_map=False)


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
    """
    Produces a table of distances between input and near features.
    closest: "ALL" or "CLOSEST".
    """
    params = [
        in_features,
        near_features,
        out_table,
        search_radius,
        location,
        angle,
        closest,
    ]
    if closest == "CLOSEST":
        params.append(closest_count)
        params.append(method)
    return run_gp_tool(
        "GenerateNearTable_analysis", params, ctx, add_outputs_to_map=False
    )


def select_layer_by_location(
    in_layer: str,
    overlap_type: str = "INTERSECT",
    select_features: str = "",
    search_distance: str = "",
    selection_type: str = "NEW_SELECTION",
    invert_spatial_relationship: str = "NOT_INVERT",
    ctx: Context = None,
) -> str:
    """
    Selects features in a layer based on their spatial relationship to
    features in another layer.
    selection_type: "NEW_SELECTION", "ADD_TO_SELECTION", "REMOVE_FROM_SELECTION",
    "SUBSET_SELECTION", "SWITCH_SELECTION", "CLEAR_SELECTION".
    """
    params = [in_layer, overlap_type]
    if select_features:
        params.append(select_features)
        if search_distance:
            params.append(search_distance)
        params.append(selection_type)
        params.append(invert_spatial_relationship)
    return run_gp_tool(
        "SelectLayerByLocation_management", params, ctx, add_outputs_to_map=False
    )


def summary_statistics(
    in_table: str,
    out_table: str,
    statistics_fields: list,
    case_fields: list | None = None,
    ctx: Context = None,
) -> str:
    """
    Computes summary statistics for fields in a table.
    statistics_fields: e.g. [["POP", "SUM"], ["AREA", "MEAN"]].
    """
    params = [in_table, out_table, statistics_fields]
    if case_fields:
        params.append(case_fields)
    return run_gp_tool("Statistics_analysis", params, ctx, add_outputs_to_map=False)


def frequency(
    in_table: str,
    out_table: str,
    frequency_fields: list,
    summary_fields: list | None = None,
    ctx: Context = None,
) -> str:
    """
    Reads a table and produces a new table containing unique field values and
    their counts.
    """
    params = [in_table, out_table, frequency_fields]
    if summary_fields:
        params.append(summary_fields)
    return run_gp_tool("Frequency_analysis", params, ctx, add_outputs_to_map=False)


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
    """
    Creates multiple buffers at specified distances around inputs.
    distances: list of numeric distances, e.g. [100, 200, 500].
    """
    params = [
        input_features,
        output_feature_class,
        distances,
        buffer_unit,
        field_name,
        dissolve_option,
        outside_polygons_only,
    ]
    return run_gp_tool(
        "MultipleRingBuffer_analysis", params, ctx, add_outputs_to_map=True
    )


def split(
    in_features: str,
    split_features: str,
    split_field: str,
    out_workspace: str,
    ctx: Context = None,
) -> str:
    """
    Splits input features into many feature classes by the unique values of a
    split field.
    """
    params = [in_features, split_features, split_field, out_workspace]
    return run_gp_tool("Split_analysis", params, ctx, add_outputs_to_map=False)


def select(
    in_features: str,
    out_feature_class: str,
    where_clause: str = "",
    ctx: Context = None,
) -> str:
    """
    Extracts features from input based on a SQL expression.
    """
    params = [in_features, out_feature_class]
    if where_clause:
        params.append(where_clause)
    return run_gp_tool("Select_analysis", params, ctx, add_outputs_to_map=True)


def table_select(
    in_table: str,
    out_table: str,
    where_clause: str = "",
    ctx: Context = None,
) -> str:
    """
    Extracts rows from a table based on an expression.
    """
    params = [in_table, out_table]
    if where_clause:
        params.append(where_clause)
    return run_gp_tool("TableSelect_analysis", params, ctx, add_outputs_to_map=False)
