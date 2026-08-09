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
        public const string AddinVersion = "0.6.0";
        public const string McpVersion = "0.6.0";

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
            "add_layer_to_group",
            "apply_graduated_symbology",
            "apply_raster_colorizer",
            "apply_symbology_from_layer",
            "apply_unique_value_symbology",
            "check_license",
            "clear_selection",
            "count_features",
            "create_basic_layout",
            "create_domain",
            "create_feature",
            "create_group_layer",
            "create_map_series",
            "create_bookmark",
            "delete_bookmark",
            "delete_selected_features",
            "delete_features",
            "describe_dataset",
            "export_active_map",
            "export_all_layouts",
            "export_layer",
            "export_layout",
            "export_map_series",
            "geometry_area",
            "geometry_contains",
            "geometry_intersects",
            "geometry_length",
            "geometry_within_distance",
            "get_active_map",
            "get_active_portal",
            "get_capabilities",
            "get_layer_fields",
            "get_layer_symbology",
            "get_selected_features",
            "health_check",
            "insert_features",
            "label_layer",
            "list_bookmarks",
            "list_domains",
            "list_feature_classes",
            "list_layers",
            "list_layouts",
            "list_maps",
            "list_project_items",
            "load_layer_file",
            "measure_distance",
            "open_map",
            "ping",
            "publish_web_layer",
            "query_layer",
            "remove_layer",
            "run_gp_tool",
            "save_layer_file",
            "save_project",
            "save_project_as",
            "select_features",
            "set_camera_3d",
            "set_definition_query",
            "set_layer_symbol",
            "set_layer_transparency",
            "set_map_extent",
            "stage_service_definition",
            "toggle_layer_visibility",
            "undo_last_edit",
            "update_attributes",
            "update_features",
            "update_layout_element",
            "zoom_to_bookmark",
            "zoom_to_layer"
        };
    }

    public static class ToolNames
    {
        public static readonly IReadOnlyList<string> All = CommandNames.All
            .Where(command => !command.Equals("ping", StringComparison.OrdinalIgnoreCase))
            .Concat(new[]
            {
                // Python-only wrappers (delegate to run_gp_tool or to another
                // Add-In command). These are not Add-In commands themselves.
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
                "update_class_breaks",
                // Conversion wrappers
                "excel_to_table",
                "table_to_excel",
                "kml_to_layer",
                "layer_to_kml",
                "features_to_json",
                "json_to_features",
                "raster_to_polygon",
                "polygon_to_raster",
                "point_to_raster",
                "export_features",
                "export_table",
                "feature_class_to_shapefile",
                "cad_to_geodatabase",
                "bim_to_geodatabase",
                // Analysis wrappers
                "dissolve",
                "intersect",
                "union",
                "erase",
                "merge",
                "append",
                "near",
                "generate_near_table",
                "select_layer_by_location",
                "summary_statistics",
                "frequency",
                "multiple_ring_buffer",
                "split",
                "select",
                "table_select",
                // Data management wrappers
                "calculate_field",
                "add_field",
                "delete_field",
                "project",
                "define_projection",
                "copy_features",
                "copy_rows",
                "get_count",
                "delete",
                "rename",
                "create_feature_class",
                "create_table",
                "repair_geometry",
                "check_geometry",
                "find_identical",
                "make_feature_layer",
                "make_table_view",
                "add_join",
                "remove_join",
                "create_file_gdb",
                "add_subtypes",
                // Network Analyst wrappers (require extension)
                "find_routes",
                "generate_service_areas",
                "find_closest_facilities",
                "generate_od_cost_matrix",
                // Spatial Analyst wrappers (require extension)
                "slope",
                "aspect",
                "hillshade",
                "reclassify",
                "raster_calculator",
                "kernel_density",
                "extract_by_mask",
                "weighted_overlay",
                // Spatial statistics wrappers
                "hot_spot_analysis",
                "cluster_and_outlier_analysis",
                "optimized_hot_spot_analysis",
                "emerging_hot_spot_analysis",
                "geographically_weighted_regression",
                "generalized_linear_regression",
                "spatial_autocorrelation",
                // Packaging and geocoding wrappers
                "package_map",
                "package_project",
                "package_layer",
                "create_mobile_map_package",
                "create_vector_tile_package",
                "share_package",
                "consolidate_project",
                "replace_web_layer",
                "geocode_addresses",
                "reverse_geocode",
                "create_locator",
                "rematch_addresses",
                // Topology wrappers (Python wrappers over run_gp_tool)
                "create_topology",
                "add_feature_class_to_topology",
                "add_rule_to_topology",
                "validate_topology"
            })
            .Distinct(StringComparer.OrdinalIgnoreCase)
            .ToList();
    }
}
