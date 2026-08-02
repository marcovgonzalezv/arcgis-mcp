import json
import os
import urllib.parse
import urllib.request
from typing import Any

from mcp.server.fastmcp import Context


def _request_json(
    url: str, params: dict[str, Any], timeout: int = 60
) -> dict[str, Any]:
    query = urllib.parse.urlencode(params)
    with urllib.request.urlopen(
        f"{url.rstrip('/')}?{query}", timeout=timeout
    ) as response:
        payload = response.read().decode("utf-8")
    data = json.loads(payload)
    if "error" in data:
        error = data["error"]
        raise RuntimeError(error.get("message", str(error)))
    return data


def get_service_layers(service_url: str, token: str = "", ctx: Context = None) -> str:
    """
    Lists layers and tables exposed by an ArcGIS FeatureServer or MapServer.
    """
    if ctx:
        ctx.info(f"Listing service layers for '{service_url}'...")
    params = {"f": "json"}
    if token:
        params["token"] = token
    data = _request_json(service_url, params)
    lines = ["Service layers:"]
    for layer in data.get("layers", []):
        lines.append(
            f"- layer {layer.get('id')}: {layer.get('name')} ({layer.get('type', 'Layer')})"
        )
    for table in data.get("tables", []):
        lines.append(
            f"- table {table.get('id')}: {table.get('name')} ({table.get('type', 'Table')})"
        )
    return "\n".join(lines) if len(lines) > 1 else "No layers or tables found."


def get_layer_schema(layer_url: str, token: str = "", ctx: Context = None) -> str:
    """
    Returns schema metadata for a FeatureServer layer URL.
    """
    if ctx:
        ctx.info(f"Retrieving layer schema for '{layer_url}'...")
    params = {"f": "json"}
    if token:
        params["token"] = token
    data = _request_json(layer_url, params)
    fields = data.get("fields", [])
    lines = [
        f"Layer: {data.get('name', '')}",
        f"Geometry: {data.get('geometryType', '')}",
        f"Object ID field: {data.get('objectIdField', '')}",
        "Fields:",
    ]
    lines.extend(
        f"- {f.get('name')} | {f.get('type')} | {f.get('alias', '')}" for f in fields
    )
    return "\n".join(lines)


def query_feature_service(
    layer_url: str,
    where: str = "1=1",
    out_fields: str = "*",
    max_records: int = 100,
    token: str = "",
    ctx: Context = None,
) -> str:
    """
    Queries a FeatureServer layer and returns JSON features.
    """
    if ctx:
        ctx.info(f"Querying feature service layer '{layer_url}'...")
    params = {
        "f": "json",
        "where": where,
        "outFields": out_fields,
        "returnGeometry": "true",
        "resultRecordCount": max(1, min(max_records, 2000)),
        "resultOffset": 0,
    }
    if token:
        params["token"] = token
    data = _query_all_features(layer_url, params, max_records)
    return json.dumps(data, ensure_ascii=False, indent=2)


def export_service_geojson(
    layer_url: str,
    output_path: str,
    where: str = "1=1",
    out_fields: str = "*",
    max_records: int = 2000,
    token: str = "",
    ctx: Context = None,
) -> str:
    """
    Exports a FeatureServer layer query result to GeoJSON.
    """
    if ctx:
        ctx.info(f"Exporting feature service layer to '{output_path}'...")
    params = {
        "f": "geojson",
        "where": where,
        "outFields": out_fields,
        "returnGeometry": "true",
        "resultRecordCount": max(1, min(max_records, 2000)),
        "resultOffset": 0,
    }
    if token:
        params["token"] = token
    data = _query_all_features(layer_url, params, max_records)
    payload = json.dumps(data, ensure_ascii=False)
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(payload)
    return f"GeoJSON exported to '{output_path}'."


def _query_all_features(
    layer_url: str, params: dict[str, Any], max_records: int
) -> dict[str, Any]:
    limit = max(1, max_records)
    page_size = max(1, min(limit, int(params.get("resultRecordCount", 2000))))
    merged: dict[str, Any] | None = None
    features: list[Any] = []
    offset = 0

    while len(features) < limit:
        page_params = dict(params)
        page_params["resultOffset"] = offset
        page_params["resultRecordCount"] = min(page_size, limit - len(features))
        page = _request_json(f"{layer_url.rstrip('/')}/query", page_params, timeout=120)

        if merged is None:
            merged = {key: value for key, value in page.items() if key != "features"}

        page_features = page.get("features", [])
        features.extend(page_features)
        if not page.get("exceededTransferLimit") or not page_features:
            break
        offset += len(page_features)

    if merged is None:
        merged = {}
    merged["features"] = features[:limit]
    merged["returnedFeatureCount"] = len(merged["features"])
    return merged
