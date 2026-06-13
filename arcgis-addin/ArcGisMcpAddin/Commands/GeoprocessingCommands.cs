using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using ArcGIS.Desktop.Core.Geoprocessing;

namespace ArcGisMcpAddin.Commands
{
    public static class GeoprocessingCommands
    {
        private static readonly string[] DestructiveToolTokens = { "delete", "truncate" };

        public static async Task<object> RunGpToolAsync(
            string toolName,
            string[] parameters,
            bool allowDelete,
            bool addOutputsToMap)
        {
            if (IsDestructiveTool(toolName) && !DeletionAllowed(allowDelete))
            {
                throw new InvalidOperationException(
                    $"Blocked destructive geoprocessing tool '{toolName}'. Pass allow_delete=true or set ARCGIS_MCP_ALLOW_DELETE=true to allow it.");
            }

            // ExecuteToolAsync is inherently asynchronous and manages its own threading.
            // Do NOT wrap this call in QueuedTask.Run() to avoid blocking the MCT thread.
            var valueArray = Geoprocessing.MakeValueArray(parameters);
            var flags = addOutputsToMap ? GPExecuteToolFlags.AddOutputsToMap : GPExecuteToolFlags.None;

            IGPResult result = await Geoprocessing.ExecuteToolAsync(toolName, valueArray, null, null, null, flags);

            var messages = new List<string>();
            if (result.Messages != null)
            {
                foreach (var msg in result.Messages)
                {
                    messages.Add($"[{msg.Type}] {msg.Text}");
                }
            }

            if (result.IsFailed)
            {
                string errorMsgs = string.Join("\n", messages.Where(m => m.Contains("[Error]")));
                throw new InvalidOperationException($"Geoprocessing tool '{toolName}' failed to execute.\nErrors:\n{errorMsgs}");
            }

            var outputs = result.Values?.Select(value => value?.ToString() ?? "").ToList() ?? new List<string>();

            return new
            {
                tool_name = toolName,
                success = true,
                messages = messages,
                outputs = outputs,
                return_value = result.ReturnValue,
                add_outputs_to_map = addOutputsToMap
            };
        }

        private static bool IsDestructiveTool(string toolName)
        {
            return DestructiveToolTokens.Any(
                token => toolName.Contains(token, StringComparison.OrdinalIgnoreCase));
        }

        private static bool DeletionAllowed(bool allowDelete)
        {
            string value = Environment.GetEnvironmentVariable("ARCGIS_MCP_ALLOW_DELETE") ?? "";
            return allowDelete || value.Equals("1", StringComparison.OrdinalIgnoreCase)
                || value.Equals("true", StringComparison.OrdinalIgnoreCase)
                || value.Equals("yes", StringComparison.OrdinalIgnoreCase)
                || value.Equals("y", StringComparison.OrdinalIgnoreCase)
                || value.Equals("on", StringComparison.OrdinalIgnoreCase);
        }
    }
}
