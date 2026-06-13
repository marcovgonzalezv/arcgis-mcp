from pipe_client import ArcGisPipeClient
from mcp.server.fastmcp import Context

client = ArcGisPipeClient()


def count_features(layer_name: str, sql_filter: str = "", ctx: Context = None) -> str:
    """
    Counts the number of features in a specified layer.
    Allows an optional SQL filter (definition query format, e.g., "POPULATION > 100000").
    """
    if ctx:
        ctx.info(f"Counting features in '{layer_name}' with filter '{sql_filter}'...")
    resp = client.send_command(
        "count_features", {"layer_name": layer_name, "sql_filter": sql_filter}
    )
    if resp.get("success"):
        count = resp.get("data", {}).get("count", 0)
        filter_msg = f" matching filter '{sql_filter}'" if sql_filter else ""
        return f"Layer '{layer_name}' has {count} features{filter_msg}."
    else:
        return f"Error counting features in '{layer_name}': {resp.get('error')}"


def select_features(
    layer_name: str,
    sql_filter: str,
    selection_combination: str = "NEW",
    ctx: Context = None,
) -> str:
    """
    Selects features in a specified layer using a SQL attribute query.
    selection_combination can be: "NEW", "ADD", "REMOVE", "SUBTRACT", "XOR".
    """
    if ctx:
        ctx.info(f"Selecting features in '{layer_name}' using query '{sql_filter}'...")
    resp = client.send_command(
        "select_features",
        {
            "layer_name": layer_name,
            "sql_filter": sql_filter,
            "combination": selection_combination,
        },
    )
    if resp.get("success"):
        count = resp.get("data", {}).get("count", 0)
        return f"Selected {count} features in layer '{layer_name}' using query '{sql_filter}'."
    else:
        return f"Error selecting features in '{layer_name}': {resp.get('error')}"


def get_selected_features(
    layer_name: str, max_features: int = 100, ctx: Context = None
) -> str:
    """
    Retrieves the attribute records for the currently selected features in a layer.
    Returns data as a formatted list (capped by max_features to prevent huge payloads).
    """
    if ctx:
        ctx.info(
            f"Retrieving selected features for '{layer_name}' (max {max_features})..."
        )
    resp = client.send_command(
        "get_selected_features",
        {"layer_name": layer_name, "max_features": max_features},
    )
    if resp.get("success"):
        features = resp.get("data", {}).get("features", [])
        if not features:
            return f"No selected features found in layer '{layer_name}'."

        result = [
            f"Selected features in '{layer_name}' (showing first {len(features)}):"
        ]
        for idx, feat in enumerate(features, 1):
            attr_strs = [f"{k}: {v}" for k, v in feat.items()]
            result.append(f"Feature {idx}: {', '.join(attr_strs)}")
        return "\n".join(result)
    else:
        return (
            f"Error retrieving selected features in '{layer_name}': {resp.get('error')}"
        )


def get_layer_fields(layer_name: str, ctx: Context = None) -> str:
    """
    Gets the schema/fields of a layer, listing names, aliases, and data types of all attributes.
    """
    if ctx:
        ctx.info(f"Retrieving schema for layer '{layer_name}'...")
    resp = client.send_command("get_layer_fields", {"layer_name": layer_name})
    if resp.get("success"):
        fields = resp.get("data", {}).get("fields", [])
        if not fields:
            return f"No fields found for layer '{layer_name}'."

        result = [f"Schema for layer '{layer_name}':"]
        for field in fields:
            result.append(
                f"- {field.get('name')} (Type: {field.get('type')}, Alias: {field.get('alias')})"
            )
        return "\n".join(result)
    else:
        return f"Error retrieving fields for layer '{layer_name}': {resp.get('error')}"


def query_layer(
    layer_name: str,
    where_clause: str = "1=1",
    fields: str = "*",
    limit: int = 100,
    include_geometry: bool = False,
    ctx: Context = None,
) -> str:
    """
    Queries attribute rows from an active-map feature layer.
    """
    if ctx:
        ctx.info(f"Querying layer '{layer_name}' with filter '{where_clause}'...")
    resp = client.send_command(
        "query_layer",
        {
            "layer_name": layer_name,
            "where_clause": where_clause,
            "fields": fields,
            "limit": limit,
            "include_geometry": include_geometry,
        },
        timeout_ms=30000,
    )
    if not resp.get("success"):
        return f"Error querying layer '{layer_name}': {resp.get('message') or resp.get('error')}"

    data = resp.get("data", {})
    rows = data.get("rows", [])
    if not rows:
        return f"No rows found in layer '{layer_name}' for filter '{where_clause}'."

    result = [
        f"Rows from '{layer_name}' (showing {len(rows)} of requested {data.get('limit', limit)}):"
    ]
    for idx, row in enumerate(rows, 1):
        values = [f"{key}: {value}" for key, value in row.items()]
        result.append(f"{idx}. {', '.join(values)}")
    if data.get("limited"):
        result.append("Result was limited; increase limit to inspect more rows.")
    return "\n".join(result)
