using System;
using System.IO.Pipes;
using System.Threading;
using System.Threading.Tasks;
using StreamJsonRpc;

namespace ArcGisMcpAddin
{
    public class PipeServer
    {
        private const string PipeName = "ArcGisMcpBridge";
        private CancellationTokenSource? _cts;
        private Task? _serverTask;

        public bool IsRunning => _serverTask != null && !_serverTask.IsCompleted;

        public void Start()
        {
            if (IsRunning) return;

            _cts = new CancellationTokenSource();
            _serverTask = Task.Run(() => ListenLoopAsync(_cts.Token));
            System.Diagnostics.Debug.WriteLine("ArcGIS MCP Named Pipe Server started (StreamJsonRpc).");
        }

        public void Stop()
        {
            if (!IsRunning) return;

            _cts?.Cancel();
            try
            {
                _serverTask?.Wait(1000);
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error stopping pipe server: {ex.Message}");
            }
            finally
            {
                _cts?.Dispose();
                _cts = null;
                _serverTask = null;
                System.Diagnostics.Debug.WriteLine("ArcGIS MCP Named Pipe Server stopped.");
            }
        }

        private async Task ListenLoopAsync(CancellationToken token)
        {
            while (!token.IsCancellationRequested)
            {
                NamedPipeServerStream? pipeServer = null;
                try
                {
                    pipeServer = new NamedPipeServerStream(
                        PipeName,
                        PipeDirection.InOut,
                        1,
                        PipeTransmissionMode.Byte,
                        PipeOptions.Asynchronous);

                    await pipeServer.WaitForConnectionAsync(token);

                    if (token.IsCancellationRequested) break;

                    var formatter = new JsonMessageFormatter();
                    var handler = new LengthHeaderMessageHandler(pipeServer, pipeServer, formatter);
                    using var rpc = new JsonRpc(handler);
                    rpc.AddLocalRpcTarget(new McpRpcService());
                    rpc.StartListening();

                    await rpc.Completion;
                }
                catch (OperationCanceledException)
                {
                    break;
                }
                catch (Exception ex)
                {
                    System.Diagnostics.Debug.WriteLine($"Pipe server connection error: {ex.Message}");
                    try { await Task.Delay(500, token); } catch { break; }
                }
                finally
                {
                    if (pipeServer != null)
                    {
                        await pipeServer.DisposeAsync();
                    }
                }
            }
        }
    }
}
