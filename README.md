# arcgis-mcp - Servidor MCP con Add-In para ArcGIS Pro

`arcgis-mcp` integra ArcGIS Pro 3.7 con clientes compatibles con Model Context Protocol (MCP). El proyecto combina un Add-In de ArcGIS Pro en C#, ejecutado dentro de ArcGIS Pro, con un servidor Python FastMCP que expone operaciones de ArcGIS Pro como herramientas MCP mediante un Named Pipe local de Windows.

El MCP incluye 63 herramientas, 52 comandos Add-In, 2 recursos MCP y 2 plantillas de prompts (ejemplos).

---

## Descripcion general

- **Add-In para ArcGIS Pro**: complemento C# cargado por ArcGIS Pro. Ejecuta llamadas al ArcGIS Pro SDK dentro del proceso de ArcGIS Pro y expone comandos mediante `\\.\pipe\ArcGisMcpBridge`.
- **Servidor MCP en Python**: servidor FastMCP que registra las herramientas, recursos y prompts publicos. Se comunica con el Add-In mediante el cliente local de Named Pipe.
- **Capa IPC**: transporte local por Named Pipe con mensajes JSON precedidos por longitud, respuestas estructuradas, timeouts, reintentos y metadatos explicitos de error.
- **Suite de validacion**: pruebas Python, linting, formato, compilacion del Add-In, revision de whitespace Git y escaneo de artefactos generados.

El servidor expone operaciones para proyectos, mapas, capas, selecciones, simbologia, layouts, geodatabases, metadatos de portal, feature services y geoprocesamiento.

---

## Requisitos

- Windows.
- ArcGIS Pro 3.7.
- ArcGIS Pro SDK for .NET instalado con los ensamblados locales del SDK de ArcGIS Pro.
- .NET 10 SDK.
- Python 3.10 o superior.
- Paquetes Python de `python-server/requirements.txt`.
- Paquetes de desarrollo de `python-server/requirements-dev.txt` para pruebas y validacion de release.

---

## Estructura del repositorio

```text
arcgis-mcp/
+- arcgis-addin/
|  +- ArcGisMcpAddin.sln
|  +- ArcGisMcpAddin/
|     +- Config.daml
|     +- Module1.cs
|     +- PipeServer.cs
|     +- CommandHandler.cs
|     +- Commands/
|     +- Images/
+- python-server/
|  +- arcgis_mcp_server.py
|  +- pipe_client.py
|  +- test_connection.py
|  +- tools/
|  +- resources/
|  +- prompts/
|  +- tests/
|  +- requirements.txt
|  +- requirements-dev.txt
+- docs/
|  +- setup-guide.md
|  +- release-checklist.md
+- scripts/
|  +- validate_release.ps1
+- install_addin.ps1
+- README.md
+- CONTRIBUTING.md
+- SECURITY.md
```

---

## Add-In para ArcGIS Pro

El Add-In inicia el servidor de pipe local cuando ArcGIS Pro carga el modulo. Los comandos se ejecutan dentro de ArcGIS Pro y pueden acceder al proyecto activo, mapa activo, capas, layouts, geodatabases, estado del portal y APIs de geoprocesamiento.

Archivos principales del Add-In:

- `arcgis-addin/ArcGisMcpAddin/Module1.cs`: inicia y detiene el servidor de pipe.
- `arcgis-addin/ArcGisMcpAddin/PipeServer.cs`: gestiona conexiones locales y framing de mensajes.
- `arcgis-addin/ArcGisMcpAddin/CommandHandler.cs`: enruta comandos JSON hacia los modulos de implementacion.
- `arcgis-addin/ArcGisMcpAddin/Commands/`: contiene grupos de comandos para proyecto, mapa, datos, layouts, simbologia, edicion, geodatabase, portal y geoprocesamiento.
- `arcgis-addin/ArcGisMcpAddin/Commands/CoreCommands.cs`: reporta version del Add-In, version MCP, nombres de comandos y capacidades de herramientas.

Los comandos internos del Add-In incluyen `health_check`, `get_capabilities`, `list_maps`, `list_layers`, `save_project`, `publish_web_layer`, `stage_service_definition`, `create_map_series` y `ping`. El comando `ping` es infraestructura IPC interna y no se expone como herramienta MCP publica.

---

## Servidor MCP en Python

El servidor Python registra la interfaz publica MCP y delega operaciones al Add-In cuando se requiere una llamada al ArcGIS Pro SDK dentro del proceso de ArcGIS Pro.

Archivos principales del servidor:

- `python-server/arcgis_mcp_server.py`: punto de entrada FastMCP y registro publico de herramientas, recursos y prompts.
- `python-server/pipe_client.py`: cliente Windows Named Pipe.
- `python-server/tools/`: wrappers de herramientas MCP agrupados por area funcional.
- `python-server/resources/`: recursos MCP con referencias de ArcPy y del SDK de Add-Ins.
- `python-server/prompts/`: plantillas MCP para desarrollo ArcPy y Add-In.
- `python-server/tests/test_operational_contracts.py`: pruebas contractuales para conteo de herramientas, cobertura de comandos Add-In, gates de release, documentacion publica e higiene del repositorio.

Las herramientas MCP publicas incluyen `spatial_join`, `stage_service_definition`, `run_gp_tool`, `search_arcgis_docs`, `query_feature_service`, `publish_web_layer`, `create_basic_layout`, `export_active_map`, `apply_graduated_symbology`, `save_layer_file` y `describe_dataset`.

---

## Configuracion MCP

Registra el servidor Python en un cliente compatible con MCP usando la ruta del script:

```json
{
  "mcpServers": {
    "arcgis-mcp": {
      "command": "python.exe",
      "args": [
        "C:/path/to/arcgis-mcp/python-server/arcgis_mcp_server.py"
      ]
    }
  }
}
```

Usa la ruta absoluta del ejecutable Python preferido si `python.exe` no esta disponible en `PATH`.

---

## Instalacion

Ejecuta PowerShell desde la raiz del repositorio:

```powershell
cd C:\path\to\arcgis-mcp
.\install_addin.ps1
```

Luego instala las dependencias Python:

```powershell
cd C:\path\to\arcgis-mcp\python-server
python -m pip install -r requirements.txt
```

Despues de instalar el Add-In, cierra y vuelve a abrir ArcGIS Pro para cargar la DLL actual.

---

## Ejecucion con ArcGIS Pro

1. Abre ArcGIS Pro 3.7.
2. Abre o crea un proyecto.
3. Confirma que `ArcGIS Pro MCP Server Bridge` aparece en el Add-In Manager.
4. Abre una vista de mapa.
5. Confirma que la pestana `ArcGIS MCP` esta disponible en la cinta.
6. Ejecuta la prueba de conexion:

```powershell
cd C:\path\to\arcgis-mcp\python-server
python test_connection.py
```

Resultado esperado:

```text
SUCCESS: Connected to ArcGIS Pro MCP Bridge.
```

---

## Validacion

Ejecuta la validacion completa de release desde la raiz del repositorio:

```powershell
.\scripts\validate_release.ps1
```

El script de release valida:

- Linting Python con Ruff.
- Formato Python con Ruff.
- Suites de Pytest y unittest.
- Compilacion de bytecode Python.
- Formato del Add-In.
- Compilacion del Add-In.
- Whitespace Git.
- Limpieza y escaneo de artefactos generados.

El workflow de GitHub Actions ejecuta las comprobaciones del lado Python que pueden correr sin una instalacion local del ArcGIS Pro SDK.

---

## Modelo de seguridad

El Add-In acepta comandos mediante un Named Pipe local y los ejecuta dentro de la sesion activa de ArcGIS Pro. Ejecuta ArcGIS Pro y el servidor MCP bajo el mismo contexto confiable de usuario Windows. Conecta solo clientes MCP confiables, porque las herramientas pueden inspeccionar, editar, exportar, publicar y geoprocesar datos GIS disponibles para el proyecto activo de ArcGIS Pro.

Consulta `SECURITY.md` para lineamientos operativos y reporte de vulnerabilidades.

---

## Licencia

Este proyecto se distribuye bajo la Licencia MIT. Consulta `LICENSE` para ver el texto completo.

---

## Checklist de publicacion

Antes de publicar:

1. Ejecuta `.\scripts\validate_release.ps1`.
2. Confirma que `README.md`, `docs/setup-guide.md` y `docs/release-checklist.md` coinciden con el contrato actual de herramientas.
3. Confirma que no hay artefactos generados.
4. Confirma que no se incluyen rutas personales locales ni datos privados de proyectos.
5. Confirma que `LICENSE` contiene la Licencia MIT.
6. Configura los metadatos de autor Git.
7. Configura el remoto GitHub.

El checklist detallado esta en `docs/release-checklist.md`.
