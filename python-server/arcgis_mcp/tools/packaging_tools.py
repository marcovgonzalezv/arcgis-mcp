"""
Packaging and sharing wrappers.

These wrap the Server and Data Management packaging tools so the caller can
consolidate projects, layers and maps into portable packages, plus extend the
existing portal publishing tools with geocoding.
"""

from mcp.server.fastmcp import Context

from .geoprocessing_tools import run_gp_tool


def package_map(
    in_map: str,
    output_file: str,
    convert_data: str = "CONVERT",
    convert_arcsddata: str = "CONVERT_ARCSDE",
    extent: str = "",
    apply_extent_to_arcsde: str = "ALL",
    ctx: Context = None,
) -> str:
    """
    Consolidates a map and all referenced data sources into a .mpkx package.
    """
    params = [in_map, output_file, convert_data, convert_arcsddata]
    if extent:
        params.append(extent)
        params.append(apply_extent_to_arcsde)
    return run_gp_tool("PackageMap_management", params, ctx, add_outputs_to_map=False)


def package_project(
    in_project: str,
    output_file: str,
    external_data: str = "EMBED",
    convert_to_arcgispro: str = "CONVERT_TO_ARGISPRO",
    ctx: Context = None,
) -> str:
    """
    Consolidates a project (.aprx) and its data into a portable .ppkx package.
    """
    return run_gp_tool(
        "PackageProject_management",
        [in_project, output_file, external_data, convert_to_arcgispro],
        ctx,
        add_outputs_to_map=False,
    )


def package_layer(
    in_layer: str,
    output_file: str,
    convert_data: str = "CONVERT",
    convert_arcsddata: str = "CONVERT_ARCSDE",
    extent: str = "",
    package_version: str = "",
    ctx: Context = None,
) -> str:
    """
    Packages a layer and its data into a single compressed .lpkx file.
    """
    params = [in_layer, output_file, convert_data, convert_arcsddata]
    if extent:
        params.append(extent)
    if package_version:
        params.append(package_version)
    return run_gp_tool("PackageLayer_management", params, ctx, add_outputs_to_map=False)


def create_mobile_map_package(
    in_map: list,
    output_file: str,
    in_location: list | None = None,
    area_of_interest: str = "",
    extent: str = "",
    ctx: Context = None,
) -> str:
    """
    Packages one or more maps for offline use in the Field Maps / Navigator
    apps into a .mmpk file.
    """
    params = [in_map, output_file]
    if in_location:
        params.append(in_location)
    if area_of_interest:
        params.append(area_of_interest)
    if extent:
        params.append(extent)
    return run_gp_tool(
        "CreateMobileMapPackage_management", params, ctx, add_outputs_to_map=False
    )


def create_vector_tile_package(
    in_map: str,
    output_file: str,
    service_type: str = "EXISTING",
    tiling_scheme: str = "",
    ctx: Context = None,
) -> str:
    """
    Creates a vector tile package (.vtpk) from a map.
    """
    params = [in_map, output_file, service_type]
    if tiling_scheme:
        params.append(tiling_scheme)
    return run_gp_tool(
        "CreateVectorTilePackage_management", params, ctx, add_outputs_to_map=False
    )


def share_package(
    package_path: str, summary: str = "", tags: list | None = None, ctx: Context = None
) -> str:
    """
    Shares a package (.mpkx, .lpkx, .ppkx, .mmpk, .vtpk) to ArcGIS Online or
    ArcGIS Enterprise portal.
    """
    params = [package_path]
    if summary:
        params.append(summary)
    if tags:
        params.append(tags)
    return run_gp_tool("SharePackage_management", params, ctx, add_outputs_to_map=False)


def consolidate_project(
    in_project: str,
    output_folder: str,
    external_data: str = "EMBED",
    convert_to_arcgispro: str = "CONVERT_TO_ARGISPRO",
    ctx: Context = None,
) -> str:
    """
    Consolidates a project and its data into a folder (no compression).
    """
    return run_gp_tool(
        "ConsolidateProject_management",
        [in_project, output_folder, external_data, convert_to_arcgispro],
        ctx,
        add_outputs_to_map=False,
    )


def replace_web_layer(
    in_sd_file: str,
    replace_layers: str = "REPLACE_ALL",
    edit_properties: str = "REPLACE",
    ctx: Context = None,
) -> str:
    """
    Replaces the layers and data of an existing web layer with an updated
    service definition (.sd) file.
    """
    return run_gp_tool(
        "ReplaceWebLayer_server",
        [in_sd_file, replace_layers, edit_properties],
        ctx,
        add_outputs_to_map=False,
    )
