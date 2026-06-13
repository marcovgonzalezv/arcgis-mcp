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
            string expressionEngine)
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

                foreach (var labelClass in layer.LabelClasses)
                {
                    labelClass.SetExpressionEngine(engine);
                    labelClass.SetExpression(expression);
                    labelClass.SetLabelVisibility(visible);
                }

                return new
                {
                    success = true,
                    layer_name = layerName,
                    field_name = fieldName,
                    visible,
                    expression = expression,
                    expression_engine = engine.ToString()
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
    }
}
