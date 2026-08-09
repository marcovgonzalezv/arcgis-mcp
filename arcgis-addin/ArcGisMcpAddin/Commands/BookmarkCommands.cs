using System;
using System.Linq;
using System.Threading.Tasks;
using ArcGIS.Desktop.Framework.Threading.Tasks;
using ArcGIS.Desktop.Mapping;

namespace ArcGisMcpAddin.Commands
{
    /// <summary>
    /// Bookmark management. ``list_bookmarks`` lives in
    /// ProjectCommands; this class adds create and zoom operations against the
    /// active map view.
    /// </summary>
    public static class BookmarkCommands
    {
        public static async Task<object> CreateBookmarkAsync(string name)
        {
            var view = MapView.Active;
            if (view == null || view.Map == null)
            {
                throw new InvalidOperationException("No active map view to bookmark.");
            }

            // The public SDK creates a bookmark from the current view via
            // Map.AddBookmark(MapView, name).
            var bookmark = await QueuedTask.Run(() => view.Map.AddBookmark(view, name));
            return new { success = true, bookmark_name = bookmark?.Name ?? name };
        }

        public static Task<object> ZoomToBookmarkAsync(string name)
        {
            return QueuedTask.Run<object>(() =>
            {
                var view = MapView.Active;
                if (view == null || view.Map == null)
                {
                    throw new InvalidOperationException("No active map view.");
                }

                foreach (var bookmark in view.Map.GetBookmarks())
                {
                    if (bookmark.Name != null &&
                        bookmark.Name.Equals(name, StringComparison.OrdinalIgnoreCase))
                    {
                        view.ZoomTo(bookmark);
                        return new { success = true, bookmark_name = bookmark.Name };
                    }
                }

                throw new ArgumentException($"Bookmark '{name}' not found.");
            });
        }

        public static Task<object> DeleteBookmarkAsync(string name)
        {
            return QueuedTask.Run<object>(() =>
            {
                var view = MapView.Active;
                if (view == null || view.Map == null)
                {
                    throw new InvalidOperationException("No active map view.");
                }

                foreach (var bookmark in view.Map.GetBookmarks())
                {
                    if (bookmark.Name != null &&
                        bookmark.Name.Equals(name, StringComparison.OrdinalIgnoreCase))
                    {
                        view.Map.RemoveBookmark(bookmark);
                        return new { success = true, bookmark_name = bookmark.Name };
                    }
                }

                throw new ArgumentException($"Bookmark '{name}' not found.");
            });
        }
    }
}
