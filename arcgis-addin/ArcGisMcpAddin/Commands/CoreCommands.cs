using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Threading.Tasks;
using ArcGIS.Desktop.Core;
using ArcGIS.Desktop.Framework.Threading.Tasks;
using ArcGIS.Desktop.Mapping;

namespace ArcGisMcpAddin.Commands
{
    public static class CoreCommands
    {
        public const string AddinVersion = "0.3.0";
        public const string McpVersion = "0.3.0";

        public static Task<object> HealthCheckAsync()
        {
            return QueuedTask.Run<object>(() =>
            {
                var activeView = MapView.Active;
                var project = Project.Current;
                return new
                {
                    mcp_version = McpVersion,
                    addin_version = AddinVersion,
                    arcgis_pro_active = true,
                    arcgis_pro_version = Assembly.GetEntryAssembly()?.GetName().Version?.ToString() ?? "unknown",
                    project_open = project != null,
                    project_name = project?.Name ?? "",
                    project_path = project?.Path ?? "",
                    map_active = activeView?.Map != null,
                    active_map = activeView?.Map?.Name ?? "",
                    pipe = "available"
                };
            });
        }

        public static Task<object> GetCapabilitiesAsync()
        {
            return Task.FromResult<object>(new
            {
                mcp_version = McpVersion,
                addin_version = AddinVersion,
                addin_commands = CommandNames.All.OrderBy(value => value).ToList(),
                mcp_tools = ToolNames.All.OrderBy(value => value).ToList(),
                mcp_tool_count = ToolNames.All.Count,
                addin_command_count = CommandNames.All.Count
            });
        }
    }

    public static class CommandNames
    {
        public static readonly IReadOnlyList<string> All = new List<string>
        {
            "add_dynamic_text",
            "add_layer_to_map",
            "apply_graduated_symbology",
            "apply_raster_colorizer",
            "apply_symbology_from_layer",
            "apply_unique_value_symbology",
            "clear_selection",
            "count_features",
            "create_basic_layout",
            "create_domain",
            "create_feature",
            "create_map_series",
            "delete_selected_features",
            "describe_dataset",
            "export_active_map",
            "export_layer",
            "export_layout",
            "export_map_series",
            "get_active_map",
            "get_active_portal",
            "get_capabilities",
            "get_layer_fields",
            "get_layer_symbology",
            "get_selected_features",
            "health_check",
            "label_layer",
            "list_bookmarks",
            "list_domains",
            "list_feature_classes",
            "list_layers",
            "list_layouts",
            "list_maps",
            "list_project_items",
            "load_layer_file",
            "open_map",
            "ping",
            "publish_web_layer",
            "remove_layer",
            "run_gp_tool",
            "save_layer_file",
            "save_project",
            "save_project_as",
            "select_features",
            "set_definition_query",
            "set_layer_transparency",
            "set_map_extent",
            "stage_service_definition",
            "toggle_layer_visibility",
            "undo_last_edit",
            "update_attributes",
            "update_layout_element",
            "zoom_to_layer"
        };
    }

    public static class ToolNames
    {
        public static readonly IReadOnlyList<string> All = CommandNames.All
            .Where(command => !command.Equals("ping", StringComparison.OrdinalIgnoreCase))
            .Concat(new[]
            {
                "buffer_analysis",
                "clip_analysis",
                "connect_portal",
                "describe_portal_item",
                "export_service_geojson",
                "get_layer_schema",
                "get_service_layers",
                "query_feature_service",
                "search_arcgis_docs",
                "search_portal_items",
                "spatial_join",
                "update_class_breaks"
            })
            .Distinct(StringComparer.OrdinalIgnoreCase)
            .ToList();
    }
}
