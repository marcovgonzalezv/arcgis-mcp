"""
License and extension management for arcgis-mcp.

ArcGIS Pro ships in three base levels (Basic, Standard, Advanced) plus a set
of licensed extensions. Each wrapper that requires a particular extension or a
minimum base level must call :func:`require_license` (or :func:`require_level`)
before delegating to the Add-In. If the requested entitlement is not
available, a clear, actionable message is returned to the caller instead of a
cryptic geoprocessing error.

Availability is queried at runtime through the Add-In ``check_license``
command (which calls ``arcpy`` / the Pro SDK inside ArcGIS Pro). The Add-In
caches the result so repeat checks are cheap.
"""

from dataclasses import dataclass

from mcp.server.fastmcp import Context

from ..pipe_client import ArcGisPipeClient

client = ArcGisPipeClient()

# ------------------------------------------------------------------
# ArcPy product codes (as returned by arcpy.ProductInfo())
# ------------------------------------------------------------------
LEVEL_BASIC = "Basic"
LEVEL_STANDARD = "Standard"
LEVEL_ADVANCED = "Advanced"

# Ordered from least to most capable so a minimum-level check is a simple
# index comparison.
_LEVEL_ORDER = {LEVEL_BASIC: 1, LEVEL_STANDARD: 2, LEVEL_ADVANCED: 3}

# ------------------------------------------------------------------
# Extension catalogue.
#
# Each entry maps our canonical extension key to the metadata the Add-In
# needs to verify availability. ``arcpy_code`` is the value accepted by
# ``arcpy.CheckExtension`` / ``arcpy.CheckOutExtension`` and is the source of
# truth inside ArcGIS Pro. ``display_name`` is what we surface to the caller and
# the end user in error messages.
# Source: https://doc.esri.com/en/arcgis-pro/latest/arcpy/functions/checkextension.html
# ------------------------------------------------------------------


@dataclass(frozen=True)
class ExtensionInfo:
    key: str
    display_name: str
    arcpy_code: str


EXTENSIONS: dict[str, ExtensionInfo] = {
    ext.key: ext
    for ext in [
        ExtensionInfo("3d_analyst", "ArcGIS 3D Analyst", "3D"),
        ExtensionInfo("spatial_analyst", "ArcGIS Spatial Analyst", "Spatial"),
        ExtensionInfo("network_analyst", "ArcGIS Network Analyst", "Network"),
        ExtensionInfo(
            "geostatistical_analyst", "ArcGIS Geostatistical Analyst", "GeoStats"
        ),
        ExtensionInfo("image_analyst", "ArcGIS Image Analyst", "ImageAnalyst"),
        ExtensionInfo("data_reviewer", "ArcGIS Data Reviewer", "DataReviewer"),
        ExtensionInfo(
            "data_interoperability",
            "ArcGIS Data Interoperability",
            "DataInteroperability",
        ),
        ExtensionInfo("airports", "ArcGIS Aviation Airports", "Airports"),
        ExtensionInfo("aeronautical", "ArcGIS Aviation Charting", "Aeronautical"),
        ExtensionInfo("bathymetry", "ArcGIS Bathymetry", "Bathymetry"),
        ExtensionInfo("business_analyst", "ArcGIS Business Analyst", "BusinessPrem"),
        ExtensionInfo("defense_mapping", "ArcGIS Defense Mapping", "Defense"),
        ExtensionInfo("foundation", "ArcGIS Foundation", "Foundation"),
        ExtensionInfo("indoors", "ArcGIS Indoors", "Indoors"),
        ExtensionInfo(
            "location_referencing", "ArcGIS Location Referencing", "LocationReferencing"
        ),
        ExtensionInfo("locatext", "LocateXT", "LocateXT"),
        ExtensionInfo("maritime", "ArcGIS Maritime", "Nautical"),
        ExtensionInfo("publisher", "ArcGIS Publisher", "Publisher"),
        ExtensionInfo(
            "streetmap_north_america",
            "StreetMap Premium North America",
            "SMPNorthAmerica",
        ),
        ExtensionInfo("streetmap_europe", "StreetMap Premium Europe", "SMPEurope"),
        ExtensionInfo(
            "streetmap_asia_pacific", "StreetMap Premium Asia Pacific", "SMPAsiaPacific"
        ),
        ExtensionInfo("streetmap_japan", "StreetMap Premium Japan", "SMPJapan"),
        ExtensionInfo(
            "streetmap_latin_america",
            "StreetMap Premium Latin America",
            "SMPLatinAmerica",
        ),
        ExtensionInfo(
            "streetmap_middle_east_africa",
            "StreetMap Premium Middle East & Africa",
            "SMPMiddleEastAfrica",
        ),
        ExtensionInfo("arcscan", "ArcScan", "ArcScan"),
        ExtensionInfo("schematics", "ArcGIS Schematics", "Schematics"),
        ExtensionInfo("tracking_analyst", "ArcGIS Tracking Analyst", "Tracking"),
        ExtensionInfo("workflow_manager", "ArcGIS Workflow Manager (Classic)", "JTX"),
    ]
}


class LicenseError(RuntimeError):
    """Raised when a required license or extension is not available."""


# In-process cache so we do not hit the pipe for every wrapper call. The
# Add-In re-evaluates availability on demand when the cache is cold.
_cache: dict[str, dict] = {}


def _query_addin(ctx: Context = None) -> dict:
    """Ask the Add-In for the current license level and active extensions."""
    if "status" in _cache:
        return _cache["status"]

    resp = client.send_command("check_license", timeout_ms=15000)
    if resp.get("success"):
        data = resp.get("data", {}) or {}
        _cache["status"] = data
        return data

    # If the Add-In is unreachable we cannot make any guarantee; surface the
    # IPC error so the caller can decide. We do NOT cache failures.
    error = resp.get("message") or resp.get("error") or "IPC unavailable"
    raise LicenseError(
        f"Could not verify ArcGIS Pro license (Add-In unreachable): {error}"
    )


def check_license(ctx: Context = None) -> dict:
    """
    Public helper: returns the raw license status payload from the Add-In.
    Used by the ``check_license`` MCP tool.
    """
    _cache.clear()
    return _query_addin(ctx)


def require_level(minimum: str, ctx: Context = None) -> None:
    """
    Raise :class:`LicenseError` unless the active license level is at least
    ``minimum`` (Basic < Standard < Advanced).
    """
    status = _query_addin(ctx)
    current = status.get("level") or status.get("product") or LEVEL_BASIC
    if _LEVEL_ORDER.get(current, 0) < _LEVEL_ORDER[minimum]:
        raise LicenseError(
            f"This operation requires ArcGIS Pro {minimum} license level. "
            f"Current level is '{current}'. Upgrade your license to use it."
        )


def require_extension(key: str, ctx: Context = None) -> None:
    """
    Raise :class:`LicenseError` unless extension ``key`` is available.

    ``key`` is one of the canonical keys in :data:`EXTENSIONS`.
    """
    info = EXTENSIONS.get(key)
    if info is None:
        raise LicenseError(f"Unknown extension key '{key}'.")

    status = _query_addin(ctx)
    active = set(status.get("extensions") or [])
    if info.arcpy_code not in active:
        raise LicenseError(
            f"This operation requires the {info.display_name} extension "
            f"(code '{info.arcpy_code}'), which is not licensed or not "
            f"available in this ArcGIS Pro session."
        )


def get_license_status(ctx: Context = None) -> str:
    """
    Human-readable license status. Exposed as the ``check_license`` MCP tool.
    """
    try:
        status = check_license(ctx)
    except LicenseError as exc:
        return str(exc)

    level = status.get("level") or status.get("product") or "Unknown"
    active = sorted(status.get("extensions") or [])
    inactive = sorted(
        info.display_name
        for key, info in EXTENSIONS.items()
        if info.arcpy_code not in active
    )

    lines = [f"License level: {level}"]
    if active:
        lines.append("Available extensions:")
        for code in active:
            info = next((i for i in EXTENSIONS.values() if i.arcpy_code == code), None)
            label = info.display_name if info else code
            lines.append(f"  - {label} ({code})")
    else:
        lines.append("Available extensions: none")

    if inactive:
        lines.append("Not available extensions:")
        for name in inactive:
            lines.append(f"  - {name}")
    return "\n".join(lines)
