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
    public static class EditingCommands
    {
        private static EditOperation? LastOperation { get; set; }

        public static async Task<object> UpdateAttributesAsync(
            string layerName,
            long objectId,
            Dictionary<string, object?> attributes)
        {
            var operation = await QueuedTask.Run(() =>
            {
                var layer = GetFeatureLayer(layerName);
                var editOperation = new EditOperation
                {
                    Name = $"MCP update attributes {layerName}:{objectId}"
                };
                editOperation.Modify(layer, objectId, attributes);
                return editOperation;
            });

            if (!await operation.ExecuteAsync())
            {
                throw new InvalidOperationException(operation.ErrorMessage);
            }

            LastOperation = operation;
            return new { success = true, layer_name = layerName, object_id = objectId };
        }

        public static async Task<object> CreateFeatureAsync(
            string layerName,
            double x,
            double y,
            int wkid,
            Dictionary<string, object?> attributes)
        {
            var operation = await QueuedTask.Run(() =>
            {
                var layer = GetFeatureLayer(layerName);
                var spatialReference = SpatialReferenceBuilder.CreateSpatialReference(wkid);
                var point = MapPointBuilderEx.CreateMapPoint(x, y, spatialReference);
                var editOperation = new EditOperation
                {
                    Name = $"MCP create feature {layerName}"
                };
                editOperation.Create(layer, point, attributes);
                return editOperation;
            });

            if (!await operation.ExecuteAsync())
            {
                throw new InvalidOperationException(operation.ErrorMessage);
            }

            LastOperation = operation;
            return new { success = true, layer_name = layerName, x, y, wkid };
        }

        public static async Task<object> DeleteSelectedFeaturesAsync(string layerName)
        {
            var payload = await QueuedTask.Run(() =>
            {
                var layer = GetFeatureLayer(layerName);
                using var selection = layer.GetSelection();
                var ids = selection.GetObjectIDs().ToList();
                if (!ids.Any())
                {
                    throw new InvalidOperationException($"Layer '{layerName}' has no selected features.");
                }
                var editOperation = new EditOperation
                {
                    Name = $"MCP delete selected {layerName}"
                };
                editOperation.Delete(layer, ids);
                return new { operation = editOperation, count = ids.Count };
            });

            if (!await payload.operation.ExecuteAsync())
            {
                throw new InvalidOperationException(payload.operation.ErrorMessage);
            }

            LastOperation = payload.operation;
            return new { success = true, layer_name = layerName, deleted_count = payload.count };
        }

        public static async Task<object> UndoLastEditAsync()
        {
            if (LastOperation == null)
            {
                throw new InvalidOperationException("No MCP edit operation is available to undo.");
            }

            if (!await LastOperation.UndoAsync())
            {
                throw new InvalidOperationException("ArcGIS Pro could not undo the last MCP edit operation.");
            }

            LastOperation = null;
            return new { success = true };
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
