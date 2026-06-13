using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using ArcGIS.Core.Data;
using ArcGIS.Core.Geometry;
using ArcGIS.Desktop.Framework.Threading.Tasks;
using ArcGIS.Desktop.Mapping;

namespace ArcGisMcpAddin.Commands
{
    public static class DataCommands
    {
        public static Task<object> CountFeaturesAsync(string layerName, string sqlFilter)
        {
            return QueuedTask.Run<object>(() =>
            {
                var layer = GetFeatureLayer(layerName);
                using var featureClass = layer.GetFeatureClass();
                if (featureClass == null)
                {
                    throw new InvalidOperationException($"Layer '{layerName}' does not reference a valid feature class.");
                }

                long count;
                if (string.IsNullOrEmpty(sqlFilter))
                {
                    count = featureClass.GetCount();
                }
                else
                {
                    var filter = new QueryFilter { WhereClause = sqlFilter };
                    count = featureClass.GetCount(filter);
                }

                return new { layer_name = layerName, count };
            });
        }

        public static Task<object> SelectFeaturesAsync(string layerName, string sqlFilter, string combination)
        {
            return QueuedTask.Run<object>(() =>
            {
                var layer = GetFeatureLayer(layerName);

                var comboType = SelectionCombinationMethod.New;
                switch (combination.ToUpperInvariant())
                {
                    case "ADD": comboType = SelectionCombinationMethod.Add; break;
                    case "REMOVE": comboType = SelectionCombinationMethod.Subtract; break;
                    case "SUBTRACT": comboType = SelectionCombinationMethod.Subtract; break;
                    case "AND": comboType = SelectionCombinationMethod.And; break;
                    case "XOR": comboType = SelectionCombinationMethod.XOR; break;
                    case "NEW":
                    default:
                        comboType = SelectionCombinationMethod.New;
                        break;
                }

                var filter = new QueryFilter { WhereClause = sqlFilter };
                using var selection = layer.Select(filter, comboType);

                long selectedCount = selection.GetCount();
                return new { layer_name = layerName, count = selectedCount, combination };
            });
        }

        public static Task<object> GetSelectedFeaturesAsync(string layerName, int maxFeatures)
        {
            return QueuedTask.Run<object>(() =>
            {
                var layer = GetFeatureLayer(layerName);
                using var selection = layer.GetSelection();
                if (selection == null || selection.GetCount() == 0)
                {
                    return new { layer_name = layerName, features = new List<object>() };
                }

                var featuresList = new List<Dictionary<string, object>>();

                using (var cursor = selection.Search(null, false))
                {
                    int count = 0;
                    while (cursor.MoveNext() && count < maxFeatures)
                    {
                        using var row = cursor.Current;
                        var attrDict = new Dictionary<string, object>();
                        var fields = row.GetFields();

                        foreach (var field in fields)
                        {
                            object val = row[field.Name];
                            // Format standard DBNull or complex values
                            if (val == DBNull.Value || val == null)
                            {
                                attrDict[field.Name] = null!;
                            }
                            else if (field.FieldType == FieldType.Geometry)
                            {
                                attrDict[field.Name] = "Geometry Object";
                            }
                            else
                            {
                                attrDict[field.Name] = val;
                            }
                        }
                        featuresList.Add(attrDict);
                        count++;
                    }
                }

                return new { layer_name = layerName, total_selected = selection.GetCount(), features = featuresList };
            });
        }

        public static Task<object> GetLayerFieldsAsync(string layerName)
        {
            return QueuedTask.Run<object>(() =>
            {
                var layer = GetFeatureLayer(layerName);
                using var featureClass = layer.GetFeatureClass();
                if (featureClass == null)
                {
                    throw new InvalidOperationException($"Layer '{layerName}' does not reference a valid feature class.");
                }

                using var definition = featureClass.GetDefinition();
                var fields = definition.GetFields();

                var fieldList = fields.Select(f => new
                {
                    name = f.Name,
                    alias = f.AliasName,
                    type = f.FieldType.ToString()
                }).ToList();

                return new { layer_name = layerName, fields = fieldList };
            });
        }

        public static Task<object> QueryLayerAsync(
            string layerName,
            string whereClause,
            string fields,
            int limit,
            bool includeGeometry)
        {
            return QueuedTask.Run<object>(() =>
            {
                var layer = GetFeatureLayer(layerName);
                using var featureClass = layer.GetFeatureClass();
                if (featureClass == null)
                {
                    throw new InvalidOperationException($"Layer '{layerName}' does not reference a valid feature class.");
                }

                using var definition = featureClass.GetDefinition();
                var availableFields = definition.GetFields();
                var selectedFields = ResolveFields(fields, availableFields);
                int rowLimit = Math.Clamp(limit, 1, 5000);
                var rows = new List<Dictionary<string, object?>>();
                var filter = new QueryFilter { WhereClause = whereClause };

                using var cursor = layer.Search(filter);
                int count = 0;
                while (cursor.MoveNext() && count < rowLimit)
                {
                    using var row = cursor.Current;
                    var values = new Dictionary<string, object?>();

                    foreach (string fieldName in selectedFields)
                    {
                        object value = row[fieldName];
                        values[fieldName] = value == DBNull.Value ? null : value;
                    }

                    if (includeGeometry)
                    {
                        var geometryField = row.GetFields()
                            .FirstOrDefault(field => field.FieldType == FieldType.Geometry);
                        if (geometryField != null && row[geometryField.Name] is Geometry geometry)
                        {
                            var extent = geometry.Extent;
                            values["geometry_extent"] = new
                            {
                                xmin = extent.XMin,
                                ymin = extent.YMin,
                                xmax = extent.XMax,
                                ymax = extent.YMax,
                                wkid = extent.SpatialReference?.Wkid
                            };
                        }
                    }

                    rows.Add(values);
                    count++;
                }

                bool limited = rows.Count == rowLimit;
                return new
                {
                    layer_name = layerName,
                    where_clause = whereClause,
                    fields = selectedFields,
                    limit = rowLimit,
                    include_geometry = includeGeometry,
                    returned = rows.Count,
                    limited,
                    rows
                };
            });
        }

        // Helper to retrieve a feature layer by name (case-insensitive)
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

        private static List<string> ResolveFields(string fields, IReadOnlyList<Field> availableFields)
        {
            var attributeFields = availableFields
                .Where(field => field.FieldType != FieldType.Geometry)
                .Select(field => field.Name)
                .ToList();

            if (string.IsNullOrWhiteSpace(fields) || fields.Trim() == "*")
            {
                return attributeFields;
            }

            var selected = fields
                .Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries)
                .ToList();
            var missing = selected
                .Where(fieldName => !attributeFields.Any(
                    available => available.Equals(fieldName, StringComparison.OrdinalIgnoreCase)))
                .ToList();

            if (missing.Count > 0)
            {
                throw new ArgumentException($"Field(s) not found: {string.Join(", ", missing)}.");
            }

            return selected;
        }
    }
}
