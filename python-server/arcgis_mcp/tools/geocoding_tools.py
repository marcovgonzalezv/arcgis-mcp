"""
Geocoding wrappers.
"""

from mcp.server.fastmcp import Context

from .geoprocessing_tools import run_gp_tool


def geocode_addresses(
    in_table: str,
    address_fields: dict,
    in_address_locator: str,
    out_feature_class: str,
    out_relationship_type: str = "STATIC",
    ctx: Context = None,
) -> str:
    """
    Geocodes a table of addresses using a locator.
    address_fields: dict mapping locator input names to table field names,
    e.g. {"Address": "STREET", "City": "CITY", "ZIP": "POSTCODE"}.
    """
    fields = " ".join(f"'{k}' '{v}'" for k, v in address_fields.items()).strip()
    params = [
        in_table,
        fields,
        in_address_locator,
        out_feature_class,
        out_relationship_type,
    ]
    return run_gp_tool(
        "GeocodeAddresses_geocoding", params, ctx, add_outputs_to_map=True
    )


def reverse_geocode(
    in_features: str,
    in_address_locator: str,
    out_feature_class: str,
    address_type: str = "ADDRESS",
    ctx: Context = None,
) -> str:
    """
    Creates addresses from point locations (reverse geocoding).
    address_type: "ADDRESS", "POI", "INTERSECTION", "STREET_ADDRESS".
    """
    return run_gp_tool(
        "ReverseGeocode_geocoding",
        [in_features, in_address_locator, out_feature_class, address_type],
        ctx,
        add_outputs_to_map=True,
    )


def create_locator(
    reference_data: list,
    primary_table_info: dict,
    in_address_fields: dict,
    out_locator: str,
    language_code: str = "",
    ctx: Context = None,
) -> str:
    """
    Creates a geocoding locator from reference data.
    reference_data: list of {"role": "...", "dataset": "..."} entries.
    primary_table_info: {"primary_table": "...", "alias": "..."}.
    in_address_fields: e.g. {"Address": "STREET_NAME"}.
    """
    refs = ";".join(f"{r['dataset']} {r['role']}" for r in reference_data)
    fields = ";".join(f"{k} {v}" for k, v in in_address_fields.items())
    params = [refs, primary_table_info.get("alias", ""), fields, out_locator]
    if language_code:
        params.append(language_code)
    return run_gp_tool("CreateLocator_geocoding", params, ctx, add_outputs_to_map=False)


def rematch_addresses(
    in_geocoded_feature_class: str,
    in_address_locator: str,
    geocoding_options: str = "",
    ctx: Context = None,
) -> str:
    """
    Re-matches addresses in a geocoded feature class that were unmatched or
    tied.
    """
    params = [in_geocoded_feature_class, in_address_locator]
    if geocoding_options:
        params.append(geocoding_options)
    return run_gp_tool(
        "RematchAddresses_geocoding", params, ctx, add_outputs_to_map=False
    )
