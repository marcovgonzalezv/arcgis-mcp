using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ArcGIS.Core.Geometry;
using ArcGIS.Desktop.Core;
using ArcGIS.Desktop.Framework.Threading.Tasks;
using ArcGIS.Desktop.Mapping;

namespace ArcGisMcpAddin.Commands
{
    public static class MapCommands
    {
        public static Task<object> GetActiveMapAsync()
        {
            return QueuedTask.Run<object>(() =>
            {
                var activeView = MapView.Active;
                if (activeView == null)
                {
                    throw new InvalidOperationException("No active map or scene view found in ArcGIS Pro.");
                }

                var map = activeView.Map;
                return new
                {
                    map_name = map?.Name ?? "None",
                    view_type = activeView.ViewingMode.ToString(), // 2D or 3D
                    camera = new
                    {
                        heading = SafeDouble(activeView.Camera.Heading),
                        pitch = SafeDouble(activeView.Camera.Pitch),
                        roll = SafeDouble(activeView.Camera.Roll),
                        x = SafeDouble(activeView.Camera.X),
                        y = SafeDouble(activeView.Camera.Y),
                        z = SafeDouble(activeView.Camera.Z)
                    }
                };
            });
        }

        private static double? SafeDouble(double value)
        {
            return double.IsFinite(value) ? value : null;
        }

        public static Task<object> ListLayersAsync(bool includeHidden)
        {
            return QueuedTask.Run<object>(() =>
            {
                var activeView = MapView.Active;
                if (activeView == null)
                {
                    throw new InvalidOperationException("No active map view found.");
                }

                var layers = activeView.Map.GetLayersAsFlattenedList();
                var layerList = new List<object>();

                foreach (var layer in layers)
                {
                    bool isVisible = layer.IsVisible;
                    if (!includeHidden && !isVisible) continue;

                    long? featureCount = null;
                    if (layer is FeatureLayer featLayer)
                    {
                        try
                        {
                            featureCount = featLayer.GetFeatureClass()?.GetCount() ?? 0;
                        }
                        catch { /* Ignore if geodatabase is locked or offline */ }
                    }

                    layerList.Add(new
                    {
                        name = layer.Name,
                        type = layer.GetType().Name.Replace("Layer", ""),
                        visible = isVisible,
                        count = featureCount
                    });
                }

                return new { layers = layerList };
            });
        }

        public static Task<object> ZoomToLayerAsync(string layerName)
        {
            return QueuedTask.Run<object>(() =>
            {
                var activeView = MapView.Active;
                if (activeView == null)
                {
                    throw new InvalidOperationException("No active map view found.");
                }

                var layer = activeView.Map.GetLayersAsFlattenedList().FirstOrDefault(l => l.Name.Equals(layerName, StringComparison.OrdinalIgnoreCase));
                if (layer == null)
                {
                    throw new ArgumentException($"Layer '{layerName}' not found in the active map.");
                }

                activeView.ZoomTo(layer);
                return new { success = true, layer_name = layerName };
            });
        }

        public static Task<object> ToggleLayerVisibilityAsync(string layerName, bool visible)
        {
            return QueuedTask.Run<object>(() =>
            {
                var activeView = MapView.Active;
                if (activeView == null)
                {
                    throw new InvalidOperationException("No active map view found.");
                }

                var layer = activeView.Map.GetLayersAsFlattenedList().FirstOrDefault(l => l.Name.Equals(layerName, StringComparison.OrdinalIgnoreCase));
                if (layer == null)
                {
                    throw new ArgumentException($"Layer '{layerName}' not found in the active map.");
                }

                layer.SetVisibility(visible);
                return new { success = true, layer_name = layerName, visible };
            });
        }

        public static Task<object> SetMapExtentAsync(double xmin, double ymin, double xmax, double ymax, int wkid)
        {
            return QueuedTask.Run<object>(() =>
            {
                var activeView = MapView.Active;
                if (activeView == null)
                {
                    throw new InvalidOperationException("No active map view found.");
                }

                var spatialRef = SpatialReferenceBuilder.CreateSpatialReference(wkid);
                var envelope = EnvelopeBuilderEx.CreateEnvelope(xmin, ymin, xmax, ymax, spatialRef);

                activeView.ZoomTo(envelope);
                return new { success = true, xmin, ymin, xmax, ymax, wkid };
            });
        }

        public static Task<object> AddLayerToMapAsync(string dataPath, string layerName)
        {
            return QueuedTask.Run<object>(() =>
            {
                var activeView = MapView.Active;
                if (activeView == null)
                {
                    throw new InvalidOperationException("No active map view found.");
                }

                var layer = LayerFactory.Instance.CreateLayer(new Uri(dataPath), activeView.Map);
                if (!string.IsNullOrWhiteSpace(layerName))
                {
                    layer.SetName(layerName);
                }

                return new { success = true, layer_name = layer.Name, data_path = dataPath };
            });
        }

        public static Task<object> SetLayerTransparencyAsync(string layerName, double transparency)
        {
            return QueuedTask.Run<object>(() =>
            {
                if (transparency < 0 || transparency > 100)
                {
                    throw new ArgumentOutOfRangeException(nameof(transparency), "Transparency must be between 0 and 100.");
                }

                var layer = GetLayer(layerName);
                layer.SetTransparency(transparency);
                return new { success = true, layer_name = layerName, transparency };
            });
        }

        public static Task<object> SetDefinitionQueryAsync(string layerName, string sqlFilter)
        {
            return QueuedTask.Run<object>(() =>
            {
                var layer = GetFeatureLayer(layerName);
                layer.SetDefinitionQuery(string.IsNullOrWhiteSpace(sqlFilter) ? null : sqlFilter);
                return new { success = true, layer_name = layerName, sql_filter = sqlFilter ?? string.Empty };
            });
        }

        public static Task<object> ClearSelectionAsync(string layerName)
        {
            return QueuedTask.Run<object>(() =>
            {
                if (string.IsNullOrWhiteSpace(layerName))
                {
                    var activeView = MapView.Active;
                    if (activeView == null)
                    {
                        throw new InvalidOperationException("No active map view found.");
                    }

                    activeView.Map.ClearSelection();
                    return new { success = true, scope = "map" };
                }

                var layer = GetFeatureLayer(layerName);
                layer.ClearSelection();
                return new { success = true, scope = "layer", layer_name = layerName };
            });
        }

        public static async Task<object> SaveProjectAsync()
        {
            return await Task.Factory.StartNew(
                async () =>
                {
                    if (Project.Current == null)
                    {
                        throw new InvalidOperationException("No active project found in ArcGIS Pro.");
                    }

                    var projectName = Project.Current.Name;
                    var saved = await Project.Current.SaveAsync();
                    return (object)new { success = saved, project = projectName };
                },
                CancellationToken.None,
                TaskCreationOptions.None,
                QueuedTask.UIScheduler
            ).Unwrap();
        }

        private static Layer GetLayer(string layerName)
        {
            var activeView = MapView.Active;
            if (activeView == null)
            {
                throw new InvalidOperationException("No active map view found.");
            }

            var layer = activeView.Map.GetLayersAsFlattenedList()
                .FirstOrDefault(l => l.Name.Equals(layerName, StringComparison.OrdinalIgnoreCase));

            if (layer == null)
            {
                throw new ArgumentException($"Layer '{layerName}' not found in the active map.");
            }

            return layer;
        }

        private static FeatureLayer GetFeatureLayer(string layerName)
        {
            var layer = GetLayer(layerName) as FeatureLayer;
            if (layer == null)
            {
                throw new ArgumentException($"Feature layer '{layerName}' not found in the active map.");
            }

            return layer;
        }
    }
}
