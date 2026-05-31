using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using ArcGIS.Desktop.Core.Geoprocessing;
using ArcGIS.Desktop.Core;

namespace ArcGisMcpAddin.Commands
{
    public static class PortalCommands
    {
        public static Task<object> GetActivePortalAsync()
        {
            var portal = ArcGISPortalManager.Current.GetActivePortal();
            return Task.FromResult<object>(new
            {
                url = portal?.PortalUri?.ToString() ?? "",
                is_signed_in = portal?.IsSignedOn() ?? false,
                user = portal?.GetSignOnUsername() ?? ""
            });
        }

        public static async Task<object> PublishWebLayerAsync(
            string serviceDefinitionPath,
            string serverConnection,
            string serviceName,
            string folderType,
            string folder,
            string startupType,
            string overrideDefinition,
            string myContents,
            string publicShare,
            string organization,
            string groups)
        {
            if (string.IsNullOrWhiteSpace(serviceDefinitionPath))
            {
                throw new ArgumentException("Parameter 'service_definition_path' is required.");
            }

            if (!File.Exists(serviceDefinitionPath))
            {
                throw new FileNotFoundException($"Service definition file not found: {serviceDefinitionPath}", serviceDefinitionPath);
            }

            string extension = Path.GetExtension(serviceDefinitionPath);
            if (!extension.Equals(".sd", StringComparison.OrdinalIgnoreCase) &&
                !extension.Equals(".sddraft", StringComparison.OrdinalIgnoreCase))
            {
                throw new ArgumentException("Parameter 'service_definition_path' must point to an ArcGIS service definition (.sd) or draft (.sddraft) file.");
            }

            string uploadPath = extension.Equals(".sddraft", StringComparison.OrdinalIgnoreCase)
                ? (await StageServiceDefinitionFileAsync(serviceDefinitionPath, "")).Path
                : serviceDefinitionPath;

            var uploadValues = BuildUploadValueArray(
                uploadPath,
                string.IsNullOrWhiteSpace(serverConnection) ? "My Hosted Services" : serverConnection,
                serviceName,
                folderType,
                folder,
                startupType,
                overrideDefinition,
                myContents,
                publicShare,
                organization,
                groups);

            IGPResult result = await Geoprocessing.ExecuteToolAsync(
                "UploadServiceDefinition_server",
                Geoprocessing.MakeValueArray(uploadValues.ToArray()),
                null,
                null,
                null,
                GPExecuteToolFlags.None
            );

            var messages = CollectMessages(result);
            if (result.IsFailed)
            {
                throw new InvalidOperationException(string.Join("\n", messages));
            }

            return new
            {
                success = true,
                source_path = serviceDefinitionPath,
                uploaded_service_definition_path = uploadPath,
                server_connection = serverConnection,
                staged_from_draft = extension.Equals(".sddraft", StringComparison.OrdinalIgnoreCase),
                messages
            };
        }

        public static async Task<object> StageServiceDefinitionAsync(
            string serviceDraftPath,
            string outputServiceDefinitionPath)
        {
            var staged = await StageServiceDefinitionFileAsync(serviceDraftPath, outputServiceDefinitionPath);
            return new
            {
                success = true,
                service_draft_path = serviceDraftPath,
                service_definition_path = staged.Path,
                messages = staged.Messages
            };
        }

        private static async Task<(string Path, IReadOnlyList<string> Messages)> StageServiceDefinitionFileAsync(
            string draftPath,
            string outputServiceDefinitionPath)
        {
            if (string.IsNullOrWhiteSpace(draftPath))
            {
                throw new ArgumentException("Parameter 'service_draft_path' is required.");
            }

            if (!File.Exists(draftPath))
            {
                throw new FileNotFoundException($"Service draft file not found: {draftPath}", draftPath);
            }

            if (!Path.GetExtension(draftPath).Equals(".sddraft", StringComparison.OrdinalIgnoreCase))
            {
                throw new ArgumentException("Parameter 'service_draft_path' must point to an ArcGIS service definition draft (.sddraft) file.");
            }

            string serviceDefinitionPath = outputServiceDefinitionPath;
            if (string.IsNullOrWhiteSpace(serviceDefinitionPath))
            {
                string outputDirectory = Path.Combine(Path.GetTempPath(), "arcgis-mcp");
                Directory.CreateDirectory(outputDirectory);
                serviceDefinitionPath = Path.Combine(outputDirectory, $"{Path.GetFileNameWithoutExtension(draftPath)}_{Guid.NewGuid():N}.sd");
            }

            IGPResult result = await Geoprocessing.ExecuteToolAsync(
                "StageService_server",
                Geoprocessing.MakeValueArray(draftPath, serviceDefinitionPath),
                null,
                null,
                null,
                GPExecuteToolFlags.None
            );

            var messages = CollectMessages(result);
            if (result.IsFailed)
            {
                throw new InvalidOperationException(string.Join("\n", messages));
            }

            if (!File.Exists(serviceDefinitionPath))
            {
                throw new FileNotFoundException($"StageService did not create the expected service definition: {serviceDefinitionPath}", serviceDefinitionPath);
            }

            return (serviceDefinitionPath, messages);
        }

        private static IReadOnlyList<string> BuildUploadValueArray(
            string serviceDefinitionPath,
            string serverConnection,
            string serviceName,
            string folderType,
            string folder,
            string startupType,
            string overrideDefinition,
            string myContents,
            string publicShare,
            string organization,
            string groups)
        {
            var values = new List<string>
            {
                serviceDefinitionPath,
                serverConnection,
                serviceName,
                "",
                folderType,
                folder,
                startupType,
                overrideDefinition,
                myContents,
                publicShare,
                organization,
                groups
            };

            while (values.Count > 2 && string.IsNullOrWhiteSpace(values[values.Count - 1]))
            {
                values.RemoveAt(values.Count - 1);
            }

            return values;
        }

        private static string[] CollectMessages(IGPResult result)
        {
            return result.Messages?.Select(message => $"[{message.Type}] {message.Text}").ToArray()
                ?? Array.Empty<string>();
        }
    }
}
