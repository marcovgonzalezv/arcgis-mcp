from pipe_client import ArcGisPipeClient
from mcp.server.fastmcp import Context
from tools.safety import DestructiveOperationBlocked, guard_destructive_tool

client = ArcGisPipeClient()


def run_gp_tool(
    tool_name: str,
    parameters: list,
    ctx: Context = None,
    add_outputs_to_map: bool = False,
    allow_delete: bool = False,
) -> str:
    """
    Executes any ArcGIS Pro geoprocessing tool by name with list of parameters.
    Example: tool_name="Buffer_analysis", parameters=["Roads", "Roads_Buffer", "100 Meters"]
    """
    try:
        guard_destructive_tool(tool_name, allow_delete)
    except DestructiveOperationBlocked as exc:
        return str(exc)

    if ctx:
        ctx.info(
            f"Executing geoprocessing tool '{tool_name}' with parameters {parameters}..."
        )
    resp = client.send_command(
        "run_gp_tool",
        {
            "tool_name": tool_name,
            "parameters": parameters,
            "add_outputs_to_map": add_outputs_to_map,
            "allow_delete": allow_delete,
        },
        timeout_ms=120000,
    )
    if resp.get("success"):
        data = resp.get("data", {})
        messages = data.get("messages", [])
        outputs = data.get("outputs", [])
        msg_str = (
            "\n".join(messages) if messages else "Execution completed without messages."
        )
        output_str = f"\nOutputs:\n{outputs}" if outputs else ""
        return (
            f"Geoprocessing tool '{tool_name}' executed successfully.\n"
            f"Messages:\n{msg_str}{output_str}"
        )
    else:
        error = resp.get("message") or resp.get("error")
        return f"Error executing geoprocessing tool '{tool_name}': {error}"


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
    if ctx:
        ctx.info(
            f"Running Buffer analysis for '{input_features}' (distance: {buffer_distance})..."
        )
    # Buffer_analysis [in_features, out_feature_class, buffer_distance_or_field, line_side, line_end_type, dissolve_option, dissolve_field, method]
    params = [input_features, output_feature_class, buffer_distance]
    return run_gp_tool("Buffer_analysis", params, ctx, add_outputs_to_map=True)


def clip_analysis(
    input_features: str,
    clip_features: str,
    output_feature_class: str,
    ctx: Context = None,
) -> str:
    """
    Clips/extracts input features that overlay clip features.
    """
    if ctx:
        ctx.info(
            f"Running Clip analysis on '{input_features}' with clip boundary '{clip_features}'..."
        )
    # Clip_analysis [in_features, clip_features, out_feature_class, cluster_tolerance]
    params = [input_features, clip_features, output_feature_class]
    return run_gp_tool("Clip_analysis", params, ctx, add_outputs_to_map=True)


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
    if ctx:
        ctx.info(
            f"Running Spatial Join between '{target_features}' and '{join_features}'..."
        )
    # SpatialJoin_analysis [target_features, join_features, out_feature_class, join_operation, join_type, field_mapping, match_option, search_radius, distance_field_name]
    params = [
        target_features,
        join_features,
        output_feature_class,
        join_operation,
        join_type,
        "",  # Skip field mapping (uses defaults)
        match_option,
    ]
    return run_gp_tool("SpatialJoin_analysis", params, ctx, add_outputs_to_map=True)
