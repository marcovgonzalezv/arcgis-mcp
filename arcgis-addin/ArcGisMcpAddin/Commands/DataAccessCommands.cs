using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using ArcGIS.Core.Geometry;
using ArcGIS.Desktop.Editing;
using ArcGIS.Desktop.Framework.Threading.Tasks;
using ArcGIS.Desktop.Mapping;

namespace ArcGisMcpAddin.Commands
{
    /// <summary>
    /// Bulk data-access operations equivalent to arcpy.da cursors.
    ///
    /// Instead of exposing raw cursors across the IPC boundary, these commands
    /// accept batches of records (already JSON-serialised) and perform a
    /// single grouped <see cref="EditOperation"/>. This keeps the wire format
    /// simple while delivering the throughput of arcpy.da cursors.
    /// </summary>
    public static class DataAccessCommands
    {
        /// <summary>
        /// Inserts multiple point features in a single edit operation.
        /// Each item in ``features`` is { x, y, attributes?, wkid? }.
        /// </summary>
        public static async Task<object> InsertFeaturesAsync(
            string layerName,
            List<Dictionary<string, object?>> features)
        {
            if (features == null || features.Count == 0)
            {
                throw new ArgumentException("No features provided for insertion.");
            }

            var op = await QueuedTask.Run(() =>
            {
                var layer = GetFeatureLayer(layerName);
                var editOperation = new EditOperation
                {
                    Name = $"MCP insert {features.Count} features into {layerName}"
                };

                foreach (var feature in features)
                {
                    double x = Convert.ToDouble(feature["x"]);
                    double y = Convert.ToDouble(feature["y"]);
                    int wkid = feature.TryGetValue("wkid", out var w) && w != null ? Convert.ToInt32(w) : 4326;
                    var sr = SpatialReferenceBuilder.CreateSpatialReference(wkid);
                    var point = MapPointBuilderEx.CreateMapPoint(x, y, sr);

                    var attributes = new Dictionary<string, object?>();
                    if (feature.TryGetValue("attributes", out var attrObj) && attrObj is Dictionary<string, object?> attr)
                    {
                        attributes = attr;
                    }
                    editOperation.Create(layer, point, attributes);
                }

                return editOperation;
            });

            if (!await op.ExecuteAsync())
            {
                throw new InvalidOperationException(op.ErrorMessage);
            }

            return new { success = true, layer_name = layerName, inserted_count = features.Count };
        }

        /// <summary>
        /// Updates multiple features by ObjectID in a single edit operation.
        /// Each item in ``updates`` is { objectid, attributes }.
        /// </summary>
        public static async Task<object> UpdateFeaturesAsync(
            string layerName,
            List<Dictionary<string, object?>> updates)
        {
            if (updates == null || updates.Count == 0)
            {
                throw new ArgumentException("No updates provided.");
            }

            var op = await QueuedTask.Run(() =>
            {
                var layer = GetFeatureLayer(layerName);
                var editOperation = new EditOperation
                {
                    Name = $"MCP update {updates.Count} features in {layerName}"
                };

                foreach (var update in updates)
                {
                    long oid = Convert.ToInt64(update["objectid"]);
                    var attributes = new Dictionary<string, object?>();
                    if (update.TryGetValue("attributes", out var attrObj) && attrObj is Dictionary<string, object?> attr)
                    {
                        attributes = attr;
                    }
                    editOperation.Modify(layer, oid, attributes);
                }

                return editOperation;
            });

            if (!await op.ExecuteAsync())
            {
                throw new InvalidOperationException(op.ErrorMessage);
            }

            return new { success = true, layer_name = layerName, updated_count = updates.Count };
        }

        /// <summary>
        /// Deletes the features identified by the given ObjectIDs.
        /// </summary>
        public static async Task<object> DeleteFeaturesAsync(
            string layerName,
            List<long> objectIds)
        {
            if (objectIds == null || objectIds.Count == 0)
            {
                throw new ArgumentException("No ObjectIDs provided for deletion.");
            }

            var op = await QueuedTask.Run(() =>
            {
                var layer = GetFeatureLayer(layerName);
                var editOperation = new EditOperation
                {
                    Name = $"MCP delete {objectIds.Count} features from {layerName}"
                };
                editOperation.Delete(layer, objectIds);
                return editOperation;
            });

            if (!await op.ExecuteAsync())
            {
                throw new InvalidOperationException(op.ErrorMessage);
            }

            return new { success = true, layer_name = layerName, deleted_count = objectIds.Count };
        }

        private static FeatureLayer GetFeatureLayer(string layerName)
        {
            var layer = MapView.Active?.Map?.GetLayersAsFlattenedList()
                .OfType<FeatureLayer>()
                .FirstOrDefault(candidate => candidate.Name.Equals(layerName, StringComparison.OrdinalIgnoreCase));
            if (layer == null)
            {
                throw new ArgumentException($"Feature layer '{layerName}' not found.");
            }
            return layer;
        }
    }
}
