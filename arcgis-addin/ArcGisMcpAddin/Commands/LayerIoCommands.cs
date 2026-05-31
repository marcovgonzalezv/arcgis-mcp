using System;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using ArcGIS.Desktop.Core.Geoprocessing;
using ArcGIS.Desktop.Framework.Threading.Tasks;
using ArcGIS.Desktop.Mapping;

namespace ArcGisMcpAddin.Commands
{
    public static class LayerIoCommands
    {
        public static async Task<object> SaveLayerFileAsync(string layerName, string outputPath)
        {
            EnsureDirectory(outputPath);
            var result = await ExecuteGpAsync(
                "SaveToLayerFile_management",
                Geoprocessing.MakeValueArray(layerName, outputPath, "ABSOLUTE")
            );
            return new { success = true, layer_name = layerName, output_path = outputPath, messages = result };
        }

        public static Task<object> LoadLayerFileAsync(string layerFilePath)
        {
            return QueuedTask.Run<object>(() =>
            {
                var map = MapView.Active?.Map;
                if (map == null)
                {
                    throw new InvalidOperationException("No active map view found.");
                }

                var layer = LayerFactory.Instance.CreateLayer(new Uri(layerFilePath), map);
                return new { success = true, layer_name = layer.Name, layer_file_path = layerFilePath };
            });
        }

        public static async Task<object> ExportLayerAsync(string layerName, string outputPath, string whereClause)
        {
            EnsureDirectory(outputPath);
            var valueArray = string.IsNullOrWhiteSpace(whereClause)
                ? Geoprocessing.MakeValueArray(layerName, outputPath)
                : Geoprocessing.MakeValueArray(layerName, outputPath, whereClause);
            var result = await ExecuteGpAsync("ExportFeatures_conversion", valueArray);
            return new { success = true, layer_name = layerName, output_path = outputPath, messages = result };
        }

        public static Task<object> RemoveLayerAsync(string layerName)
        {
            return QueuedTask.Run<object>(() =>
            {
                var map = MapView.Active?.Map;
                if (map == null)
                {
                    throw new InvalidOperationException("No active map view found.");
                }

                var layer = map.GetLayersAsFlattenedList()
                    .FirstOrDefault(candidate => candidate.Name.Equals(layerName, StringComparison.OrdinalIgnoreCase));
                if (layer == null)
                {
                    throw new ArgumentException($"Layer '{layerName}' not found.");
                }

                map.RemoveLayer(layer);
                return new { success = true, layer_name = layerName };
            });
        }

        private static async Task<string[]> ExecuteGpAsync(string toolName, System.Collections.Generic.IEnumerable<string> valueArray)
        {
            IGPResult result = await Geoprocessing.ExecuteToolAsync(
                toolName,
                valueArray,
                null,
                null,
                null,
                GPExecuteToolFlags.None
            );
            var messages = result.Messages?.Select(message => $"[{message.Type}] {message.Text}").ToArray()
                ?? Array.Empty<string>();
            if (result.IsFailed)
            {
                throw new InvalidOperationException(string.Join("\n", messages));
            }
            return messages;
        }

        private static void EnsureDirectory(string outputPath)
        {
            var directory = Path.GetDirectoryName(outputPath);
            if (!string.IsNullOrWhiteSpace(directory) && !Directory.Exists(directory))
            {
                Directory.CreateDirectory(directory);
            }
        }
    }
}
