"""
Spatial Analyst wrappers.

All wrappers require the ArcGIS Spatial Analyst extension and therefore call
:func:`require_extension` first. The check returns a clear, actionable message
to the caller if the user does not hold the license.
"""

from mcp.server.fastmcp import Context

from .geoprocessing_tools import run_gp_tool
from .licensing import LicenseError, require_extension


def slope(
    in_raster: str,
    out_raster: str,
    output_measurement: str = "DEGREE",
    z_factor: float = 1.0,
    method: str = "PLANAR",
    z_unit: str = "",
    ctx: Context = None,
) -> str:
    """
    Derives slope from a surface raster. Requires Spatial Analyst.
    output_measurement: "DEGREE" or "PERCENT_RISE".
    """
    try:
        require_extension("spatial_analyst", ctx)
    except LicenseError as exc:
        return str(exc)

    params = [in_raster, out_raster, output_measurement, z_factor, method]
    if z_unit:
        params.append(z_unit)
    return run_gp_tool("Slope_sa", params, ctx, add_outputs_to_map=True)


def aspect(
    in_raster: str, out_raster: str, method: str = "PLANAR", ctx: Context = None
) -> str:
    """
    Derives aspect (compass direction of slope) from a surface raster.
    Requires Spatial Analyst.
    """
    try:
        require_extension("spatial_analyst", ctx)
    except LicenseError as exc:
        return str(exc)

    return run_gp_tool(
        "Aspect_sa", [in_raster, out_raster, method], ctx, add_outputs_to_map=True
    )


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
    """
    Generates a hillshade from a surface raster. Requires Spatial Analyst.
    """
    try:
        require_extension("spatial_analyst", ctx)
    except LicenseError as exc:
        return str(exc)

    params = [
        in_raster,
        out_raster,
        azimuth,
        altitude,
        "SHADOWS" if shadows else "NO_SHADOWS",
        z_factor,
        method,
    ]
    return run_gp_tool("Hillshade_sa", params, ctx, add_outputs_to_map=True)


def reclassify(
    in_raster: str,
    reclass_field: str,
    remap: str,
    out_raster: str,
    missing_values: str = "NODATA",
    ctx: Context = None,
) -> str:
    """
    Reclassifies (changes) values in a raster. Requires Spatial Analyst.
    remap: e.g. "0 50 1;50 100 2;100 1000 3" (From To NewValue).
    """
    try:
        require_extension("spatial_analyst", ctx)
    except LicenseError as exc:
        return str(exc)

    return run_gp_tool(
        "Reclassify_sa",
        [in_raster, reclass_field, remap, out_raster, missing_values],
        ctx,
        add_outputs_to_map=True,
    )


def raster_calculator(expression: str, output_raster: str, ctx: Context = None) -> str:
    """
    Builds and executes a Map Algebra expression (Raster Calculator).
    Requires Spatial Analyst.
    expression: e.g. "\"slope\" * 2 + \"aspect\"".
    """
    try:
        require_extension("spatial_analyst", ctx)
    except LicenseError as exc:
        return str(exc)

    return run_gp_tool(
        "RasterCalculator_sa", [expression, output_raster], ctx, add_outputs_to_map=True
    )


def kernel_density(
    in_features: str,
    population_field: str,
    out_raster: str,
    search_radius: str = "",
    area_units: str = "SQUARE_MAP_UNITS",
    method: str = "PLANAR",
    ctx: Context = None,
) -> str:
    """
    Calculates density from point/polyline features using a kernel function.
    Requires Spatial Analyst.
    """
    try:
        require_extension("spatial_analyst", ctx)
    except LicenseError as exc:
        return str(exc)

    params = [in_features, population_field, out_raster]
    if search_radius:
        params.append(search_radius)
        params.append(area_units)
        params.append(method)
    return run_gp_tool("KernelDensity_sa", params, ctx, add_outputs_to_map=True)


def extract_by_mask(
    in_raster: str,
    in_mask_data: str,
    out_raster: str,
    extraction_area: str = "INSIDE",
    ctx: Context = None,
) -> str:
    """
    Extracts the cells of a raster that correspond to the mask features.
    Requires Spatial Analyst.
    """
    try:
        require_extension("spatial_analyst", ctx)
    except LicenseError as exc:
        return str(exc)

    return run_gp_tool(
        "ExtractByMask_sa",
        [in_raster, in_mask_data, out_raster, extraction_area],
        ctx,
        add_outputs_to_map=True,
    )


def weighted_overlay(
    weighted_overlay_table: str,
    out_raster: str,
    evaluation_scale: str = "1 9 1",
    ctx: Context = None,
) -> str:
    """
    Overlays several rasters using a common scale and weights each by a given
    percentage. Requires Spatial Analyst.
    weighted_overlay_table: e.g. "\"ElevationRaster\" 1 1 50;\"SlopeRaster\" 1 1 50".
    """
    try:
        require_extension("spatial_analyst", ctx)
    except LicenseError as exc:
        return str(exc)

    params = [weighted_overlay_table, out_raster, evaluation_scale]
    return run_gp_tool("WeightedOverlay_sa", params, ctx, add_outputs_to_map=True)
