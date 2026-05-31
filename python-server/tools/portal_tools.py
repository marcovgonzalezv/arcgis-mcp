import json
import urllib.parse
import urllib.request
from typing import Any

from mcp.server.fastmcp import Context
from pipe_client import ArcGisPipeClient

client = ArcGisPipeClient()
_portal_session = {"portal_url": "https://www.arcgis.com", "token": ""}


def _portal_url(portal_url: str = "") -> str:
    base = portal_url or _portal_session["portal_url"]
    return base.rstrip("/")


def _request_json(
    url: str, params: dict[str, Any], timeout: int = 30
) -> dict[str, Any]:
    query = urllib.parse.urlencode(params)
    with urllib.request.urlopen(f"{url}?{query}", timeout=timeout) as response:
        payload = response.read().decode("utf-8")
    data = json.loads(payload)
    if "error" in data:
        error = data["error"]
        raise RuntimeError(error.get("message", str(error)))
    return data


def connect_portal(portal_url: str, token: str = "", ctx: Context = None) -> str:
    """
    Stores a portal URL and optional token for subsequent REST calls.
    """
    if ctx:
        ctx.info(f"Connecting MCP REST session to portal '{portal_url}'...")
    _portal_session["portal_url"] = _portal_url(portal_url)
    _portal_session["token"] = token or ""
    return f"Portal REST session set to {_portal_session['portal_url']}."


def get_active_portal(ctx: Context = None) -> str:
    """
    Returns the active portal reported by ArcGIS Pro and the MCP REST session portal.
    """
    if ctx:
        ctx.info("Retrieving active ArcGIS Pro portal...")
    resp = client.send_command("get_active_portal")
    if resp.get("success"):
        data = resp.get("data", {})
        return (
            f"ArcGIS Pro active portal: {data.get('url', 'unknown')}\n"
            f"Signed in: {data.get('is_signed_in', False)}\n"
            f"User: {data.get('user', '')}\n"
            f"MCP REST portal: {_portal_session['portal_url']}"
        )
    return (
        f"ArcGIS Pro portal unavailable: {resp.get('message') or resp.get('error')}\n"
        f"MCP REST portal: {_portal_session['portal_url']}"
    )


def search_portal_items(
    query: str,
    max_items: int = 10,
    portal_url: str = "",
    token: str = "",
    ctx: Context = None,
) -> str:
    """
    Searches ArcGIS Online or ArcGIS Enterprise portal items.
    """
    if ctx:
        ctx.info(f"Searching portal items: {query}")
    params = {"f": "json", "q": query, "num": max(1, min(max_items, 100))}
    auth_token = token or _portal_session["token"]
    if auth_token:
        params["token"] = auth_token
    data = _request_json(f"{_portal_url(portal_url)}/sharing/rest/search", params)
    results = data.get("results", [])
    if not results:
        return "No portal items found."
    lines = ["Portal items:"]
    for item in results:
        lines.append(
            f"- {item.get('title')} | {item.get('type')} | "
            f"id={item.get('id')} | owner={item.get('owner')}"
        )
    return "\n".join(lines)


def describe_portal_item(
    item_id: str, portal_url: str = "", token: str = "", ctx: Context = None
) -> str:
    """
    Describes a portal item by item id.
    """
    if ctx:
        ctx.info(f"Describing portal item '{item_id}'...")
    params = {"f": "json"}
    auth_token = token or _portal_session["token"]
    if auth_token:
        params["token"] = auth_token
    item = _request_json(
        f"{_portal_url(portal_url)}/sharing/rest/content/items/{item_id}", params
    )
    return json.dumps(item, ensure_ascii=False, indent=2)


def publish_web_layer(
    service_definition_path: str,
    server_connection: str = "My Hosted Services",
    service_name: str = "",
    folder_type: str = "",
    folder: str = "",
    startup_type: str = "",
    override_definition: str = "",
    my_contents: str = "",
    public_share: str = "",
    organization: str = "",
    groups: str = "",
    ctx: Context = None,
) -> str:
    """
    Publishes an ArcGIS .sd file or stages and publishes an .sddraft file.
    """
    if ctx:
        ctx.info(f"Publishing service definition '{service_definition_path}'...")
    resp = client.send_command(
        "publish_web_layer",
        {
            "service_definition_path": service_definition_path,
            "server_connection": server_connection,
            "service_name": service_name,
            "folder_type": folder_type,
            "folder": folder,
            "startup_type": startup_type,
            "override_definition": override_definition,
            "my_contents": my_contents,
            "public_share": public_share,
            "organization": organization,
            "groups": groups,
        },
        timeout_ms=600000,
        retries=0,
    )
    if resp.get("success"):
        return json.dumps(resp.get("data", {}), ensure_ascii=False, indent=2)
    return f"Error publishing web layer: {resp.get('message') or resp.get('error')}"


def stage_service_definition(
    service_draft_path: str,
    output_service_definition_path: str = "",
    ctx: Context = None,
) -> str:
    """
    Stages an ArcGIS service definition draft (.sddraft) into a service definition (.sd).
    """
    if ctx:
        ctx.info(f"Staging service definition draft '{service_draft_path}'...")
    resp = client.send_command(
        "stage_service_definition",
        {
            "service_draft_path": service_draft_path,
            "output_service_definition_path": output_service_definition_path,
        },
        timeout_ms=600000,
        retries=0,
    )
    if resp.get("success"):
        return json.dumps(resp.get("data", {}), ensure_ascii=False, indent=2)
    return (
        f"Error staging service definition: {resp.get('message') or resp.get('error')}"
    )
