using System;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using ArcGIS.Core.CIM;
using ArcGIS.Desktop.Core;
using ArcGIS.Desktop.Framework.Threading.Tasks;
using ArcGIS.Desktop.Layouts;
using ArcGIS.Desktop.Mapping;

namespace ArcGisMcpAddin.Commands
{
    public static class ProjectCommands
    {
        public static Task<object> ListMapsAsync()
        {
            return QueuedTask.Run<object>(() =>
            {
                EnsureProject();
                var maps = Project.Current.GetItems<MapProjectItem>()
                    .Select(item => new { name = item.Name })
                    .ToList();
                return new { maps };
            });
        }

        public static async Task<object> OpenMapAsync(string mapName)
        {
            EnsureProject();
            var item = Project.Current.GetItems<MapProjectItem>()
                .FirstOrDefault(map => map.Name.Equals(mapName, StringComparison.OrdinalIgnoreCase));
            if (item == null)
            {
                throw new ArgumentException($"Map '{mapName}' not found.");
            }

            await item.OpenMapPaneAsync(MapViewingMode.Map);
            return new { success = true, map_name = mapName };
        }

        public static async Task<object> SaveProjectAsAsync(string outputPath, bool overwrite)
        {
            return await Task.Factory.StartNew(
                async () =>
                {
                    EnsureProject();
                    var saved = await Project.Current.SaveAsAsync(outputPath, overwrite);
                    return (object)new
                    {
                        success = saved,
                        output_path = outputPath
                    };
                },
                CancellationToken.None,
                TaskCreationOptions.None,
                QueuedTask.UIScheduler
            ).Unwrap();
        }

        public static Task<object> ListProjectItemsAsync()
        {
            return QueuedTask.Run<object>(() =>
            {
                EnsureProject();
                var items = Project.Current.GetItems<MapProjectItem>()
                    .Select(item => new { type = "Map", name = item.Name, path = "" })
                    .Cast<object>()
                    .Concat(Project.Current.GetItems<LayoutProjectItem>()
                        .Select(item => new { type = "Layout", name = item.Name, path = "" })
                        .Cast<object>())
                    .Append(new { type = "Project", name = Project.Current.Name, path = Project.Current.Path })
                    .ToList();
                return new { items };
            });
        }

        public static Task<object> ListBookmarksAsync(string mapName)
        {
            return QueuedTask.Run<object>(() =>
            {
                Map? map = null;
                if (!string.IsNullOrWhiteSpace(mapName))
                {
                    var item = Project.Current.GetItems<MapProjectItem>()
                        .FirstOrDefault(candidate => candidate.Name.Equals(mapName, StringComparison.OrdinalIgnoreCase));
                    map = item?.GetMap();
                }
                else
                {
                    map = MapView.Active?.Map;
                }

                if (map == null)
                {
                    throw new InvalidOperationException("No map available for bookmark listing.");
                }

                var bookmarks = map.GetBookmarks()
                    .Select(bookmark => new { name = bookmark.Name })
                    .ToList();
                return new { map_name = map.Name, bookmarks };
            });
        }

        private static void EnsureProject()
        {
            if (Project.Current == null)
            {
                throw new InvalidOperationException("No active project found in ArcGIS Pro.");
            }
        }
    }
}
