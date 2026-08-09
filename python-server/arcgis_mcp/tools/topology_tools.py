"""
Topology and geodatabase workflow wrappers.

These wrap the geoprocessing tools that create, validate and edit geodatabase
topologies, plus the utility network trace network helpers.
"""

from mcp.server.fastmcp import Context

from .geoprocessing_tools import run_gp_tool


def create_topology(
    in_dataset: str,
    out_name: str,
    cluster_tolerance: str = "",
    ctx: Context = None,
) -> str:
    """
    Creates a new topology in a feature dataset.
    """
    params = [in_dataset, out_name]
    if cluster_tolerance:
        params.append(cluster_tolerance)
    return run_gp_tool(
        "CreateTopology_management", params, ctx, add_outputs_to_map=False
    )


def add_feature_class_to_topology(
    in_topology: str,
    in_feature_class: str,
    xy_rank: int = 1,
    z_rank: int = 1,
    ctx: Context = None,
) -> str:
    """
    Adds a feature class to a topology.
    """
    return run_gp_tool(
        "AddFeatureClassToTopology_management",
        [in_topology, in_feature_class, xy_rank, z_rank],
        ctx,
        add_outputs_to_map=False,
    )


def add_rule_to_topology(
    in_topology: str,
    rule_type: str,
    in_featureclass: str,
    in_subtype: str = "",
    in_featureclass2: str = "",
    in_subtype2: str = "",
    ctx: Context = None,
) -> str:
    """
    Adds a rule to a topology.
    rule_type: e.g. "Must Not Overlap", "Must Be Inside".
    """
    params = [in_topology, rule_type, in_featureclass]
    if in_subtype:
        params.append(in_subtype)
    if in_featureclass2:
        params.append(in_featureclass2)
    if in_subtype2:
        params.append(in_subtype2)
    return run_gp_tool(
        "AddRuleToTopology_management", params, ctx, add_outputs_to_map=False
    )


def validate_topology(
    in_topology: str,
    in_area: str = "FULL_EXTENT",
    visible_only: bool = False,
    ctx: Context = None,
) -> str:
    """
    Validates the specified topology.
    in_area: "FULL_EXTENT" or an extent string.
    """
    return run_gp_tool(
        "ValidateTopology_management",
        [in_topology, in_area, visible_only],
        ctx,
        add_outputs_to_map=False,
    )
