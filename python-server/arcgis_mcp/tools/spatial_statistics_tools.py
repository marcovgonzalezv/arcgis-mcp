"""
Spatial statistics wrappers.

The Spatial Statistics toolbox is part of the core ArcGIS Pro license (Basic and
above), so these wrappers do not require an extension. They expose the most
valuable clustering, regression and distribution analyses.
"""

from mcp.server.fastmcp import Context

from .geoprocessing_tools import run_gp_tool


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
    """
    Given a set of weighted features, identifies statistically significant hot
    spots and cold spots using the Getis-Ord Gi* statistic.
    """
    params = [
        input_features,
        input_field,
        output_features,
        conceptualization_of_spatial_relationships,
        distance_method,
        standardization,
    ]
    if distance_band_or_threshold_distance:
        params.append(distance_band_or_threshold_distance)
    return run_gp_tool("HotSpotAnalysis_stats", params, ctx, add_outputs_to_map=True)


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
    """
    Identifies statistically significant clusters of high and low values, and
    spatial outliers, using the Anselin Local Moran's I statistic.
    """
    params = [
        input_features,
        input_field,
        output_features,
        conceptualization_of_spatial_relationships,
        distance_method,
        standardization,
    ]
    if distance_band_or_threshold_distance:
        params.append(distance_band_or_threshold_distance)
    return run_gp_tool("ClustersOutliers_stats", params, ctx, add_outputs_to_map=True)


def optimized_hot_spot_analysis(
    input_features: str,
    output_features: str,
    analysis_field: str = "",
    ctx: Context = None,
) -> str:
    """
    Given event points or weighted features, creates a map of statistically
    significant hot and cold trends, choosing parameters automatically.
    """
    params = [input_features, output_features]
    if analysis_field:
        params.append(analysis_field)
    return run_gp_tool(
        "OptimizedHotSpotAnalysis_stats", params, ctx, add_outputs_to_map=True
    )


def emerging_hot_spot_analysis(
    in_cube: str,
    analysis_variable: str,
    output_features: str,
    neighborhood_distance: str = "",
    neighborhood_time_step: int = 1,
    ctx: Context = None,
) -> str:
    """
    Identifies trends in spatial clustering (new, intensifying, diminishing,
    sporadic, oscillating) from a space-time cube.
    in_cube: path to a netCDF space-time cube.
    """
    params = [in_cube, analysis_variable, output_features]
    if neighborhood_distance:
        params.append(neighborhood_distance)
        params.append(neighborhood_time_step)
    return run_gp_tool(
        "EmergingHotSpotAnalysis_stpm", params, ctx, add_outputs_to_map=True
    )


def geographically_weighted_regression(
    in_features: str,
    dependent_variable: str,
    explanatory_variables: list,
    out_featureclass: str,
    kernel_type: str = "ADAPTIVE",
    bandwidth_method: str = "AICc",
    ctx: Context = None,
) -> str:
    """
    Performs Geographically Weighted Regression (GWR), a local form of linear
    regression used to model spatially varying relationships.
    """
    params = [
        in_features,
        dependent_variable,
        ",".join(explanatory_variables),
        out_featureclass,
        kernel_type,
        bandwidth_method,
    ]
    return run_gp_tool("GWR_stats", params, ctx, add_outputs_to_map=True)


def generalized_linear_regression(
    in_features: str,
    dependent_variable: str,
    model_type: str = "CONTINUOUS",
    explanatory_variables: list | None = None,
    out_featureclass: str = "",
    ctx: Context = None,
) -> str:
    """
    Performs Generalized Linear Regression (GLR) to generate predictions or
    model a dependent variable in terms of its relationship to explanatory
    variables.
    model_type: "CONTINUOUS", "BINARY", "COUNT".
    """
    params = [in_features, dependent_variable, model_type]
    if explanatory_variables:
        params.append(",".join(explanatory_variables))
    if out_featureclass:
        params.append(out_featureclass)
    return run_gp_tool("GLR_stats", params, ctx, add_outputs_to_map=True)


def spatial_autocorrelation(
    input_features: str,
    input_field: str,
    conceptualization_of_spatial_relationships: str = "INVERSE_DISTANCE",
    distance_method: str = "EUCLIDEAN_DISTANCE",
    standardization: str = "NONE",
    distance_band_or_threshold_distance: str = "",
    ctx: Context = None,
) -> str:
    """
    Measures spatial autocorrelation (Global Moran's I) for a feature dataset.
    """
    params = [
        input_features,
        input_field,
        "NO_REPORT",
        conceptualization_of_spatial_relationships,
        distance_method,
        standardization,
    ]
    if distance_band_or_threshold_distance:
        params.append(distance_band_or_threshold_distance)
    return run_gp_tool(
        "SpatialAutocorrelation_stats", params, ctx, add_outputs_to_map=False
    )
