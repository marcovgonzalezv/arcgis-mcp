using System;
using ArcGIS.Desktop.Framework;
using ArcGIS.Desktop.Framework.Contracts;

namespace ArcGisMcpAddin
{
    public class Module1 : Module
    {
        private static Module1? _this = null;
        private readonly PipeServer _pipeServer = new();

        /// <summary>
        /// Retrieve the singleton instance of this module.
        /// </summary>
        public static Module1 Current => _this ??= (Module1)FrameworkApplication.FindModule("ArcGisMcpAddin_Module");

        public PipeServer Server => _pipeServer;

        #region Overrides
        /// <summary>
        /// Called when the Module is initialized by ArcGIS Pro on startup (due to autoLoad="true").
        /// </summary>
        protected override bool Initialize()
        {
            try
            {
                _pipeServer.Start();
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Failed to start MCP Pipe Server in Module initialization: {ex.Message}");
            }
            return base.Initialize();
        }

        /// <summary>
        /// Called when ArcGIS Pro is closing and unloading the module.
        /// </summary>
        protected override void Uninitialize()
        {
            try
            {
                _pipeServer.Stop();
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Failed to stop MCP Pipe Server during Module uninitialization: {ex.Message}");
            }
            base.Uninitialize();
        }

        /// <summary>
        /// Called when the module is asked if it can be unloaded.
        /// We allow unloading but clean up the server first.
        /// </summary>
        protected override bool CanUnload()
        {
            return true;
        }
        #endregion
    }

    /// <summary>
    /// UI Button control to check the status of the Named Pipe server.
    /// </summary>
    public class StatusButton : Button
    {
        protected override void OnClick()
        {
            var server = Module1.Current.Server;
            string status = server.IsRunning ? "Active and Running" : "Stopped / Inactive";

            ArcGIS.Desktop.Framework.Dialogs.MessageBox.Show(
                $"ArcGIS Pro MCP Server Bridge Status:\n\n" +
                $"Named Pipe: \\\\.\\pipe\\ArcGisMcpBridge\n" +
                $"Status: {status}\n\n" +
                $"The server starts automatically with ArcGIS Pro and communicates with the Python MCP agent.",
                "ArcGIS MCP Status",
                System.Windows.MessageBoxButton.OK,
                System.Windows.MessageBoxImage.Information
            );
        }
    }
}
