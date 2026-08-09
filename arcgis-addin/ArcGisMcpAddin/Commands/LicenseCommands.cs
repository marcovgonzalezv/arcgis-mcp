using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using ArcGIS.Core.Licensing;
using ArcGIS.Desktop.Framework.Threading.Tasks;

namespace ArcGisMcpAddin.Commands
{
    /// <summary>
    /// License and extension availability checks.
    ///
    /// Mirrors the arcpy.CheckExtension / arcpy.ProductInfo semantics so the
    /// Python licensing module can decide whether a wrapper is allowed to run
    /// without triggering a cryptic geoprocessing failure.
    /// </summary>
    public static class LicenseCommands
    {
        /// <summary>
        /// ArcPy extension codes recognised by LicenseInformation and the
        /// Python EXTENSIONS catalogue. The string values match the arcpy
        /// CheckExtension / CheckOutExtension codes exactly.
        /// Reference: https://doc.esri.com/en/arcgis-pro/latest/arcpy/functions/checkextension.html
        /// </summary>
        private static readonly string[] ExtensionCodes =
        {
            "3D", "Spatial", "Network", "GeoStats", "ImageAnalyst",
            "DataReviewer", "DataInteroperability", "Airports", "Aeronautical",
            "Bathymetry", "BusinessPrem", "Defense", "Foundation", "Indoors",
            "LocationReferencing", "LocateXT", "Nautical", "Publisher",
            "SMPNorthAmerica", "SMPEurope", "SMPAsiaPacific", "SMPJapan",
            "SMPLatinAmerica", "SMPMiddleEastAfrica", "ArcScan", "Schematics",
            "Tracking", "JTX"
        };

        /// <summary>
        /// Map of arcpy extension code -> LicenseCodes enum member name used by
        /// the Pro SDK. ArcPy and the .NET SDK do not share the same string
        /// identifiers, so we translate here.
        /// Reference: https://pro.arcgis.com/en/pro-app/latest/sdk/api-reference/topic8897.htm
        /// </summary>
        private static readonly Dictionary<string, string> CodeToLicenseCodes = new()
        {
            { "3D", "Analyst3D" },
            { "Spatial", "SpatialAnalyst" },
            { "Network", "NetworkAnalyst" },
            { "GeoStats", "GeostatisticalAnalyst" },
            { "ImageAnalyst", "ImageAnalyst" },
            { "DataReviewer", "DataReviewer" },
            { "DataInteroperability", "DataInteroperability" },
            { "Airports", "AviationAirports" },
            { "Aeronautical", "AviationCharting" },
            { "Bathymetry", "Bathymetry" },
            { "BusinessPrem", "BusinessAnalyst" },
            { "Defense", "DefenseMapping" },
            { "Foundation", "Foundation" },
            { "Indoors", "Indoors" },
            { "LocationReferencing", "LocationReferencing" },
            { "LocateXT", "LocateXT" },
            { "Nautical", "MaritimeCharting" },
            { "Publisher", "Publisher" },
            { "SMPNorthAmerica", "StreetMapPremiumNorthAmerica" },
            { "SMPEurope", "StreetMapPremiumEurope" },
            { "SMPAsiaPacific", "StreetMapPremiumAsiaPacific" },
            { "SMPJapan", "StreetMapPremiumJapan" },
            { "SMPLatinAmerica", "StreetMapPremiumLatinAmerica" },
            { "SMPMiddleEastAfrica", "StreetMapPremiumMiddleEastAfrica" },
            { "ArcScan", "ArcScan" },
            { "Schematics", "Schematics" },
            { "Tracking", "TrackingAnalyst" },
            { "JTX", "WorkflowManager" }
        };

        public static Task<object> CheckLicenseAsync()
        {
            return QueuedTask.Run<object>(() =>
            {
                var level = LicenseInformation.Level.ToString();
                var active = new List<string>();

                foreach (var code in ExtensionCodes)
                {
                    if (IsExtensionCheckedOut(code))
                    {
                        active.Add(code);
                    }
                }

                return new
                {
                    level = level,
                    product = level,
                    extensions = active
                };
            });
        }

        /// <summary>
        /// Returns true if the given arcpy extension code is currently checked
        /// out (licensed and active) in this session. Uses
        /// LicenseInformation.IsCheckedOut when a LicenseCodes mapping exists;
        /// otherwise reports the extension as unavailable so the Python layer
        /// can refuse the operation safely.
        /// </summary>
        private static bool IsExtensionCheckedOut(string arcpyCode)
        {
            if (!CodeToLicenseCodes.TryGetValue(arcpyCode, out var enumName))
            {
                return false;
            }

            try
            {
                if (Enum.TryParse(typeof(LicenseCodes), enumName, out var parsed) &&
                    parsed is LicenseCodes code)
                {
                    return LicenseInformation.IsCheckedOut(code);
                }
            }
            catch
            {
                // Some enum members only exist on newer Pro builds; treat as
                // unavailable rather than crashing the whole license probe.
            }

            return false;
        }
    }
}
