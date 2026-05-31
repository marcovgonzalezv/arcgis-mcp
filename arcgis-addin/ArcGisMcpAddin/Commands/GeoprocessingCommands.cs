using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using ArcGIS.Desktop.Core.Geoprocessing;

namespace ArcGisMcpAddin.Commands
{
    public static class GeoprocessingCommands
    {
        public static async Task<object> RunGpToolAsync(string toolName, string[] parameters)
        {
            // ExecuteToolAsync is inherently asynchronous and manages its own threading.
            // Do NOT wrap this call in QueuedTask.Run() to avoid blocking the MCT thread.
            var valueArray = Geoprocessing.MakeValueArray(parameters);

            IGPResult result = await Geoprocessing.ExecuteToolAsync(toolName, valueArray, null, null, null, GPExecuteToolFlags.None);

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

            return new
            {
                tool_name = toolName,
                success = true,
                messages = messages
            };
        }
    }
}
