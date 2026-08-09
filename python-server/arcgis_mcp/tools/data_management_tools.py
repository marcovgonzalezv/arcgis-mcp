"""
Data management wrappers.

Essential geodatabase and schema management tools from the Data Management
toolbox. These cover the most common automation needs: field management,
projection, geometry repair, copy/delete operations and definition of new
feature classes.
"""

from mcp.server.fastmcp import Context

from .geoprocessing_tools import run_gp_tool


def calculate_field(
    in_table: str,
    field: str,
    expression: str,
    expression_type: str = "PYTHON3",
    code_block: str = "",
    field_type: str = "",
    ctx: Context = None,
) -> str:
    """
    Performs field calculations on feature classes or tables.
    expression_type: "PYTHON3", "ARCADE", "SQL", "VB".
    Example: expression="!POP! / !AREA_KM2!", expression_type="PYTHON3".
    code_block: optional Python/SQL function body for complex expressions.
    field_type: optional, when set the field is (re)created with this type.
    """
    params = [in_table, field, expression, expression_type]
    if code_block:
        params.append(code_block)
    if field_type:
        params.append(field_type)
    return run_gp_tool(
        "CalculateField_management", params, ctx, add_outputs_to_map=False
    )


def add_field(
    in_table: str,
    field_name: str,
    field_type: str,
    field_precision: int = 0,
    field_scale: int = 0,
    field_length: int = 50,
    field_alias: str = "",
    field_is_nullable: str = "NULLABLE",
    field_is_required: str = "NON_REQUIRED",
    field_domain: str = "",
    ctx: Context = None,
) -> str:
    """
    Adds a new field to a table or feature class.
    field_type: "TEXT", "LONG", "SHORT", "DOUBLE", "FLOAT", "DATE", "BLOB".
    """
    params = [
        in_table,
        field_name,
        field_type,
        field_precision if field_precision else None,
        field_scale if field_scale else None,
        field_length,
        field_alias,
        field_is_nullable,
        field_is_required,
        field_domain,
    ]
    return run_gp_tool("AddField_management", params, ctx, add_outputs_to_map=False)


def delete_field(in_table: str, fields, ctx: Context = None) -> str:
    """
    Deletes one or more fields from a table or feature class.
    fields: a single field name or a list of field names.
    """
    if isinstance(fields, str):
        fields = [fields]
    return run_gp_tool(
        "DeleteField_management", [in_table, fields], ctx, add_outputs_to_map=False
    )


def project(
    in_dataset: str,
    out_dataset: str,
    out_coor_system: str,
    transform_method: str = "",
    in_coor_system: str = "",
    preserve_shape: str = "NO_PRESERVE_SHAPE",
    max_deviation: str = "",
    vertical: str = "NO_VERTICAL",
    ctx: Context = None,
) -> str:
    """
    Projects spatial data from one coordinate system to another.
    out_coor_system: WKID, WKT, or path to a .prj file.
    """
    params = [in_dataset, out_dataset, out_coor_system]
    if transform_method:
        params.append(transform_method)
        params.append(in_coor_system)
        params.append(preserve_shape)
        if max_deviation:
            params.append(max_deviation)
            params.append(vertical)
    return run_gp_tool("Project_management", params, ctx, add_outputs_to_map=True)


def define_projection(in_dataset: str, coor_system: str, ctx: Context = None) -> str:
    """
    Defines the projection of a dataset without transforming its coordinates.
    """
    return run_gp_tool(
        "DefineProjection_management",
        [in_dataset, coor_system],
        ctx,
        add_outputs_to_map=False,
    )


def copy_features(in_features: str, out_feature_class: str, ctx: Context = None) -> str:
    """
    Copies features to a new feature class.
    """
    return run_gp_tool(
        "CopyFeatures_management",
        [in_features, out_feature_class],
        ctx,
        add_outputs_to_map=True,
    )


def copy_rows(in_rows: str, out_table: str, ctx: Context = None) -> str:
    """
    Copies the rows of a table, table view or feature class to a new table.
    """
    return run_gp_tool(
        "CopyRows_management", [in_rows, out_table], ctx, add_outputs_to_map=False
    )


def get_count(in_features: str, ctx: Context = None) -> str:
    """
    Returns the total number of rows for a feature class, table or layer.
    """
    return run_gp_tool(
        "GetCount_management", [in_features], ctx, add_outputs_to_map=False
    )


def delete(in_data: str, data_type: str = "", ctx: Context = None) -> str:
    """
    Permanently deletes a dataset.
    """
    params = [in_data]
    if data_type:
        params.append(data_type)
    return run_gp_tool(
        "Delete_management", params, ctx, allow_delete=True, add_outputs_to_map=False
    )


def rename(
    in_data: str, out_data: str, data_type: str = "", ctx: Context = None
) -> str:
    """
    Renames a dataset.
    """
    params = [in_data, out_data]
    if data_type:
        params.append(data_type)
    return run_gp_tool("Rename_management", params, ctx, add_outputs_to_map=False)


def create_feature_class(
    out_path: str,
    out_name: str,
    geometry_type: str = "POINT",
    template: str = "",
    has_m: str = "DISABLED",
    has_z: str = "DISABLED",
    spatial_reference: str = "",
    ctx: Context = None,
) -> str:
    """
    Creates an empty feature class in a geodatabase or folder.
    geometry_type: "POINT", "MULTIPOINT", "POLYLINE", "POLYGON".
    """
    params = [
        out_path,
        out_name,
        geometry_type,
        template,
        has_m,
        has_z,
        spatial_reference,
    ]
    return run_gp_tool(
        "CreateFeatureclass_management", params, ctx, add_outputs_to_map=False
    )


def create_table(out_path: str, out_name: str, ctx: Context = None) -> str:
    """
    Creates an empty table in a geodatabase or dBASE workspace.
    """
    return run_gp_tool(
        "CreateTable_management", [out_path, out_name], ctx, add_outputs_to_map=False
    )


def repair_geometry(
    in_features: str, delete_null: bool = False, ctx: Context = None
) -> str:
    """
    Repairs problematic geometry errors in a feature class.
    """
    return run_gp_tool(
        "RepairGeometry_management",
        [in_features, "DELETE_NULL" if delete_null else "KEEP_NULL"],
        ctx,
        add_outputs_to_map=False,
    )


def check_geometry(in_features: list, out_table: str, ctx: Context = None) -> str:
    """
    Produces a report of geometry problems in a feature class.
    """
    return run_gp_tool(
        "CheckGeometry_management",
        [in_features, out_table],
        ctx,
        add_outputs_to_map=False,
    )


def find_identical(
    in_dataset: str,
    out_dataset: str,
    fields: list,
    xy_tolerance: str = "",
    z_tolerance: str = "",
    output_record_option: str = "ALL",
    ctx: Context = None,
) -> str:
    """
    Reports records in a feature class or table that have identical values in
    a list of fields, and generates a table listing these records.
    """
    params = [in_dataset, out_dataset, fields]
    if xy_tolerance:
        params.append(xy_tolerance)
        if z_tolerance:
            params.append(z_tolerance)
            params.append(output_record_option)
    return run_gp_tool(
        "FindIdentical_management", params, ctx, add_outputs_to_map=False
    )


def make_feature_layer(
    in_features: str,
    out_layer: str,
    where_clause: str = "",
    ctx: Context = None,
) -> str:
    """
    Creates a feature layer from an input feature class or layer file.
    """
    params = [in_features, out_layer]
    if where_clause:
        params.append(where_clause)
    return run_gp_tool(
        "MakeFeatureLayer_management", params, ctx, add_outputs_to_map=False
    )


def make_table_view(
    in_table: str,
    out_view: str,
    where_clause: str = "",
    workspace: str = "",
    ctx: Context = None,
) -> str:
    """
    Creates a table view from an input table or feature class.
    """
    params = [in_table, out_view]
    if where_clause:
        params.append(where_clause)
    if workspace:
        params.append(workspace)
    return run_gp_tool(
        "MakeTableView_management", params, ctx, add_outputs_to_map=False
    )


def add_join(
    in_layer_or_view: str,
    in_field: str,
    join_table: str,
    join_field: str,
    join_type: str = "KEEP_ALL",
    ctx: Context = None,
) -> str:
    """
    Joins a table to a layer or table view based on a common field.
    """
    return run_gp_tool(
        "AddJoin_management",
        [in_layer_or_view, in_field, join_table, join_field, join_type],
        ctx,
        add_outputs_to_map=False,
    )


def remove_join(in_layer_or_view: str, join_name: str = "", ctx: Context = None) -> str:
    """
    Removes a join from a feature layer or table view.
    """
    params = [in_layer_or_view]
    if join_name:
        params.append(join_name)
    return run_gp_tool("RemoveJoin_management", params, ctx, add_outputs_to_map=False)


def create_file_gdb(out_folder_path: str, out_name: str, ctx: Context = None) -> str:
    """
    Creates a file geodatabase in the specified folder.
    """
    return run_gp_tool(
        "CreateFileGDB_management",
        [out_folder_path, out_name],
        ctx,
        add_outputs_to_map=False,
    )


def add_subtypes(
    in_table: str,
    field: str,
    subtype_code: int = 0,
    subtype_description: str = "",
    ctx: Context = None,
) -> str:
    """
    Adds a subtype to a subtype definition.
    """
    params = [in_table, field]
    if subtype_code:
        params.append(subtype_code)
        params.append(subtype_description)
    return run_gp_tool("AddSubtype_management", params, ctx, add_outputs_to_map=False)
