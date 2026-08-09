using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using ArcGIS.Core.CIM;
using ArcGIS.Core.Data;
using ArcGIS.Core.Geometry;
using ArcGIS.Desktop.Core.Geoprocessing;
using ArcGIS.Desktop.Framework.Threading.Tasks;
using ArcGIS.Desktop.Mapping;

namespace ArcGisMcpAddin.Commands
{
    public static class SymbologyCommands
    {
        public static Task<object> ApplyGraduatedSymbologyAsync(
            string layerName,
            string fieldName,
            int breakCount,
            string classificationMethod,
            string colorRamp)
        {
            return QueuedTask.Run<object>(() =>
            {
                var layer = GetFeatureLayer(layerName);
                if (!LayerHasField(layer, fieldName))
                {
                    throw new ArgumentException($"Field '{fieldName}' not found in layer '{layerName}'.");
                }

                var method = ParseClassificationMethod(classificationMethod);
                var ramp = GetColorRamp(colorRamp);
                var symbol = CreateSymbolTemplate(layer);

                var definition = new GraduatedColorsRendererDefinition(
                    fieldName,
                    method,
                    Math.Clamp(breakCount, 2, 32),
                    ramp,
                    symbol
                );

                if (!layer.CanCreateRenderer(definition))
                {
                    throw new InvalidOperationException($"Layer '{layerName}' cannot create a graduated renderer for field '{fieldName}'.");
                }

                var renderer = layer.CreateRenderer(definition);
                layer.SetRenderer(renderer);

                return new
                {
                    success = true,
                    layer_name = layerName,
                    field_name = fieldName,
                    break_count = breakCount,
                    classification_method = method.ToString(),
                    renderer_type = layer.GetRenderer()?.GetType().Name ?? ""
                };
            });
        }

        public static Task<object> ApplyUniqueValueSymbologyAsync(
            string layerName,
            string fieldName,
            string colorRamp,
            int valuesLimit)
        {
            return QueuedTask.Run<object>(() =>
            {
                var layer = GetFeatureLayer(layerName);
                if (!LayerHasField(layer, fieldName))
                {
                    throw new ArgumentException($"Field '{fieldName}' not found in layer '{layerName}'.");
                }

                var definition = new UniqueValueRendererDefinition
                {
                    ValueFields = new List<string> { fieldName },
                    ColorRamp = GetColorRamp(colorRamp),
                    SymbolTemplate = CreateSymbolTemplate(layer),
                    ValuesLimit = Math.Clamp(valuesLimit, 1, 10000),
                    UseDefaultSymbol = true,
                    DefaultSymbol = CreateSymbolTemplate(layer)
                };

                if (!layer.CanCreateRenderer(definition))
                {
                    throw new InvalidOperationException($"Layer '{layerName}' cannot create a unique value renderer for field '{fieldName}'.");
                }

                var renderer = layer.CreateRenderer(definition);
                layer.SetRenderer(renderer);

                return new
                {
                    success = true,
                    layer_name = layerName,
                    field_name = fieldName,
                    renderer_type = layer.GetRenderer()?.GetType().Name ?? ""
                };
            });
        }

        public static async Task<object> ApplySymbologyFromLayerAsync(string targetLayer, string symbologyLayer)
        {
            var valueArray = Geoprocessing.MakeValueArray(targetLayer, symbologyLayer);
            IGPResult result = await Geoprocessing.ExecuteToolAsync(
                "ApplySymbologyFromLayer_management",
                valueArray,
                null,
                null,
                null,
                GPExecuteToolFlags.None
            );

            if (result.IsFailed)
            {
                throw new InvalidOperationException(BuildGpError(result));
            }

            return new { success = true, target_layer = targetLayer, symbology_layer = symbologyLayer };
        }

        public static Task<object> LabelLayerAsync(
            string layerName,
            string fieldName,
            bool visible,
            string expressionEngine,
            double haloSize = 0,
            string haloColor = "#FFFFFF")
        {
            return QueuedTask.Run<object>(() =>
            {
                var layer = GetFeatureLayer(layerName);
                if (!LayerHasField(layer, fieldName))
                {
                    throw new ArgumentException($"Field '{fieldName}' not found in layer '{layerName}'.");
                }

                var engine = ParseLabelExpressionEngine(expressionEngine);
                var expression = BuildLabelExpression(fieldName, engine);
                layer.SetLabelVisibility(visible);

                bool haloApplied = false;

                foreach (var labelClass in layer.LabelClasses)
                {
                    labelClass.SetExpressionEngine(engine);
                    labelClass.SetExpression(expression);
                    labelClass.SetLabelVisibility(visible);
                }

                if (haloSize > 0)
                {
                    var cim = layer.GetDefinition() as CIMFeatureLayer;
                    if (cim?.LabelClasses != null)
                    {
                        var haloCimColor = ParseHexColor(haloColor);
                        foreach (var lc in cim.LabelClasses)
                        {
                            if (lc.TextSymbol?.Symbol is CIMTextSymbol textSymbol)
                            {
                                textSymbol.HaloSize = haloSize;
                                textSymbol.HaloSymbol = SymbolFactory.Instance.ConstructPolygonSymbol(haloCimColor);
                                haloApplied = true;
                            }
                        }
                        layer.SetDefinition(cim);
                    }
                }

                return new
                {
                    success = true,
                    layer_name = layerName,
                    field_name = fieldName,
                    visible,
                    expression = expression,
                    expression_engine = engine.ToString(),
                    halo_size = haloApplied ? haloSize : 0,
                    halo_color = haloApplied ? haloColor : ""
                };
            });
        }

        public static Task<object> GetLayerSymbologyAsync(string layerName)
        {
            return QueuedTask.Run<object>(() =>
            {
                var activeView = MapView.Active;
                if (activeView == null)
                {
                    throw new InvalidOperationException("No active map view found.");
                }

                var layer = activeView.Map.GetLayersAsFlattenedList()
                    .FirstOrDefault(candidate => candidate.Name.Equals(layerName, StringComparison.OrdinalIgnoreCase));
                if (layer == null)
                {
                    throw new ArgumentException($"Layer '{layerName}' not found.");
                }

                if (layer is not FeatureLayer featureLayer)
                {
                    return new { layer_name = layerName, renderer_type = layer.GetType().Name, renderer_json = "" };
                }

                var renderer = featureLayer.GetRenderer();
                return new
                {
                    layer_name = layerName,
                    renderer_type = renderer?.GetType().Name ?? "",
                    renderer_json = renderer?.ToJson() ?? ""
                };
            });
        }

        public static async Task<object> ApplyRasterColorizerAsync(
            string rasterLayer,
            string symbologyLayer,
            string colorRamp)
        {
            if (string.IsNullOrWhiteSpace(symbologyLayer))
            {
                throw new ArgumentException("Parameter 'symbology_layer' is required. Raster colorizers are applied from an existing raster layer or .lyrx file.");
            }

            var valueArray = Geoprocessing.MakeValueArray(rasterLayer, symbologyLayer);
            IGPResult result = await Geoprocessing.ExecuteToolAsync(
                "ApplySymbologyFromLayer_management",
                valueArray,
                null,
                null,
                null,
                GPExecuteToolFlags.None
            );

            if (result.IsFailed)
            {
                throw new InvalidOperationException(BuildGpError(result));
            }

            return new { success = true, raster_layer = rasterLayer, symbology_layer = symbologyLayer, color_ramp = colorRamp };
        }

        private static FeatureLayer GetFeatureLayer(string layerName)
        {
            var activeView = MapView.Active;
            if (activeView == null)
            {
                throw new InvalidOperationException("No active map view found.");
            }

            var layer = activeView.Map.GetLayersAsFlattenedList()
                .OfType<FeatureLayer>()
                .FirstOrDefault(l => l.Name.Equals(layerName, StringComparison.OrdinalIgnoreCase));

            if (layer == null)
            {
                throw new ArgumentException($"Feature layer '{layerName}' not found in the active map.");
            }

            return layer;
        }

        private static CIMColorRamp GetColorRamp(string colorRamp)
        {
            if (!string.IsNullOrWhiteSpace(colorRamp) && !colorRamp.Equals("Default", StringComparison.OrdinalIgnoreCase))
            {
                var namedRamp = ColorFactory.Instance.GetColorRamp(colorRamp);
                if (namedRamp != null)
                {
                    return namedRamp;
                }
            }

            return ColorFactory.Instance.ConstructColorRamp(
                ColorRampAlgorithm.LinearContinuous,
                CIMColor.CreateRGBColor(255, 255, 178, 100),
                CIMColor.CreateRGBColor(189, 0, 38, 100)
            );
        }

        private static bool LayerHasField(FeatureLayer layer, string fieldName)
        {
            using var featureClass = layer.GetFeatureClass();
            using var definition = featureClass.GetDefinition();
            return definition.GetFields()
                .Any(field => field.Name.Equals(fieldName, StringComparison.OrdinalIgnoreCase));
        }

        private static LabelExpressionEngine ParseLabelExpressionEngine(string value)
        {
            if (Enum.TryParse(value, true, out LabelExpressionEngine engine))
            {
                return engine;
            }

            return LabelExpressionEngine.Arcade;
        }

        private static string BuildLabelExpression(string fieldName, LabelExpressionEngine engine)
        {
            return engine switch
            {
                LabelExpressionEngine.Python => $"[{fieldName}]",
                LabelExpressionEngine.VBScript => $"[{fieldName}]",
                LabelExpressionEngine.JScript => $"[{fieldName}]",
                _ => $"$feature.{fieldName}"
            };
        }

        private static CIMSymbolReference CreateSymbolTemplate(FeatureLayer layer)
        {
            using var featureClass = layer.GetFeatureClass();
            using var definition = featureClass.GetDefinition();
            var geometryType = definition.GetShapeType();
            var fill = CIMColor.CreateRGBColor(252, 141, 89, 70);
            var outline = SymbolFactory.Instance.ConstructStroke(CIMColor.CreateRGBColor(90, 90, 90, 100), 0.5);

            return geometryType switch
            {
                GeometryType.Point or GeometryType.Multipoint =>
                    SymbolFactory.Instance.ConstructPointSymbol(fill, 6.0).MakeSymbolReference(),
                GeometryType.Polyline =>
                    SymbolFactory.Instance.ConstructLineSymbol(fill, 1.5).MakeSymbolReference(),
                _ =>
                    SymbolFactory.Instance.ConstructPolygonSymbol(fill, SimpleFillStyle.Solid, outline).MakeSymbolReference()
            };
        }

        private static ClassificationMethod ParseClassificationMethod(string value)
        {
            if (Enum.TryParse(value, true, out ClassificationMethod method))
            {
                return method;
            }

            return ClassificationMethod.NaturalBreaks;
        }

        private static string BuildGpError(IGPResult result)
        {
            var messages = result.Messages?.Select(m => $"[{m.Type}] {m.Text}") ?? Enumerable.Empty<string>();
            return string.Join("\n", messages);
        }

        private static CIMColor ParseHexColor(string hex)
        {
            int r = 255, g = 255, b = 255;
            if (!string.IsNullOrEmpty(hex) && hex.StartsWith("#") && hex.Length >= 7)
            {
                r = Convert.ToInt32(hex.Substring(1, 2), 16);
                g = Convert.ToInt32(hex.Substring(3, 2), 16);
                b = Convert.ToInt32(hex.Substring(5, 2), 16);
            }
            return ColorFactory.Instance.CreateRGBColor(r, g, b);
        }

        public static Task<object> SetLayerSymbolAsync(
            string layerName, int r, int g, int b,
            double width = 0, double alpha = 100)
        {
            return QueuedTask.Run<object>(() =>
            {
                var layer = GetFeatureLayer(layerName);
                var def = layer.GetDefinition() as CIMFeatureLayer;

                if (def?.Renderer is not CIMSimpleRenderer simpleRenderer)
                {
                    throw new InvalidOperationException(
                        $"Layer '{layerName}' does not use a simple renderer. " +
                        "Convert to single-symbol symbology first.");
                }

                var color = ColorFactory.Instance.CreateRGBColor(
                    Math.Clamp(r, 0, 255),
                    Math.Clamp(g, 0, 255),
                    Math.Clamp(b, 0, 255),
                    Math.Clamp(alpha, 0, 100));

                var geometryType = layer.ShapeType;
                string symbolType;

                if (simpleRenderer.Symbol?.Symbol is CIMLineSymbol lineSymbol)
                {
                    symbolType = "line";
                    foreach (var symLayer in lineSymbol.SymbolLayers)
                    {
                        if (symLayer is CIMSolidStroke stroke)
                        {
                            stroke.Color = color;
                            if (width > 0) stroke.Width = width;
                        }
                    }
                }
                else if (simpleRenderer.Symbol?.Symbol is CIMPolygonSymbol polySymbol)
                {
                    symbolType = "polygon";
                    foreach (var symLayer in polySymbol.SymbolLayers)
                    {
                        if (symLayer is CIMSolidFill fill)
                        {
                            fill.Color = color;
                        }
                        if (symLayer is CIMSolidStroke stroke && width > 0)
                        {
                            stroke.Width = width;
                        }
                    }
                }
                else if (simpleRenderer.Symbol?.Symbol is CIMPointSymbol pointSymbol)
                {
                    symbolType = "point";
                    foreach (var symLayer in pointSymbol.SymbolLayers)
                    {
                        if (symLayer is CIMVectorMarker marker && marker.MarkerGraphics != null)
                        {
                            foreach (var graphic in marker.MarkerGraphics)
                            {
                                if (graphic?.Symbol is CIMPolygonSymbol markerPoly)
                                {
                                    foreach (var ml in markerPoly.SymbolLayers)
                                    {
                                        if (ml is CIMSolidFill fill) fill.Color = color;
                                    }
                                }
                            }
                        }
                    }
                }
                else
                {
                    symbolType = geometryType.ToString();
                }

                layer.SetDefinition(def);

                return new
                {
                    success = true,
                    layer_name = layerName,
                    symbol_type = symbolType,
                    color = $"#{r:X2}{g:X2}{b:X2}",
                    width = width > 0 ? width : (double?)null
                };
            });
        }
    }
}
