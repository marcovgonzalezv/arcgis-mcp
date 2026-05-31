def arcpy_script(task_description: str) -> str:
    """
    Returns a prompt template for writing a high-quality,
    production-ready ArcPy automation script for a specific task.
    """
    return f"""Please write a production-grade, standalone ArcPy Python script to accomplish the following task:
"{task_description}"

Follow these development guidelines and best practices:
1. Always import 'arcpy' and handle exceptions using a try-except block.
2. Utilize 'arcpy.env.overwriteOutput = True' so scripts can run repeatedly.
3. Use geodatabases (.gdb) or well-known folder paths for workspaces.
4. Keep memory optimization in mind (e.g. clean up cursors using 'with' statements).
5. Add clear, descriptive comments explaining each step of the geoprocessing workflow.
6. Provide error logging using 'arcpy.AddError()' and general printing with 'print()'.
"""


def addin_button(button_action: str) -> str:
    """
    Returns a prompt template for building a custom C#
    ArcGIS Pro SDK Add-In button that implements a specific action.
    """
    return f"""You need to create a custom C# Add-In Button for ArcGIS Pro 3.x to execute this specific action:
"{button_action}"

Please write the complete, compilable C# class implementing this button. Make sure to adhere to these rules:
1. Extend the button class from 'ArcGIS.Desktop.Framework.Contracts.Button'.
2. Override the 'OnClick()' method. Since this is an async operation, make it 'protected override async void OnClick()'.
3. All synchronous ArcGIS Pro API interactions (accessing map, layers, selections, geodata) MUST run inside a 'QueuedTask.Run()' block to comply with ArcGIS Pro's threading model.
4. If executing a geoprocessing tool (like Buffer or Spatial Join), call it directly using 'await Geoprocessing.ExecuteToolAsync()' and do NOT wrap it in 'QueuedTask.Run()'.
5. Handle exceptions cleanly using a try-catch block and present descriptive error messages or write to debug output.
6. Provide the corresponding DAML (Config.daml) XML registration tag for this button under '<controls>'.
"""
