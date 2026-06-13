import os


TRUTHY_VALUES = {"1", "true", "yes", "y", "on"}
DESTRUCTIVE_TOOL_TOKENS = ("delete", "truncate")
ALLOW_DELETE_ENV = "ARCGIS_MCP_ALLOW_DELETE"


class DestructiveOperationBlocked(ValueError):
    """Raised when a destructive geoprocessing tool is blocked."""


def is_destructive_tool(tool_name: str) -> bool:
    """
    Returns whether a geoprocessing tool name is considered destructive.
    """
    normalized = tool_name.lower()
    return any(token in normalized for token in DESTRUCTIVE_TOOL_TOKENS)


def deletion_allowed(allow_delete: bool = False) -> bool:
    """
    Returns whether destructive geoprocessing operations are explicitly allowed.
    """
    env_value = os.environ.get(ALLOW_DELETE_ENV, "").strip().lower()
    return allow_delete or env_value in TRUTHY_VALUES


def guard_destructive_tool(tool_name: str, allow_delete: bool = False) -> None:
    """
    Blocks destructive geoprocessing tools unless the caller opts in explicitly.
    """
    if is_destructive_tool(tool_name) and not deletion_allowed(allow_delete):
        raise DestructiveOperationBlocked(
            f"Blocked destructive geoprocessing tool '{tool_name}'. "
            f"Pass allow_delete=True or set {ALLOW_DELETE_ENV}=true to allow it."
        )
