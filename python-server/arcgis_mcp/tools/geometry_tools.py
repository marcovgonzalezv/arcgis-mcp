"""
Direct GeometryEngine wrappers.

These run spatial operations in-process via the ArcGIS Pro SDK
``GeometryEngine`` instead of geoprocessing tools, so they are much faster for
single-feature queries. They operate on the first selected feature of each
named layer.
"""

from mcp.server.fastmcp import Context

from ..pipe_client import ArcGisPipeClient

client = ArcGisPipeClient()


def _send(command: str, params: dict, ctx: Context = None, info: str = "") -> str:
    if ctx and info:
        ctx.info(info)
    resp = client.send_command(command, params)
    if resp.get("success"):
        data = resp.get("data", {}) or {}
        return f"{command}: {data}"
    error = resp.get("message") or resp.get("error")
    return f"Error in {command}: {error}"


def measure_distance(layer_a: str, layer_b: str, ctx: Context = None) -> str:
    """
    Returns the geodesic distance (meters) between the first selected feature
    of ``layer_a`` and the first selected feature of ``layer_b``.
    """
    return _send(
        "measure_distance",
        {"layer_a": layer_a, "layer_b": layer_b},
        ctx,
        f"Measuring distance between '{layer_a}' and '{layer_b}'...",
    )


def geometry_contains(layer_a: str, layer_b: str, ctx: Context = None) -> str:
    """
    Returns True if the selected feature of ``layer_a`` contains the selected
    feature of ``layer_b``.
    """
    return _send(
        "geometry_contains",
        {"layer_a": layer_a, "layer_b": layer_b},
        ctx,
        f"Testing containment '{layer_a}' contains '{layer_b}'...",
    )


def geometry_intersects(layer_a: str, layer_b: str, ctx: Context = None) -> str:
    """
    Returns True if the two selected geometries intersect.
    """
    return _send(
        "geometry_intersects",
        {"layer_a": layer_a, "layer_b": layer_b},
        ctx,
        f"Testing intersection '{layer_a}' vs '{layer_b}'...",
    )


def geometry_within_distance(
    layer_a: str, layer_b: str, distance: float, ctx: Context = None
) -> str:
    """
    Returns True if the two selected geometries are within ``distance`` map
    units of each other.
    """
    return _send(
        "geometry_within_distance",
        {"layer_a": layer_a, "layer_b": layer_b, "distance": distance},
        ctx,
        f"Testing proximity '{layer_a}' vs '{layer_b}' within {distance}...",
    )


def geometry_area(layer_name: str, ctx: Context = None) -> str:
    """
    Returns the area of the first selected polygon feature in ``layer_name``.
    """
    return _send(
        "geometry_area",
        {"layer_name": layer_name},
        ctx,
        f"Measuring area of '{layer_name}'...",
    )


def geometry_length(layer_name: str, ctx: Context = None) -> str:
    """
    Returns the length of the first selected polyline feature in ``layer_name``.
    """
    return _send(
        "geometry_length",
        {"layer_name": layer_name},
        ctx,
        f"Measuring length of '{layer_name}'...",
    )


def set_camera_3d(
    heading: float,
    pitch: float,
    roll: float = 0,
    scale: float = 0,
    ctx: Context = None,
) -> str:
    """
    Sets the camera orientation of the active view (3D scenes). Useful for
    panning/tilting a scene programmatically.
    heading: 0-360 degrees (compass direction).
    pitch: -90 (looking down) to 90 (looking up).
    """
    params = {"heading": heading, "pitch": pitch}
    if roll:
        params["roll"] = roll
    if scale:
        params["scale"] = scale
    return _send(
        "set_camera_3d",
        params,
        ctx,
        f"Setting camera heading={heading} pitch={pitch}...",
    )
