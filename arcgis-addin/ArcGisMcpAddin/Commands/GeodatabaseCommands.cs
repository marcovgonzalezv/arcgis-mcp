using System;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using ArcGIS.Core.Data;
using ArcGIS.Desktop.Core.Geoprocessing;
using ArcGIS.Desktop.Framework.Threading.Tasks;
using ArcGIS.Desktop.Mapping;

namespace ArcGisMcpAddin.Commands
{
    public static class GeodatabaseCommands
    {
        public static Task<object> ListFeatureClassesAsync(string workspacePath)
        {
            return QueuedTask.Run<object>(() =>
            {
                using var geodatabase = OpenFileGeodatabase(workspacePath);
                var featureClasses = geodatabase.GetDefinitions<FeatureClassDefinition>()
                    .Select(definition => definition.GetName())
                    .ToList();
                return new { workspace_path = workspacePath, feature_classes = featureClasses };
            });
        }

        public static Task<object> ListDomainsAsync(string workspacePath)
        {
            return QueuedTask.Run<object>(() =>
            {
                using var geodatabase = OpenFileGeodatabase(workspacePath);
                var domains = geodatabase.GetDomains()
                    .Select(domain => new { name = domain.GetName(), type = domain.GetType().Name })
                    .ToList();
                return new { workspace_path = workspacePath, domains };
            });
        }

        public static async Task<object> CreateDomainAsync(
            string workspacePath,
            string domainName,
            string fieldType,
            string domainType,
            string description)
        {
            var result = await Geoprocessing.ExecuteToolAsync(
                "CreateDomain_management",
                Geoprocessing.MakeValueArray(workspacePath, domainName, description, fieldType, domainType),
                null,
                null,
                null,
                GPExecuteToolFlags.None
            );
            if (result.IsFailed)
            {
                var messages = result.Messages?.Select(message => $"[{message.Type}] {message.Text}") ?? Enumerable.Empty<string>();
                throw new InvalidOperationException(string.Join("\n", messages));
            }
            return new { success = true, workspace_path = workspacePath, domain_name = domainName };
        }

        public static Task<object> DescribeDatasetAsync(string datasetPath)
        {
            return QueuedTask.Run<object>(() =>
            {
                var geodatabaseDescription = TryDescribeFileGeodatabaseDataset(datasetPath);
                if (geodatabaseDescription != null)
                {
                    return geodatabaseDescription;
                }

                var layer = MapView.Active?.Map?.GetLayersAsFlattenedList()
                    .OfType<FeatureLayer>()
                    .FirstOrDefault(candidate =>
                        candidate.Name.Equals(datasetPath, StringComparison.OrdinalIgnoreCase)
                        || candidate.GetPath()?.LocalPath.Equals(datasetPath, StringComparison.OrdinalIgnoreCase) == true);

                if (layer == null)
                {
                    throw new ArgumentException("Dataset description requires an active-map feature layer name/path or a feature class path inside a file geodatabase.");
                }

                using var featureClass = layer.GetFeatureClass();
                using var definition = featureClass.GetDefinition();
                var fields = definition.GetFields()
                    .Select(field => new { name = field.Name, alias = field.AliasName, type = field.FieldType.ToString() })
                    .ToList();
                return new
                {
                    name = layer.Name,
                    type = "FeatureLayer",
                    path = layer.GetPath()?.LocalPath ?? "",
                    geometry_type = definition.GetShapeType().ToString(),
                    count = featureClass.GetCount(),
                    fields
                };
            });
        }

        private static object? TryDescribeFileGeodatabaseDataset(string datasetPath)
        {
            string? geodatabasePath = FindFileGeodatabasePath(datasetPath);
            if (geodatabasePath == null)
            {
                return null;
            }

            string datasetName = datasetPath.Length == geodatabasePath.Length
                ? string.Empty
                : datasetPath[(geodatabasePath.Length + 1)..].Replace(Path.DirectorySeparatorChar, '\\');

            using var geodatabase = OpenFileGeodatabase(geodatabasePath);
            if (string.IsNullOrWhiteSpace(datasetName))
            {
                var featureClasses = geodatabase.GetDefinitions<FeatureClassDefinition>()
                    .Select(definition => definition.GetName())
                    .ToList();
                return new
                {
                    name = Path.GetFileName(geodatabasePath),
                    type = "FileGeodatabase",
                    path = geodatabasePath,
                    feature_classes = featureClasses
                };
            }

            using var featureClass = geodatabase.OpenDataset<FeatureClass>(datasetName);
            using var definition = featureClass.GetDefinition();
            var fields = definition.GetFields()
                .Select(field => new { name = field.Name, alias = field.AliasName, type = field.FieldType.ToString() })
                .ToList();

            return new
            {
                name = definition.GetName(),
                type = "FeatureClass",
                path = datasetPath,
                workspace_path = geodatabasePath,
                geometry_type = definition.GetShapeType().ToString(),
                count = featureClass.GetCount(),
                fields
            };
        }

        private static string? FindFileGeodatabasePath(string datasetPath)
        {
            var fullPath = Path.GetFullPath(datasetPath);
            var marker = ".gdb";
            var index = fullPath.IndexOf(marker, StringComparison.OrdinalIgnoreCase);
            if (index < 0)
            {
                return null;
            }

            var geodatabasePath = fullPath[..(index + marker.Length)];
            return Directory.Exists(geodatabasePath) ? geodatabasePath : null;
        }

        private static Geodatabase OpenFileGeodatabase(string workspacePath)
        {
            if (!Directory.Exists(workspacePath) || !workspacePath.EndsWith(".gdb", StringComparison.OrdinalIgnoreCase))
            {
                throw new ArgumentException("workspace_path must be an existing file geodatabase path ending in .gdb.");
            }

            return new Geodatabase(new FileGeodatabaseConnectionPath(new Uri(workspacePath)));
        }
    }
}
