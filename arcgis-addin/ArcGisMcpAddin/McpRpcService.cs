using System.Text.Json;
using System.Threading.Tasks;

namespace ArcGisMcpAddin
{
    /// <summary>
    /// JSON-RPC service exposed over the Named Pipe via StreamJsonRpc.
    /// The single <see cref="InvokeAsync"/> method delegates to the existing
    /// <see cref="CommandHandler"/> dispatch, preserving the response envelope.
    /// </summary>
    public class McpRpcService
    {
        public async Task<JsonElement> InvokeAsync(string command, JsonElement parameters)
        {
            string requestJson = JsonSerializer.Serialize(new { command, @params = parameters });
            string responseJson = await CommandHandler.HandleAsync(requestJson);
            using var doc = JsonDocument.Parse(responseJson);
            return doc.RootElement.Clone();
        }
    }
}
