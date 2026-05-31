using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Text.Json;
using System.Threading.Tasks;
using ArcGisMcpAddin.Commands;

namespace ArcGisMcpAddin
{
    public static class CommandHandler
    {
        public static async Task<string> HandleAsync(string jsonRequest)
        {
            var stopwatch = Stopwatch.StartNew();
            try
            {
                using var doc = JsonDocument.Parse(jsonRequest);
                var root = doc.RootElement;

                if (!root.TryGetProperty("command", out var cmdProp) || cmdProp.GetString() == null)
                {
                    return SerializeError("Missing or invalid 'command' property in request.");
                }

                string command = cmdProp.GetString()!;
                JsonElement paramsEl = root.TryGetProperty("params", out var paramsProp) ? paramsProp : default;

                System.Diagnostics.Debug.WriteLine($"Processing MCP Command: {command}");

                object? resultData = null;

                switch (command)
                {
                    case "ping":
                        resultData = new { message = "pong", time = DateTime.Now.ToString("o") };
                        break;

                    case "health_check":
                        resultData = await CoreCommands.HealthCheckAsync();
                        break;

                    case "get_capabilities":
                        resultData = await CoreCommands.GetCapabilitiesAsync();
                        break;

                    case "list_maps":
                        resultData = await ProjectCommands.ListMapsAsync();
                        break;

                    case "open_map":
                        string? openMapName = paramsEl.TryGetProperty("map_name", out var omnProp) ? omnProp.GetString() : null;
                        if (string.IsNullOrEmpty(openMapName)) throw new ArgumentException("Parameter 'map_name' is required.");
                        resultData = await ProjectCommands.OpenMapAsync(openMapName);
                        break;

                    case "save_project_as":
                        string? saveAsPath = paramsEl.TryGetProperty("output_path", out var sapProp) ? sapProp.GetString() : null;
                        bool overwriteProject = paramsEl.TryGetProperty("overwrite", out var owProp) && owProp.GetBoolean();
                        if (string.IsNullOrEmpty(saveAsPath)) throw new ArgumentException("Parameter 'output_path' is required.");
                        resultData = await ProjectCommands.SaveProjectAsAsync(saveAsPath, overwriteProject);
                        break;

                    case "list_project_items":
                        resultData = await ProjectCommands.ListProjectItemsAsync();
                        break;

                    case "list_bookmarks":
                        string bookmarkMap = paramsEl.TryGetProperty("map_name", out var bmProp) ? bmProp.GetString() ?? "" : "";
                        resultData = await ProjectCommands.ListBookmarksAsync(bookmarkMap);
                        break;

                    // Map Commands
                    case "get_active_map":
                        resultData = await MapCommands.GetActiveMapAsync();
                        break;

                    case "list_layers":
                        bool includeHidden = paramsEl.ValueKind != JsonValueKind.Undefined &&
                                             paramsEl.TryGetProperty("include_hidden", out var ihProp) &&
                                             ihProp.GetBoolean();
                        resultData = await MapCommands.ListLayersAsync(includeHidden);
                        break;

                    case "zoom_to_layer":
                        string? layerToZoom = paramsEl.TryGetProperty("layer_name", out var lzProp) ? lzProp.GetString() : null;
                        if (string.IsNullOrEmpty(layerToZoom)) throw new ArgumentException("Parameter 'layer_name' is required.");
                        resultData = await MapCommands.ZoomToLayerAsync(layerToZoom);
                        break;

                    case "toggle_layer_visibility":
                        string? layerToToggle = paramsEl.TryGetProperty("layer_name", out var ltProp) ? ltProp.GetString() : null;
                        if (string.IsNullOrEmpty(layerToToggle)) throw new ArgumentException("Parameter 'layer_name' is required.");
                        if (!paramsEl.TryGetProperty("visible", out var vProp)) throw new ArgumentException("Parameter 'visible' is required.");
                        resultData = await MapCommands.ToggleLayerVisibilityAsync(layerToToggle, vProp.GetBoolean());
                        break;

                    case "set_map_extent":
                        double xmin = paramsEl.GetProperty("xmin").GetDouble();
                        double ymin = paramsEl.GetProperty("ymin").GetDouble();
                        double xmax = paramsEl.GetProperty("xmax").GetDouble();
                        double ymax = paramsEl.GetProperty("ymax").GetDouble();
                        int wkid = paramsEl.TryGetProperty("wkid", out var wkProp) ? wkProp.GetInt32() : 4326;
                        resultData = await MapCommands.SetMapExtentAsync(xmin, ymin, xmax, ymax, wkid);
                        break;

                    case "add_layer_to_map":
                        string? dataPath = paramsEl.TryGetProperty("data_path", out var dpProp) ? dpProp.GetString() : null;
                        string addLayerName = paramsEl.TryGetProperty("layer_name", out var alnProp) ? alnProp.GetString() ?? "" : "";
                        if (string.IsNullOrEmpty(dataPath)) throw new ArgumentException("Parameter 'data_path' is required.");
                        resultData = await MapCommands.AddLayerToMapAsync(dataPath, addLayerName);
                        break;

                    case "set_layer_transparency":
                        string? transparencyLayer = paramsEl.TryGetProperty("layer_name", out var tlProp) ? tlProp.GetString() : null;
                        if (string.IsNullOrEmpty(transparencyLayer)) throw new ArgumentException("Parameter 'layer_name' is required.");
                        double transparency = paramsEl.GetProperty("transparency").GetDouble();
                        resultData = await MapCommands.SetLayerTransparencyAsync(transparencyLayer, transparency);
                        break;

                    case "set_definition_query":
                        string? queryLayer = paramsEl.TryGetProperty("layer_name", out var qlProp) ? qlProp.GetString() : null;
                        string definitionSql = paramsEl.TryGetProperty("sql_filter", out var dqProp) ? dqProp.GetString() ?? "" : "";
                        if (string.IsNullOrEmpty(queryLayer)) throw new ArgumentException("Parameter 'layer_name' is required.");
                        resultData = await MapCommands.SetDefinitionQueryAsync(queryLayer, definitionSql);
                        break;

                    case "clear_selection":
                        string clearLayer = paramsEl.TryGetProperty("layer_name", out var cslProp) ? cslProp.GetString() ?? "" : "";
                        resultData = await MapCommands.ClearSelectionAsync(clearLayer);
                        break;

                    case "save_project":
                        resultData = await MapCommands.SaveProjectAsync();
                        break;

                    // Data Commands
                    case "count_features":
                        string? countLayer = paramsEl.TryGetProperty("layer_name", out var clProp) ? clProp.GetString() : null;
                        string sqlFilter = paramsEl.TryGetProperty("sql_filter", out var sfProp) ? sfProp.GetString() ?? "" : "";
                        if (string.IsNullOrEmpty(countLayer)) throw new ArgumentException("Parameter 'layer_name' is required.");
                        resultData = await DataCommands.CountFeaturesAsync(countLayer, sqlFilter);
                        break;

                    case "select_features":
                        string? selectLayer = paramsEl.TryGetProperty("layer_name", out var slProp) ? slProp.GetString() : null;
                        string selectSql = paramsEl.TryGetProperty("sql_filter", out var ssProp) ? ssProp.GetString() ?? "" : "";
                        string combo = paramsEl.TryGetProperty("combination", out var cProp) ? cProp.GetString() ?? "NEW" : "NEW";
                        if (string.IsNullOrEmpty(selectLayer)) throw new ArgumentException("Parameter 'layer_name' is required.");
                        if (string.IsNullOrEmpty(selectSql)) throw new ArgumentException("Parameter 'sql_filter' is required.");
                        resultData = await DataCommands.SelectFeaturesAsync(selectLayer, selectSql, combo);
                        break;

                    case "get_selected_features":
                        string? getSelLayer = paramsEl.TryGetProperty("layer_name", out var gslProp) ? gslProp.GetString() : null;
                        int maxFeatures = paramsEl.TryGetProperty("max_features", out var mfProp) ? mfProp.GetInt32() : 100;
                        if (string.IsNullOrEmpty(getSelLayer)) throw new ArgumentException("Parameter 'layer_name' is required.");
                        resultData = await DataCommands.GetSelectedFeaturesAsync(getSelLayer, maxFeatures);
                        break;

                    case "get_layer_fields":
                        string? fieldsLayer = paramsEl.TryGetProperty("layer_name", out var flProp) ? flProp.GetString() : null;
                        if (string.IsNullOrEmpty(fieldsLayer)) throw new ArgumentException("Parameter 'layer_name' is required.");
                        resultData = await DataCommands.GetLayerFieldsAsync(fieldsLayer);
                        break;

                    // Symbology and Labeling Commands
                    case "apply_graduated_symbology":
                        string? graduatedLayer = paramsEl.TryGetProperty("layer_name", out var glProp) ? glProp.GetString() : null;
                        string? graduatedField = paramsEl.TryGetProperty("field_name", out var gfProp) ? gfProp.GetString() : null;
                        int breakCount = paramsEl.TryGetProperty("break_count", out var bcProp) ? bcProp.GetInt32() : 5;
                        string classMethod = paramsEl.TryGetProperty("classification_method", out var cmProp) ? cmProp.GetString() ?? "NaturalBreaks" : "NaturalBreaks";
                        string gradRamp = paramsEl.TryGetProperty("color_ramp", out var grProp) ? grProp.GetString() ?? "Yellow-Orange-Red" : "Yellow-Orange-Red";
                        if (string.IsNullOrEmpty(graduatedLayer)) throw new ArgumentException("Parameter 'layer_name' is required.");
                        if (string.IsNullOrEmpty(graduatedField)) throw new ArgumentException("Parameter 'field_name' is required.");
                        resultData = await SymbologyCommands.ApplyGraduatedSymbologyAsync(graduatedLayer, graduatedField, breakCount, classMethod, gradRamp);
                        break;

                    case "apply_unique_value_symbology":
                        string? uniqueLayer = paramsEl.TryGetProperty("layer_name", out var ulProp) ? ulProp.GetString() : null;
                        string? uniqueField = paramsEl.TryGetProperty("field_name", out var ufProp) ? ufProp.GetString() : null;
                        string uniqueRamp = paramsEl.TryGetProperty("color_ramp", out var urProp) ? urProp.GetString() ?? "Default" : "Default";
                        int valuesLimit = paramsEl.TryGetProperty("values_limit", out var vlProp) ? vlProp.GetInt32() : 100;
                        if (string.IsNullOrEmpty(uniqueLayer)) throw new ArgumentException("Parameter 'layer_name' is required.");
                        if (string.IsNullOrEmpty(uniqueField)) throw new ArgumentException("Parameter 'field_name' is required.");
                        resultData = await SymbologyCommands.ApplyUniqueValueSymbologyAsync(uniqueLayer, uniqueField, uniqueRamp, valuesLimit);
                        break;

                    case "apply_symbology_from_layer":
                        string? targetLayer = paramsEl.TryGetProperty("target_layer", out var atlProp) ? atlProp.GetString() : null;
                        string? symbologyLayer = paramsEl.TryGetProperty("symbology_layer", out var aslProp) ? aslProp.GetString() : null;
                        if (string.IsNullOrEmpty(targetLayer)) throw new ArgumentException("Parameter 'target_layer' is required.");
                        if (string.IsNullOrEmpty(symbologyLayer)) throw new ArgumentException("Parameter 'symbology_layer' is required.");
                        resultData = await SymbologyCommands.ApplySymbologyFromLayerAsync(targetLayer, symbologyLayer);
                        break;

                    case "label_layer":
                        string? labelLayer = paramsEl.TryGetProperty("layer_name", out var llProp) ? llProp.GetString() : null;
                        string? labelField = paramsEl.TryGetProperty("field_name", out var lfProp) ? lfProp.GetString() : null;
                        bool labelVisible = !paramsEl.TryGetProperty("visible", out var lvProp) || lvProp.GetBoolean();
                        string labelEngine = paramsEl.TryGetProperty("expression_engine", out var leProp) ? leProp.GetString() ?? "Arcade" : "Arcade";
                        if (string.IsNullOrEmpty(labelLayer)) throw new ArgumentException("Parameter 'layer_name' is required.");
                        if (string.IsNullOrEmpty(labelField)) throw new ArgumentException("Parameter 'field_name' is required.");
                        resultData = await SymbologyCommands.LabelLayerAsync(labelLayer, labelField, labelVisible, labelEngine);
                        break;

                    case "get_layer_symbology":
                        string? symLayer = paramsEl.TryGetProperty("layer_name", out var symLayerProp) ? symLayerProp.GetString() : null;
                        if (string.IsNullOrEmpty(symLayer)) throw new ArgumentException("Parameter 'layer_name' is required.");
                        resultData = await SymbologyCommands.GetLayerSymbologyAsync(symLayer);
                        break;

                    case "apply_raster_colorizer":
                        string? rasterLayer = paramsEl.TryGetProperty("raster_layer", out var rlProp) ? rlProp.GetString() : null;
                        string rasterSymbology = paramsEl.TryGetProperty("symbology_layer", out var rslProp) ? rslProp.GetString() ?? "" : "";
                        string rasterRamp = paramsEl.TryGetProperty("color_ramp", out var rrProp) ? rrProp.GetString() ?? "Default" : "Default";
                        if (string.IsNullOrEmpty(rasterLayer)) throw new ArgumentException("Parameter 'raster_layer' is required.");
                        resultData = await SymbologyCommands.ApplyRasterColorizerAsync(rasterLayer, rasterSymbology, rasterRamp);
                        break;

                    // Layer IO Commands
                    case "save_layer_file":
                        string? saveLayer = paramsEl.TryGetProperty("layer_name", out var slfProp) ? slfProp.GetString() : null;
                        string? layerFileOut = paramsEl.TryGetProperty("output_path", out var lfoProp) ? lfoProp.GetString() : null;
                        if (string.IsNullOrEmpty(saveLayer)) throw new ArgumentException("Parameter 'layer_name' is required.");
                        if (string.IsNullOrEmpty(layerFileOut)) throw new ArgumentException("Parameter 'output_path' is required.");
                        resultData = await LayerIoCommands.SaveLayerFileAsync(saveLayer, layerFileOut);
                        break;

                    case "load_layer_file":
                        string? layerFilePath = paramsEl.TryGetProperty("layer_file_path", out var lfpProp) ? lfpProp.GetString() : null;
                        if (string.IsNullOrEmpty(layerFilePath)) throw new ArgumentException("Parameter 'layer_file_path' is required.");
                        resultData = await LayerIoCommands.LoadLayerFileAsync(layerFilePath);
                        break;

                    case "export_layer":
                        string? exportLayer = paramsEl.TryGetProperty("layer_name", out var elProp) ? elProp.GetString() : null;
                        string? exportOut = paramsEl.TryGetProperty("output_path", out var eoProp) ? eoProp.GetString() : null;
                        string whereClause = paramsEl.TryGetProperty("where_clause", out var wcProp) ? wcProp.GetString() ?? "" : "";
                        if (string.IsNullOrEmpty(exportLayer)) throw new ArgumentException("Parameter 'layer_name' is required.");
                        if (string.IsNullOrEmpty(exportOut)) throw new ArgumentException("Parameter 'output_path' is required.");
                        resultData = await LayerIoCommands.ExportLayerAsync(exportLayer, exportOut, whereClause);
                        break;

                    case "remove_layer":
                        string? removeLayer = paramsEl.TryGetProperty("layer_name", out var rmProp) ? rmProp.GetString() : null;
                        if (string.IsNullOrEmpty(removeLayer)) throw new ArgumentException("Parameter 'layer_name' is required.");
                        resultData = await LayerIoCommands.RemoveLayerAsync(removeLayer);
                        break;

                    // Geoprocessing Commands
                    case "run_gp_tool":
                        string? gpTool = paramsEl.TryGetProperty("tool_name", out var gptProp) ? gptProp.GetString() : null;
                        if (string.IsNullOrEmpty(gpTool)) throw new ArgumentException("Parameter 'tool_name' is required.");

                        var paramListProp = paramsEl.GetProperty("parameters");
                        string[] gpParams = new string[paramListProp.GetArrayLength()];
                        int index = 0;
                        foreach (var item in paramListProp.EnumerateArray())
                        {
                            gpParams[index++] = item.GetString() ?? "";
                        }
                        resultData = await GeoprocessingCommands.RunGpToolAsync(gpTool, gpParams);
                        break;

                    // Geodatabase Commands
                    case "list_feature_classes":
                        string? fcWorkspace = paramsEl.TryGetProperty("workspace_path", out var fcpProp) ? fcpProp.GetString() : null;
                        if (string.IsNullOrEmpty(fcWorkspace)) throw new ArgumentException("Parameter 'workspace_path' is required.");
                        resultData = await GeodatabaseCommands.ListFeatureClassesAsync(fcWorkspace);
                        break;

                    case "list_domains":
                        string? domainWorkspace = paramsEl.TryGetProperty("workspace_path", out var dwpProp) ? dwpProp.GetString() : null;
                        if (string.IsNullOrEmpty(domainWorkspace)) throw new ArgumentException("Parameter 'workspace_path' is required.");
                        resultData = await GeodatabaseCommands.ListDomainsAsync(domainWorkspace);
                        break;

                    case "create_domain":
                        string? createDomainWorkspace = paramsEl.TryGetProperty("workspace_path", out var cdwProp) ? cdwProp.GetString() : null;
                        string? domainName = paramsEl.TryGetProperty("domain_name", out var dnProp) ? dnProp.GetString() : null;
                        string fieldType = paramsEl.TryGetProperty("field_type", out var ftProp) ? ftProp.GetString() ?? "TEXT" : "TEXT";
                        string domainType = paramsEl.TryGetProperty("domain_type", out var dtProp) ? dtProp.GetString() ?? "CODED" : "CODED";
                        string domainDesc = paramsEl.TryGetProperty("description", out var ddProp) ? ddProp.GetString() ?? "" : "";
                        if (string.IsNullOrEmpty(createDomainWorkspace)) throw new ArgumentException("Parameter 'workspace_path' is required.");
                        if (string.IsNullOrEmpty(domainName)) throw new ArgumentException("Parameter 'domain_name' is required.");
                        resultData = await GeodatabaseCommands.CreateDomainAsync(createDomainWorkspace, domainName, fieldType, domainType, domainDesc);
                        break;

                    case "describe_dataset":
                        string? datasetPath = paramsEl.TryGetProperty("dataset_path", out var dsProp) ? dsProp.GetString() : null;
                        if (string.IsNullOrEmpty(datasetPath)) throw new ArgumentException("Parameter 'dataset_path' is required.");
                        resultData = await GeodatabaseCommands.DescribeDatasetAsync(datasetPath);
                        break;

                    // Editing Commands
                    case "update_attributes":
                        string? updateLayer = paramsEl.TryGetProperty("layer_name", out var uaLayerProp) ? uaLayerProp.GetString() : null;
                        long objectId = paramsEl.GetProperty("object_id").GetInt64();
                        var updateAttributes = DeserializeAttributes(paramsEl.GetProperty("attributes"));
                        if (string.IsNullOrEmpty(updateLayer)) throw new ArgumentException("Parameter 'layer_name' is required.");
                        resultData = await EditingCommands.UpdateAttributesAsync(updateLayer, objectId, updateAttributes);
                        break;

                    case "create_feature":
                        string? createLayer = paramsEl.TryGetProperty("layer_name", out var cfLayerProp) ? cfLayerProp.GetString() : null;
                        double createX = paramsEl.GetProperty("x").GetDouble();
                        double createY = paramsEl.GetProperty("y").GetDouble();
                        int createWkid = paramsEl.TryGetProperty("wkid", out var cwProp) ? cwProp.GetInt32() : 4326;
                        var createAttributes = paramsEl.TryGetProperty("attributes", out var caProp)
                            ? DeserializeAttributes(caProp)
                            : new Dictionary<string, object?>();
                        if (string.IsNullOrEmpty(createLayer)) throw new ArgumentException("Parameter 'layer_name' is required.");
                        resultData = await EditingCommands.CreateFeatureAsync(createLayer, createX, createY, createWkid, createAttributes);
                        break;

                    case "delete_selected_features":
                        string? deleteLayer = paramsEl.TryGetProperty("layer_name", out var dlfProp) ? dlfProp.GetString() : null;
                        if (string.IsNullOrEmpty(deleteLayer)) throw new ArgumentException("Parameter 'layer_name' is required.");
                        resultData = await EditingCommands.DeleteSelectedFeaturesAsync(deleteLayer);
                        break;

                    case "undo_last_edit":
                        resultData = await EditingCommands.UndoLastEditAsync();
                        break;

                    // Portal Commands
                    case "get_active_portal":
                        resultData = await PortalCommands.GetActivePortalAsync();
                        break;

                    case "publish_web_layer":
                        string? sdPath = paramsEl.TryGetProperty("service_definition_path", out var sdpProp) ? sdpProp.GetString() : null;
                        string serverConnection = paramsEl.TryGetProperty("server_connection", out var scProp) ? scProp.GetString() ?? "My Hosted Services" : "My Hosted Services";
                        string publishServiceName = paramsEl.TryGetProperty("service_name", out var psnProp) ? psnProp.GetString() ?? "" : "";
                        string publishFolderType = paramsEl.TryGetProperty("folder_type", out var pftProp) ? pftProp.GetString() ?? "" : "";
                        string publishFolder = paramsEl.TryGetProperty("folder", out var pfProp) ? pfProp.GetString() ?? "" : "";
                        string publishStartupType = paramsEl.TryGetProperty("startup_type", out var pstProp) ? pstProp.GetString() ?? "" : "";
                        string publishOverride = paramsEl.TryGetProperty("override_definition", out var podProp) ? podProp.GetString() ?? "" : "";
                        string publishMyContents = paramsEl.TryGetProperty("my_contents", out var pmcProp) ? pmcProp.GetString() ?? "" : "";
                        string publishPublic = paramsEl.TryGetProperty("public_share", out var ppsProp) ? ppsProp.GetString() ?? "" : "";
                        string publishOrganization = paramsEl.TryGetProperty("organization", out var poProp) ? poProp.GetString() ?? "" : "";
                        string publishGroups = paramsEl.TryGetProperty("groups", out var pgProp) ? pgProp.GetString() ?? "" : "";
                        if (string.IsNullOrEmpty(sdPath)) throw new ArgumentException("Parameter 'service_definition_path' is required.");
                        resultData = await PortalCommands.PublishWebLayerAsync(
                            sdPath,
                            serverConnection,
                            publishServiceName,
                            publishFolderType,
                            publishFolder,
                            publishStartupType,
                            publishOverride,
                            publishMyContents,
                            publishPublic,
                            publishOrganization,
                            publishGroups);
                        break;

                    case "stage_service_definition":
                        string? serviceDraftPath = paramsEl.TryGetProperty("service_draft_path", out var sdrProp) ? sdrProp.GetString() : null;
                        string outputServiceDefinitionPath = paramsEl.TryGetProperty("output_service_definition_path", out var osdProp) ? osdProp.GetString() ?? "" : "";
                        if (string.IsNullOrEmpty(serviceDraftPath)) throw new ArgumentException("Parameter 'service_draft_path' is required.");
                        resultData = await PortalCommands.StageServiceDefinitionAsync(serviceDraftPath, outputServiceDefinitionPath);
                        break;

                    // Layout Commands
                    case "list_layouts":
                        resultData = await LayoutCommands.ListLayoutsAsync();
                        break;

                    case "export_layout":
                        string? layoutName = paramsEl.TryGetProperty("layout_name", out var lnProp) ? lnProp.GetString() : null;
                        string? outPath = paramsEl.TryGetProperty("output_path", out var opProp) ? opProp.GetString() : null;
                        string format = paramsEl.TryGetProperty("format", out var fFormatProp) ? fFormatProp.GetString() ?? "PDF" : "PDF";
                        int dpi = paramsEl.TryGetProperty("resolution", out var resProp) ? resProp.GetInt32() : 300;

                        if (string.IsNullOrEmpty(layoutName)) throw new ArgumentException("Parameter 'layout_name' is required.");
                        if (string.IsNullOrEmpty(outPath)) throw new ArgumentException("Parameter 'output_path' is required.");
                        resultData = await LayoutCommands.ExportLayoutAsync(layoutName, outPath, format, dpi);
                        break;

                    case "create_basic_layout":
                        string? newLayoutName = paramsEl.TryGetProperty("layout_name", out var nlnProp) ? nlnProp.GetString() : null;
                        string layoutTitle = paramsEl.TryGetProperty("title", out var titleProp) ? titleProp.GetString() ?? "" : "";
                        double pageWidth = paramsEl.TryGetProperty("page_width", out var pwProp) ? pwProp.GetDouble() : 11.0;
                        double pageHeight = paramsEl.TryGetProperty("page_height", out var phProp) ? phProp.GetDouble() : 8.5;
                        if (string.IsNullOrEmpty(newLayoutName)) throw new ArgumentException("Parameter 'layout_name' is required.");
                        resultData = await LayoutCommands.CreateBasicLayoutAsync(newLayoutName, layoutTitle, pageWidth, pageHeight);
                        break;

                    case "export_active_map":
                        string? mapOutPath = paramsEl.TryGetProperty("output_path", out var mopProp) ? mopProp.GetString() : null;
                        string mapFormat = paramsEl.TryGetProperty("format", out var mapFormatProp) ? mapFormatProp.GetString() ?? "PNG" : "PNG";
                        int width = paramsEl.TryGetProperty("width", out var wProp) ? wProp.GetInt32() : 1920;
                        int height = paramsEl.TryGetProperty("height", out var hProp) ? hProp.GetInt32() : 1080;
                        int mapDpi = paramsEl.TryGetProperty("resolution", out var rdProp) ? rdProp.GetInt32() : 150;
                        if (string.IsNullOrEmpty(mapOutPath)) throw new ArgumentException("Parameter 'output_path' is required.");
                        resultData = await LayoutCommands.ExportActiveMapAsync(mapOutPath, mapFormat, width, height, mapDpi);
                        break;

                    case "create_map_series":
                        string? cmsLayout = paramsEl.TryGetProperty("layout_name", out var cmsLnProp) ? cmsLnProp.GetString() : null;
                        string? cmsMapFrame = paramsEl.TryGetProperty("map_frame_name", out var cmsMfProp) ? cmsMfProp.GetString() : null;
                        string? cmsIndexLayer = paramsEl.TryGetProperty("index_layer_name", out var cmsIlProp) ? cmsIlProp.GetString() : null;
                        string? cmsNameField = paramsEl.TryGetProperty("name_field", out var cmsNfProp) ? cmsNfProp.GetString() : null;
                        if (string.IsNullOrEmpty(cmsLayout)) throw new ArgumentException("Parameter 'layout_name' is required.");
                        if (string.IsNullOrEmpty(cmsMapFrame)) throw new ArgumentException("Parameter 'map_frame_name' is required.");
                        if (string.IsNullOrEmpty(cmsIndexLayer)) throw new ArgumentException("Parameter 'index_layer_name' is required.");
                        if (string.IsNullOrEmpty(cmsNameField)) throw new ArgumentException("Parameter 'name_field' is required.");
                        resultData = await LayoutCommands.CreateMapSeriesAsync(cmsLayout, cmsMapFrame, cmsIndexLayer, cmsNameField);
                        break;

                    case "export_map_series":
                        string? emsLayout = paramsEl.TryGetProperty("layout_name", out var emsLnProp) ? emsLnProp.GetString() : null;
                        string? emsOut = paramsEl.TryGetProperty("output_path", out var emsOutProp) ? emsOutProp.GetString() : null;
                        string emsFormat = paramsEl.TryGetProperty("format", out var emsFmtProp) ? emsFmtProp.GetString() ?? "PDF" : "PDF";
                        int emsDpi = paramsEl.TryGetProperty("resolution", out var emsDpiProp) ? emsDpiProp.GetInt32() : 300;
                        if (string.IsNullOrEmpty(emsLayout)) throw new ArgumentException("Parameter 'layout_name' is required.");
                        if (string.IsNullOrEmpty(emsOut)) throw new ArgumentException("Parameter 'output_path' is required.");
                        resultData = await LayoutCommands.ExportMapSeriesAsync(emsLayout, emsOut, emsFormat, emsDpi);
                        break;

                    case "add_dynamic_text":
                        string? adtLayout = paramsEl.TryGetProperty("layout_name", out var adtLnProp) ? adtLnProp.GetString() : null;
                        string adtText = paramsEl.TryGetProperty("text", out var adtTextProp) ? adtTextProp.GetString() ?? "" : "";
                        double adtX = paramsEl.TryGetProperty("x", out var adtXProp) ? adtXProp.GetDouble() : 0.5;
                        double adtY = paramsEl.TryGetProperty("y", out var adtYProp) ? adtYProp.GetDouble() : 0.5;
                        double adtWidth = paramsEl.TryGetProperty("width", out var adtWProp) ? adtWProp.GetDouble() : 4.0;
                        double adtHeight = paramsEl.TryGetProperty("height", out var adtHProp) ? adtHProp.GetDouble() : 0.5;
                        string adtElementName = paramsEl.TryGetProperty("element_name", out var adtEnProp) ? adtEnProp.GetString() ?? "MCP Dynamic Text" : "MCP Dynamic Text";
                        if (string.IsNullOrEmpty(adtLayout)) throw new ArgumentException("Parameter 'layout_name' is required.");
                        resultData = await LayoutCommands.AddDynamicTextAsync(adtLayout, adtText, adtX, adtY, adtWidth, adtHeight, adtElementName);
                        break;

                    case "update_layout_element":
                        string? uleLayout = paramsEl.TryGetProperty("layout_name", out var uleLnProp) ? uleLnProp.GetString() : null;
                        string? uleElement = paramsEl.TryGetProperty("element_name", out var uleEnProp) ? uleEnProp.GetString() : null;
                        bool uleHasText = paramsEl.TryGetProperty("text", out var uleTextProp);
                        string uleText = uleHasText ? uleTextProp.GetString() ?? "" : "";
                        bool? uleVisible = paramsEl.TryGetProperty("visible", out var uleVisProp) ? uleVisProp.GetBoolean() : null;
                        if (string.IsNullOrEmpty(uleLayout)) throw new ArgumentException("Parameter 'layout_name' is required.");
                        if (string.IsNullOrEmpty(uleElement)) throw new ArgumentException("Parameter 'element_name' is required.");
                        resultData = await LayoutCommands.UpdateLayoutElementAsync(uleLayout, uleElement, uleText, uleHasText, uleVisible);
                        break;

                    default:
                        return SerializeError($"Unsupported command: '{command}'");
                }

                stopwatch.Stop();
                return JsonSerializer.Serialize(new
                {
                    success = true,
                    data = resultData,
                    error_code = "",
                    message = "",
                    elapsed_ms = stopwatch.ElapsedMilliseconds
                });
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error executing MCP command: {ex}");
                stopwatch.Stop();
                return SerializeError(ex.Message, ex.GetType().Name, stopwatch.ElapsedMilliseconds);
            }
        }

        private static Dictionary<string, object?> DeserializeAttributes(JsonElement attributes)
        {
            var result = new Dictionary<string, object?>();
            if (attributes.ValueKind != JsonValueKind.Object)
            {
                return result;
            }

            foreach (var property in attributes.EnumerateObject())
            {
                result[property.Name] = property.Value.ValueKind switch
                {
                    JsonValueKind.String => property.Value.GetString(),
                    JsonValueKind.Number when property.Value.TryGetInt64(out var integer) => integer,
                    JsonValueKind.Number when property.Value.TryGetDouble(out var number) => number,
                    JsonValueKind.True => true,
                    JsonValueKind.False => false,
                    JsonValueKind.Null => null,
                    _ => property.Value.ToString()
                };
            }

            return result;
        }

        private static string SerializeError(string message, string errorCode = "INVALID_REQUEST", long elapsedMs = 0)
        {
            return JsonSerializer.Serialize(new
            {
                success = false,
                error_code = errorCode,
                message,
                error = message,
                data = (object?)null,
                elapsed_ms = elapsedMs
            });
        }
    }
}
