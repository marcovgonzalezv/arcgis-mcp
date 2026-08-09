"""
Network Analyst wrappers.

All wrappers require the ArcGIS Network Analyst extension and therefore call
:func:`require_extension` first. The extension check returns a clear, actionable
message to the caller if the user does not hold the license.

These wrappers use the modern arcpy.nax module by delegating to the
geoprocessing ``FindRoutes``, ``GenerateServiceAreas``, ``FindClosestFacilities``
and ``GenerateOriginDestinationCostMatrix`` tools, which expose the nax solvers
directly as GP tools.
"""

from mcp.server.fastmcp import Context

from .geoprocessing_tools import run_gp_tool
from .licensing import LicenseError, require_extension


def find_routes(
    input_stops: str,
    output_routes: str,
    route_shape: str = "TRUE_LINES_WITH_MEASURES",
    travel_mode: str = "",
    ctx: Context = None,
) -> str:
    """
    Finds the best route through ordered stops (Network Analyst Route solver).
    Requires ArcGIS Network Analyst extension.
    input_stops: layer or feature class with stops.
    route_shape: "TRUE_LINES_WITH_MEASURES", "TRUE_LINES", "NO_LINES", "STRAIGHT_LINES".
    """
    try:
        require_extension("network_analyst", ctx)
    except LicenseError as exc:
        return str(exc)

    params = [input_stops, output_routes, route_shape]
    if travel_mode:
        params.append(travel_mode)
    return run_gp_tool("FindRoutes_na", params, ctx, add_outputs_to_map=True)


def generate_service_areas(
    input_facilities: str,
    output_breaks: str,
    break_values: str = "10",
    break_units: str = "Minutes",
    travel_mode: str = "",
    ctx: Context = None,
) -> str:
    """
    Generates travel-time/distance service areas (isochrones) around facilities.
    Requires ArcGIS Network Analyst extension.
    break_values: space-separated break values, e.g. "5 10 15".
    """
    try:
        require_extension("network_analyst", ctx)
    except LicenseError as exc:
        return str(exc)

    params = [input_facilities, output_breaks, break_values, break_units]
    if travel_mode:
        params.append(travel_mode)
    return run_gp_tool("GenerateServiceAreas_na", params, ctx, add_outputs_to_map=True)


def find_closest_facilities(
    incidents: str,
    facilities: str,
    output_closest_facility: str,
    number_of_facilities: int = 1,
    travel_mode: str = "",
    ctx: Context = None,
) -> str:
    """
    Finds the closest facility(ies) for each incident.
    Requires ArcGIS Network Analyst extension.
    """
    try:
        require_extension("network_analyst", ctx)
    except LicenseError as exc:
        return str(exc)

    params = [incidents, facilities, output_closest_facility, number_of_facilities]
    if travel_mode:
        params.append(travel_mode)
    return run_gp_tool("FindClosestFacilities_na", params, ctx, add_outputs_to_map=True)


def generate_od_cost_matrix(
    origins: str,
    destinations: str,
    output_lines: str,
    number_of_destinations: int = 1,
    travel_mode: str = "",
    ctx: Context = None,
) -> str:
    """
    Generates an Origin-Destination cost matrix (Network Analyst OD solver).
    Requires ArcGIS Network Analyst extension.
    """
    try:
        require_extension("network_analyst", ctx)
    except LicenseError as exc:
        return str(exc)

    params = [origins, destinations, output_lines, number_of_destinations]
    if travel_mode:
        params.append(travel_mode)
    return run_gp_tool(
        "GenerateOriginDestinationCostMatrix_na", params, ctx, add_outputs_to_map=True
    )
