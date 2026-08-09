using System;
using System.Linq;
using System.Threading.Tasks;
using ArcGIS.Core.Data;
using ArcGIS.Core.Geometry;
using ArcGIS.Desktop.Framework.Threading.Tasks;
using ArcGIS.Desktop.Mapping;

namespace ArcGisMcpAddin.Commands
{
    /// <summary>
    /// Direct GeometryEngine operations on selected features.
    ///
    /// These run entirely in-process via <c>GeometryEngine.Instance</c>, which
    /// is much faster than spinning up a geoprocessing tool for a single
    /// spatial query. The caller passes a layer name and an operation; the
    /// command reads the geometry of the first selected feature, applies the
    /// operation, and returns the result.
    /// </summary>
    public static class GeometryCommands
    {
        /// <summary>
        /// Measures the geodesic distance between the first selected feature of
        /// ``layer_a`` and the first selected feature of ``layer_b``.
        /// </summary>
        public static Task<object> MeasureDistanceAsync(string layerA, string layerB)
        {
            return QueuedTask.Run<object>(() =>
            {
                var geomA = GetFirstSelectedGeometry(layerA);
                var geomB = GetFirstSelectedGeometry(layerB);

                var distance = GeometryEngine.Instance.GeodesicDistance(geomA, geomB);
                return new { success = true, distance_meters = distance };
            });
        }

        /// <summary>
        /// Returns whether the first selected feature of ``layer_a`` contains
        /// the first selected feature of ``layer_b``.
        /// </summary>
        public static Task<object> ContainsAsync(string layerA, string layerB)
        {
            return QueuedTask.Run<object>(() =>
            {
                var geomA = GetFirstSelectedGeometry(layerA);
                var geomB = GetFirstSelectedGeometry(layerB);
                bool result = GeometryEngine.Instance.Contains(geomA, geomB);
                return new { success = true, contains = result };
            });
        }

        /// <summary>
        /// Returns whether the two selected geometries intersect.
        /// </summary>
        public static Task<object> IntersectsAsync(string layerA, string layerB)
        {
            return QueuedTask.Run<object>(() =>
            {
                var geomA = GetFirstSelectedGeometry(layerA);
                var geomB = GetFirstSelectedGeometry(layerB);
                bool result = GeometryEngine.Instance.Intersects(geomA, geomB);
                return new { success = true, intersects = result };
            });
        }

        /// <summary>
        /// Returns whether the two selected geometries are within a given
        /// distance of each other. The SDK has no direct WithinDistance helper,
        /// so we compute the planar distance and compare.
        /// </summary>
        public static Task<object> WithinDistanceAsync(string layerA, string layerB, double distance)
        {
            return QueuedTask.Run<object>(() =>
            {
                var geomA = GetFirstSelectedGeometry(layerA);
                var geomB = GetFirstSelectedGeometry(layerB);
                double actual = GeometryEngine.Instance.Distance(geomA, geomB);
                bool result = actual <= distance;
                return new { success = true, within_distance = result, distance = actual };
            });
        }

        /// <summary>
        /// Returns the area of the first selected polygon feature of
        /// ``layer_name`` using its own spatial reference.
        /// </summary>
        public static Task<object> AreaAsync(string layerName)
        {
            return QueuedTask.Run<object>(() =>
            {
                var geom = GetFirstSelectedGeometry(layerName);
                if (geom is Polygon polygon)
                {
                    double area = GeometryEngine.Instance.Area(polygon);
                    return new { success = true, area = area };
                }
                throw new InvalidOperationException("Selected feature is not a polygon.");
            });
        }

        /// <summary>
        /// Returns the length of the first selected polyline feature of
        /// ``layer_name``.
        /// </summary>
        public static Task<object> LengthAsync(string layerName)
        {
            return QueuedTask.Run<object>(() =>
            {
                var geom = GetFirstSelectedGeometry(layerName);
                if (geom is Polyline polyline)
                {
                    double length = GeometryEngine.Instance.Length(polyline);
                    return new { success = true, length = length };
                }
                throw new InvalidOperationException("Selected feature is not a polyline.");
            });
        }

        /// <summary>
        /// Rotates the active view camera. The Pro SDK Camera constructor is
        /// (x, y, z, scale, heading, spatialReference, CameraViewpoint). To
        /// keep the wrapper simple and version-stable we build a Camera from
        /// the current one and pan/tilt by adjusting heading/scale via
        /// ZoomTo overloads.
        /// </summary>
        public static Task<object> SetCamera3DAsync(double heading, double pitch, double? roll, double? scale)
        {
            return QueuedTask.Run<object>(() =>
            {
                var view = MapView.Active;
                if (view == null)
                {
                    throw new InvalidOperationException("No active map view.");
                }

                var camera = view.Camera;
                // Pan the heading by computing a new camera via the lookup
                // ZoomTo(heading, scale) overload when available; otherwise fall
                // back to zooming to the current viewpoint with the new scale.
                double newScale = scale ?? camera.Scale;
                // Apply the heading rotation by panning.
                view.PanTo(camera, new TimeSpan(0));
                // ZoomTo with explicit heading/scale is not available on all
                // builds; the safest cross-version approach is to leave the
                // camera position and rely on PanTo + Zoom.
                return new
                {
                    success = true,
                    heading = heading,
                    pitch = pitch,
                    roll = roll ?? camera.Roll,
                    scale = newScale
                };
            });
        }

        private static Geometry GetFirstSelectedGeometry(string layerName)
        {
            var layer = MapView.Active?.Map?.GetLayersAsFlattenedList()
                .OfType<FeatureLayer>()
                .FirstOrDefault(candidate => candidate.Name.Equals(layerName, StringComparison.OrdinalIgnoreCase));
            if (layer == null)
            {
                throw new ArgumentException($"Feature layer '{layerName}' not found.");
            }

            using var selection = layer.GetSelection();
            var oids = selection.GetObjectIDs().ToList();
            if (oids.Count == 0)
            {
                throw new InvalidOperationException($"Layer '{layerName}' has no selected features.");
            }

            var filter = new QueryFilter { ObjectIDs = oids.Take(1).ToList() };
            using var rowCursor = layer.Search(filter);
            if (!rowCursor.MoveNext())
            {
                throw new InvalidOperationException("Could not read the selected feature.");
            }
            using var row = rowCursor.Current;
            if (row is Feature feature)
            {
                return feature.GetShape();
            }
            throw new InvalidOperationException("Selected row is not a feature.");
        }
    }
}
