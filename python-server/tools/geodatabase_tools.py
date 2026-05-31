from mcp.server.fastmcp import Context
from pipe_client import ArcGisPipeClient

client = ArcGisPipeClient()


def list_feature_classes(workspace_path: str, ctx: Context = None) -> str:
    """
    Lists feature classes in a file geodatabase.
    """
    if ctx:
        ctx.info(f"Listing feature classes in '{workspace_path}'...")
    resp = client.send_command(
        "list_feature_classes", {"workspace_path": workspace_path}
    )
    if not resp.get("success"):
        return (
            f"Error listing feature classes: {resp.get('message') or resp.get('error')}"
        )
    items = resp.get("data", {}).get("feature_classes", [])
    return (
        "\n".join(["Feature classes:"] + [f"- {item}" for item in items])
        if items
        else "No feature classes found."
    )


def list_domains(workspace_path: str, ctx: Context = None) -> str:
    """
    Lists domains in a file geodatabase.
    """
    if ctx:
        ctx.info(f"Listing domains in '{workspace_path}'...")
    resp = client.send_command("list_domains", {"workspace_path": workspace_path})
    if not resp.get("success"):
        return f"Error listing domains: {resp.get('message') or resp.get('error')}"
    domains = resp.get("data", {}).get("domains", [])
    return (
        "\n".join(
            ["Domains:"] + [f"- {d.get('name')} | {d.get('type')}" for d in domains]
        )
        if domains
        else "No domains found."
    )


def create_domain(
    workspace_path: str,
    domain_name: str,
    field_type: str = "TEXT",
    domain_type: str = "CODED",
    description: str = "",
    ctx: Context = None,
) -> str:
    """
    Creates a geodatabase domain using ArcGIS geoprocessing.
    """
    if ctx:
        ctx.info(f"Creating domain '{domain_name}'...")
    resp = client.send_command(
        "create_domain",
        {
            "workspace_path": workspace_path,
            "domain_name": domain_name,
            "field_type": field_type,
            "domain_type": domain_type,
            "description": description,
        },
        timeout_ms=60000,
    )
    if resp.get("success"):
        return f"Domain '{domain_name}' created."
    return f"Error creating domain: {resp.get('message') or resp.get('error')}"


def describe_dataset(dataset_path: str, ctx: Context = None) -> str:
    """
    Describes an active-map layer or geodatabase dataset.
    """
    if ctx:
        ctx.info(f"Describing dataset '{dataset_path}'...")
    resp = client.send_command("describe_dataset", {"dataset_path": dataset_path})
    if not resp.get("success"):
        return f"Error describing dataset: {resp.get('message') or resp.get('error')}"
    data = resp.get("data", {})
    lines = [
        f"Name: {data.get('name', '')}",
        f"Type: {data.get('type', '')}",
        f"Path: {data.get('path', '')}",
        f"Geometry: {data.get('geometry_type', '')}",
        f"Count: {data.get('count', '')}",
        "Fields:",
    ]
    lines.extend(
        f"- {f.get('name')} | {f.get('type')} | {f.get('alias', '')}"
        for f in data.get("fields", [])
    )
    return "\n".join(lines)
