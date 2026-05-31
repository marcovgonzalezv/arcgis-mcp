using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using ArcGIS.Core.CIM;
using ArcGIS.Core.Geometry;
using ArcGIS.Desktop.Core;
using ArcGIS.Desktop.Framework.Threading.Tasks;
using ArcGIS.Desktop.Layouts;
using ArcGIS.Desktop.Mapping;

namespace ArcGisMcpAddin.Commands
{
    public static class LayoutCommands
    {
        public static Task<object> ListLayoutsAsync()
        {
            return QueuedTask.Run<object>(() =>
            {
                if (Project.Current == null)
                {
                    throw new InvalidOperationException("No active project found in ArcGIS Pro.");
                }

                // Get layout items from the project
                var layoutItems = Project.Current.GetItems<LayoutProjectItem>();
                var layoutNames = layoutItems.Select(l => l.Name).ToList();

                return new { layouts = layoutNames };
            });
        }

        public static Task<object> ExportLayoutAsync(string layoutName, string outputPath, string formatType, int dpi)
        {
            return QueuedTask.Run<object>(() =>
            {
                if (Project.Current == null)
                {
                    throw new InvalidOperationException("No active project found.");
                }

                var layoutItem = Project.Current.GetItems<LayoutProjectItem>()
                    .FirstOrDefault(l => l.Name.Equals(layoutName, StringComparison.OrdinalIgnoreCase));

                if (layoutItem == null)
                {
                    throw new ArgumentException($"Layout '{layoutName}' not found in the current project.");
                }

                // Ensure the output directory exists
                string? dir = Path.GetDirectoryName(outputPath);
                if (!string.IsNullOrEmpty(dir) && !Directory.Exists(dir))
                {
                    Directory.CreateDirectory(dir);
                }

                var layout = layoutItem.GetLayout();
                if (layout == null)
                {
                    throw new InvalidOperationException($"Could not open layout '{layoutName}'.");
                }

                // Create the appropriate export format
                ExportFormat exportFormat;
                switch (formatType.ToUpperInvariant())
                {
                    case "PNG":
                        exportFormat = new PNGFormat
                        {
                            OutputFileName = outputPath,
                            Resolution = dpi
                        };
                        break;
                    case "JPEG":
                    case "JPG":
                        exportFormat = new JPEGFormat
                        {
                            OutputFileName = outputPath,
                            Resolution = dpi
                        };
                        break;
                    case "PDF":
                    default:
                        exportFormat = new PDFFormat
                        {
                            OutputFileName = outputPath,
                            Resolution = dpi
                        };
                        break;
                }

                // Execute the export (runs on MCT thread)
                layout.Export(exportFormat);

                return new
                {
                    layout_name = layoutName,
                    output_path = outputPath,
                    format = formatType,
                    resolution = dpi,
                    success = true
                };
            });
        }

        public static Task<object> CreateBasicLayoutAsync(
            string layoutName,
            string title,
            double pageWidth,
            double pageHeight)
        {
            return QueuedTask.Run<object>(() =>
            {
                var activeView = MapView.Active;
                if (activeView == null || activeView.Map == null)
                {
                    throw new InvalidOperationException("No active map view found.");
                }

                var layout = LayoutFactory.Instance.CreateLayout(pageWidth, pageHeight, LinearUnit.Inches, false, 0);
                layout.SetName(layoutName);

                var mapFrameEnvelope = EnvelopeBuilderEx.CreateEnvelope(
                    0.5,
                    0.7,
                    Math.Max(1.0, pageWidth - 0.5),
                    Math.Max(1.0, pageHeight - 0.9)
                );
                var mapFrame = ElementFactory.Instance.CreateMapFrameElement(
                    layout,
                    mapFrameEnvelope,
                    activeView.Map,
                    "MCP Map Frame",
                    true,
                    null
                );
                mapFrame.SetCamera(activeView.Camera);

                var textSymbol = SymbolFactory.Instance.ConstructTextSymbol(
                    CIMColor.CreateRGBColor(40, 40, 40, 100),
                    18,
                    "Arial",
                    "Bold"
                );
                var titlePoint = MapPointBuilderEx.CreateMapPoint(pageWidth / 2.0, pageHeight - 0.35);
                ElementFactory.Instance.CreateTextGraphicElement(
                    layout,
                    TextType.PointText,
                    titlePoint,
                    textSymbol,
                    title,
                    "Title",
                    true,
                    null
                );

                TryCreateSurround(layout, mapFrame.Name, MapSurroundType.Legend, "Legend", pageWidth - 2.7, 0.8, pageWidth - 0.4, 3.0);
                TryCreateSurround(layout, mapFrame.Name, MapSurroundType.NorthArrow, "North Arrow", pageWidth - 1.0, pageHeight - 1.4, pageWidth - 0.4, pageHeight - 0.8);
                TryCreateSurround(layout, mapFrame.Name, MapSurroundType.ScaleBar, "Scale Bar", 0.7, 0.25, 3.0, 0.55);

                return new
                {
                    success = true,
                    layout_name = layoutName,
                    map_name = activeView.Map.Name,
                    page_width = pageWidth,
                    page_height = pageHeight
                };
            });
        }

        public static Task<object> ExportActiveMapAsync(
            string outputPath,
            string formatType,
            int width,
            int height,
            int dpi)
        {
            return QueuedTask.Run<object>(() =>
            {
                var activeView = MapView.Active;
                if (activeView == null)
                {
                    throw new InvalidOperationException("No active map view found.");
                }

                string? dir = Path.GetDirectoryName(outputPath);
                if (!string.IsNullOrEmpty(dir) && !Directory.Exists(dir))
                {
                    Directory.CreateDirectory(dir);
                }

                var exportFormat = CreateExportFormat(outputPath, formatType, dpi, width, height);
                activeView.Export(exportFormat);

                return new
                {
                    success = true,
                    output_path = outputPath,
                    format = formatType,
                    width,
                    height,
                    resolution = dpi
                };
            });
        }

        public static Task<object> AddDynamicTextAsync(
            string layoutName,
            string text,
            double x,
            double y,
            double width,
            double height,
            string elementName)
        {
            return QueuedTask.Run<object>(() =>
            {
                var layout = GetLayout(layoutName);
                var symbol = SymbolFactory.Instance.ConstructTextSymbol(
                    CIMColor.CreateRGBColor(40, 40, 40, 100),
                    10,
                    "Arial",
                    "Regular"
                );
                var envelope = EnvelopeBuilderEx.CreateEnvelope(x, y, x + width, y + height);
                var element = ElementFactory.Instance.CreateTextGraphicElement(
                    layout,
                    TextType.RectangleParagraph,
                    envelope,
                    symbol,
                    text,
                    elementName,
                    true,
                    null
                );
                return new { success = true, layout_name = layoutName, element_name = element.Name };
            });
        }

        public static Task<object> UpdateLayoutElementAsync(
            string layoutName,
            string elementName,
            string text,
            bool hasText,
            bool? visible)
        {
            return QueuedTask.Run<object>(() =>
            {
                var layout = GetLayout(layoutName);
                var element = layout.FindElement(elementName);
                if (element == null)
                {
                    throw new ArgumentException($"Element '{elementName}' not found in layout '{layoutName}'.");
                }

                if (visible.HasValue)
                {
                    element.SetVisible(visible.Value);
                }

                if (hasText && element is TextElement textElement)
                {
                    var properties = textElement.TextProperties;
                    properties.Text = text;
                    textElement.SetTextProperties(properties);
                }

                return new { success = true, layout_name = layoutName, element_name = elementName };
            });
        }

        public static Task<object> CreateMapSeriesAsync(
            string layoutName,
            string mapFrameName,
            string indexLayerName,
            string nameField)
        {
            return QueuedTask.Run<object>(() =>
            {
                var layout = GetLayout(layoutName);
                var mapFrame = layout.FindElement(mapFrameName) as MapFrame;
                if (mapFrame == null)
                {
                    throw new ArgumentException($"Map frame '{mapFrameName}' not found in layout '{layoutName}'.");
                }

                var indexLayer = mapFrame.Map.FindLayers(indexLayerName)
                    .OfType<BasicFeatureLayer>()
                    .FirstOrDefault();
                if (indexLayer == null)
                {
                    throw new ArgumentException($"Index feature layer '{indexLayerName}' not found in map frame '{mapFrameName}'.");
                }

                if (!LayerHasField(indexLayer, nameField))
                {
                    throw new ArgumentException($"Field '{nameField}' not found in index layer '{indexLayerName}'.");
                }

                long indexFeatureCount = GetFeatureCount(indexLayer);
                if (indexFeatureCount == 0)
                {
                    throw new InvalidOperationException($"Index layer '{indexLayerName}' has no features. A spatial map series requires at least one index feature.");
                }

                var mapSeries = MapSeries.CreateSpatialMapSeries(layout, mapFrame, indexLayer, nameField);
                mapSeries.SortField = nameField;
                mapSeries.SortAscending = true;
                mapSeries.ExtentOptions = ExtentFitType.BestFit;
                mapSeries.MarginType = ArcGIS.Core.CIM.UnitType.PageUnits;
                mapSeries.MarginUnits = LinearUnit.Centimeters;
                mapSeries.Margin = 1;
                mapSeries.ScaleRounding = 1000;
                layout.SetMapSeries(mapSeries);

                return new
                {
                    success = true,
                    layout_name = layoutName,
                    map_frame_name = mapFrame.Name,
                    index_layer_name = indexLayer.Name,
                    name_field = nameField,
                    index_feature_count = indexFeatureCount,
                    page_count = mapSeries.PageCount
                };
            });
        }

        public static Task<object> ExportMapSeriesAsync(
            string layoutName,
            string outputPath,
            string formatType,
            int dpi)
        {
            return QueuedTask.Run<object>(() =>
            {
                var layout = GetLayout(layoutName);
                if (layout.MapSeries == null)
                {
                    throw new InvalidOperationException($"Layout '{layoutName}' does not have a configured map series.");
                }

                if (layout.MapSeries.PageCount <= 0)
                {
                    throw new InvalidOperationException($"Layout '{layoutName}' has a map series with no pages.");
                }

                string? dir = Path.GetDirectoryName(outputPath);
                if (!string.IsNullOrEmpty(dir) && !Directory.Exists(dir))
                {
                    Directory.CreateDirectory(dir);
                }

                var exportFormat = CreateExportFormat(outputPath, formatType, dpi);
                var exportOptions = new MapSeriesExportOptions
                {
                    ExportPages = ExportPages.All,
                    ExportFileOptions = exportFormat is PDFFormat
                        ? ExportFileOptions.ExportAsSinglePDF
                        : ExportFileOptions.ExportMultipleNames
                };

                layout.Export(exportFormat, exportOptions);
                return new
                {
                    success = true,
                    layout_name = layoutName,
                    output_path = outputPath,
                    format = formatType,
                    resolution = dpi,
                    page_count = layout.MapSeries.PageCount,
                    export_file_options = exportOptions.ExportFileOptions.ToString()
                };
            });
        }

        private static void TryCreateSurround(
            Layout layout,
            string mapFrameName,
            MapSurroundType type,
            string name,
            double xmin,
            double ymin,
            double xmax,
            double ymax)
        {
            try
            {
                var info = CreateMapSurroundInfo(type);
                info.MapFrameName = mapFrameName;
                ElementFactory.Instance.CreateMapSurroundElement(
                    layout,
                    EnvelopeBuilderEx.CreateEnvelope(xmin, ymin, xmax, ymax),
                    info,
                    name,
                    true,
                    null
                );
            }
            catch (InvalidOperationException ex)
            {
                System.Diagnostics.Debug.WriteLine($"Map surround '{name}' was not created: {ex.Message}");
            }
            catch (ArgumentException ex)
            {
                System.Diagnostics.Debug.WriteLine($"Map surround '{name}' has invalid parameters: {ex.Message}");
            }
        }

        private static Layout GetLayout(string layoutName)
        {
            if (Project.Current == null)
            {
                throw new InvalidOperationException("No active project found.");
            }

            var layoutItem = Project.Current.GetItems<LayoutProjectItem>()
                .FirstOrDefault(item => item.Name.Equals(layoutName, StringComparison.OrdinalIgnoreCase));
            if (layoutItem == null)
            {
                throw new ArgumentException($"Layout '{layoutName}' not found in the current project.");
            }

            return layoutItem.GetLayout();
        }

        private static bool LayerHasField(BasicFeatureLayer layer, string fieldName)
        {
            using var table = layer.GetTable();
            if (table == null)
            {
                return false;
            }

            using var definition = table.GetDefinition();
            return definition.GetFields()
                .Any(field => field.Name.Equals(fieldName, StringComparison.OrdinalIgnoreCase));
        }

        private static long GetFeatureCount(BasicFeatureLayer layer)
        {
            using var table = layer.GetTable();
            return table?.GetCount() ?? 0;
        }

        private static MapSurroundInfo CreateMapSurroundInfo(MapSurroundType type)
        {
            return type switch
            {
                MapSurroundType.Legend => new LegendInfo(),
                MapSurroundType.NorthArrow => new NorthArrowInfo(),
                MapSurroundType.ScaleBar => new ScaleBarInfo(),
                _ => throw new ArgumentException($"Unsupported map surround type: {type}")
            };
        }

        private static ExportFormat CreateExportFormat(
            string outputPath,
            string formatType,
            int dpi,
            int width,
            int height)
        {
            ExportFormat exportFormat = formatType.ToUpperInvariant() switch
            {
                "JPEG" or "JPG" => new JPEGFormat(),
                "PDF" => new PDFFormat(),
                _ => new PNGFormat()
            };

            exportFormat.OutputFileName = outputPath;
            exportFormat.Resolution = dpi;
            exportFormat.Width = width;
            exportFormat.Height = height;
            return exportFormat;
        }

        private static ExportFormat CreateExportFormat(string outputPath, string formatType, int dpi)
        {
            ExportFormat exportFormat = formatType.ToUpperInvariant() switch
            {
                "JPEG" or "JPG" => new JPEGFormat(),
                "PNG" => new PNGFormat(),
                "TIFF" or "TIF" => new TIFFFormat(),
                _ => new PDFFormat()
            };

            exportFormat.OutputFileName = outputPath;
            exportFormat.Resolution = dpi;
            return exportFormat;
        }
    }
}
