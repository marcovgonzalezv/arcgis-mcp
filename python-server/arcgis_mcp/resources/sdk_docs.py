def get_arcpy_reference() -> str:
    """
    Returns reference documentation and code snippets for Esri ArcPy scripting.
    """
    return """# ArcGIS Pro ArcPy Code Reference

ArcPy is a Python site package used to perform geographic data analysis, data conversion, data management, and map automation.

## 1. Core Module Import
```python
import arcpy
```

## 2. Setting Environments
```python
arcpy.env.workspace = r"C:\\Data\\MyGeodatabase.gdb"
arcpy.env.overwriteOutput = True
```

## 3. Geoprocessing Tools
```python
# Buffer: buffer inputs to a specified distance
arcpy.analysis.Buffer(
    in_features="highways",
    out_feature_class="highways_buf",
    buffer_distance_or_field="100 Meters"
)

# Clip: cut out input features using clip features boundary
arcpy.analysis.Clip(
    in_features="roads",
    clip_features="county_boundary",
    out_feature_class="county_roads"
)
```

## 4. Querying and Cursors
```python
# SearchCursor: Read features and fields
fields = ["NAME", "POPULATION"]
with arcpy.da.SearchCursor("cities", fields, "POPULATION > 100000") as cursor:
    for row in cursor:
        print(f"City: {row[0]}, Pop: {row[1]}")

# UpdateCursor: Modify existing data
with arcpy.da.UpdateCursor("cities", ["POPULATION"], "POPULATION < 0") as cursor:
    for row in cursor:
        row[0] = 0
        cursor.updateRow(row)
```

## 5. Projections & Spatial Reference
```python
# Get Spatial Reference of an existing dataset
spatial_ref = arcpy.Describe("cities").spatialReference
print(spatial_ref.name)  # e.g. "GCS_WGS_1984"

# Project a feature class to WGS 84
wgs84 = arcpy.SpatialReference(4326)
arcpy.management.Project("input_fc", "output_wgs84", wgs84)
```
"""


def get_addin_csharp_reference() -> str:
    """
    Returns reference documentation and code snippets for ArcGIS Pro SDK Add-Ins (C#).
    """
    return """# ArcGIS Pro SDK for .NET (C#) Reference

The ArcGIS Pro SDK for .NET helps you build add-ins and configurations that extend the ArcGIS Pro UI and integrate custom GIS logic.

## 1. Threading Model: UI Thread vs MCT (Main CIM Thread)
ArcGIS Pro requires all synchronous API methods to execute on the MCT. Use `QueuedTask.Run()`.

```csharp
// Execute synchronous GIS operations
await QueuedTask.Run(() => {
    var map = MapView.Active?.Map;
    if (map == null) return;

    var layers = map.GetLayersAsFlattenedList().OfType<FeatureLayer>();
    foreach (var layer in layers) {
        // Safe inside QueuedTask
        var count = layer.GetFeatureClass()?.GetCount() ?? 0;
    }
});
```

## 2. Executing Geoprocessing Tools
Geoprocessing is inherently asynchronous and does NOT run inside `QueuedTask.Run()`.

```csharp
using ArcGIS.Desktop.Core.Geoprocessing;

var parameters = Geoprocessing.MakeValueArray("highways", "highways_buf", "100 Meters");
IGPResult gpResult = await Geoprocessing.ExecuteToolAsync("Buffer_analysis", parameters);

if (gpResult.IsFailed) {
    foreach (var msg in gpResult.Messages) {
        System.Diagnostics.Debug.WriteLine($"GP Error: {msg.Text}");
    }
}
```

## 3. Controlling Map and Camera
```csharp
await QueuedTask.Run(() => {
    var activeView = MapView.Active;
    if (activeView == null) return;

    // Zoom to a specific layer
    var layer = activeView.Map.FindLayers("Rios").FirstOrDefault();
    if (layer != null) {
        activeView.ZoomTo(layer);
    }

    // Pan to coordinate box (WGS84 example)
    var envelope = EnvelopeBuilder.CreateEnvelope(xmin, ymin, xmax, ymax, SpatialReferences.WGS84);
    activeView.ZoomTo(envelope);
});
```

## 4. Manifest Registration (Config.daml)
Custom UI buttons and background tasks (modules) must be registered in the XML DAML file. Set `autoLoad="true"` to run code on startup:

```xml
<modules>
  <insertModule id="MyAddin_Module" className="Module1" autoLoad="true">
    <controls>
      <button id="MyAddin_Button" caption="My Button" className="MyButton" loadOnClick="true" />
    </controls>
  </insertModule>
</modules>
```
"""
