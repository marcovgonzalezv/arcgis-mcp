import re
import urllib.parse
from pathlib import Path

from mcp.server.fastmcp import Context

DOC_ROOTS = [
    Path(r"C:\Program Files\ArcGIS\Pro\bin"),
    Path(r"C:\Program Files\ArcGIS\Pro\bin\Extensions"),
]


def search_arcgis_docs(query: str, max_results: int = 10, ctx: Context = None) -> str:
    """
    Searches local ArcGIS Pro XML SDK documentation and returns online doc links.
    """
    if ctx:
        ctx.info(f"Searching ArcGIS documentation for '{query}'...")
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    results = []
    for root in DOC_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*.xml"):
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            match = pattern.search(text)
            if not match:
                continue
            start = max(0, match.start() - 120)
            end = min(len(text), match.end() + 240)
            snippet = re.sub(r"\s+", " ", text[start:end]).strip()
            results.append((path, snippet))
            if len(results) >= max_results:
                break
        if len(results) >= max_results:
            break

    lines = ["Local ArcGIS SDK documentation results:"]
    if results:
        for path, snippet in results:
            lines.append(f"- {path}: {snippet}")
    else:
        lines.append("- No local matches found.")

    encoded = urllib.parse.quote_plus(query)
    lines.extend(
        [
            "Online documentation searches:",
            f"- ArcGIS Pro SDK: https://github.com/Esri/arcgis-pro-sdk/wiki?search={encoded}",
            f"- ArcPy: https://pro.arcgis.com/en/pro-app/latest/arcpy/search.htm?q={encoded}",
            f"- ArcGIS REST API: https://developers.arcgis.com/rest/?q={encoded}",
        ]
    )
    return "\n".join(lines)
