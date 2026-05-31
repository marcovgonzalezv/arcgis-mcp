using System;
using System.IO;
using System.IO.Pipes;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace ArcGisMcpAddin
{
    public class PipeServer
    {
        private const string PipeName = "ArcGisMcpBridge";
        private const int MaxRequestBytes = 10 * 1024 * 1024;
        private CancellationTokenSource? _cts;
        private Task? _serverTask;

        public bool IsRunning => _serverTask != null && !_serverTask.IsCompleted;

        public void Start()
        {
            if (IsRunning) return;

            _cts = new CancellationTokenSource();
            _serverTask = Task.Run(() => ListenLoopAsync(_cts.Token));
            System.Diagnostics.Debug.WriteLine("ArcGIS MCP Named Pipe Server started.");
        }

        public void Stop()
        {
            if (!IsRunning) return;

            _cts?.Cancel();
            try
            {
                // Wait briefly for the loop to clean up
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
                        PipeOptions.Asynchronous
                    );

                    await pipeServer.WaitForConnectionAsync(token);

                    if (token.IsCancellationRequested) break;

                    await ProcessClientRequestAsync(pipeServer, token);
                }
                catch (OperationCanceledException)
                {
                    break;
                }
                catch (Exception ex)
                {
                    System.Diagnostics.Debug.WriteLine($"Pipe server connection error: {ex.Message}");
                    await Task.Delay(500, token);
                }
                finally
                {
                    if (pipeServer != null)
                    {
                        try
                        {
                            if (pipeServer.IsConnected)
                            {
                                pipeServer.Disconnect();
                            }
                        }
                        catch (IOException ex)
                        {
                            System.Diagnostics.Debug.WriteLine($"Pipe disconnect error: {ex.Message}");
                        }
                        catch (InvalidOperationException ex)
                        {
                            System.Diagnostics.Debug.WriteLine($"Pipe disconnect skipped: {ex.Message}");
                        }
                        pipeServer.Dispose();
                    }
                }
            }
        }

        private async Task ProcessClientRequestAsync(NamedPipeServerStream pipeStream, CancellationToken token)
        {
            byte[] lengthBytes = await ReadExactlyAsync(pipeStream, sizeof(int), token);
            int requestLength = BitConverter.ToInt32(lengthBytes, 0);

            if (requestLength <= 0 || requestLength > MaxRequestBytes)
            {
                return;
            }

            byte[] requestBytes = await ReadExactlyAsync(pipeStream, requestLength, token);
            string requestJson = Encoding.UTF8.GetString(requestBytes);
            string responseJson = await CommandHandler.HandleAsync(requestJson);

            byte[] responseBytes = Encoding.UTF8.GetBytes(responseJson);
            byte[] responseLength = BitConverter.GetBytes(responseBytes.Length);

            await pipeStream.WriteAsync(responseLength.AsMemory(0, responseLength.Length), token);
            await pipeStream.WriteAsync(responseBytes.AsMemory(0, responseBytes.Length), token);
            await pipeStream.FlushAsync(token);
            pipeStream.WaitForPipeDrain();
        }

        private static async Task<byte[]> ReadExactlyAsync(Stream stream, int length, CancellationToken token)
        {
            byte[] buffer = new byte[length];
            int offset = 0;

            while (offset < length)
            {
                int read = await stream.ReadAsync(buffer.AsMemory(offset, length - offset), token);
                if (read == 0)
                {
                    throw new EndOfStreamException("The client disconnected before the full request was read.");
                }

                offset += read;
            }

            return buffer;
        }
    }
}
