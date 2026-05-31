# Guia de instalacion y configuracion

Esta guia describe como compilar, instalar, configurar y probar `arcgis-mcp` con ArcGIS Pro 3.7.

## Requisitos

1. ArcGIS Pro 3.7 instalado y con licencia activa.
2. .NET 10 SDK.
3. Python 3.10 o superior.
4. Paquetes de `python-server/requirements.txt`.

## Compilar e instalar el Add-In

Ejecuta PowerShell en la raiz del proyecto:

```powershell
cd C:\path\to\arcgis-mcp
.\install_addin.ps1
```

El instalador:

- Compila `arcgis-addin/ArcGisMcpAddin.sln`.
- Genera `ArcGisMcpAddin.esriAddinX`.
- Copia el paquete en la carpeta de Add-Ins de ArcGIS Pro.

Despues de instalar, cierra y vuelve a abrir ArcGIS Pro para cargar la version actual del Add-In.

## Instalar dependencias Python

```powershell
cd C:\path\to\arcgis-mcp\python-server
pip install -r requirements.txt
```

Puedes usar el Python de ArcGIS Pro o un entorno virtual propio con `mcp` y `pywin32`.

Para ejecutar pruebas y controles de estilo:

```powershell
pip install -r requirements-dev.txt
```

## Verificar el Add-In

1. Abre ArcGIS Pro 3.7.
2. Abre o crea un proyecto con al menos un mapa.
3. Ve a `Settings > Add-In Manager`.
4. Verifica que aparezca `ArcGIS Pro MCP Server Bridge`.
5. Abre una vista de mapa.
6. En la cinta superior debe aparecer la pestana `ArcGIS MCP`.
7. Usa `Show MCP Status` para confirmar que el Named Pipe `\\.\pipe\ArcGisMcpBridge` esta activo.

## Probar la conexion

Con ArcGIS Pro abierto:

```powershell
cd C:\path\to\arcgis-mcp\python-server
python test_connection.py
```

Salida esperada:

```text
SUCCESS: Connected to ArcGIS Pro MCP Bridge.
```

## Registrar el servidor MCP

Agrega el servidor en la configuracion de tu cliente MCP:

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

Si `python.exe` no esta en `PATH`, usa la ruta absoluta del ejecutable.

## Pruebas locales

```powershell
cd C:\path\to\arcgis-mcp\python-server
python -m ruff check . --no-cache
python -m ruff format . --check --no-cache
python -m pytest -q
python -m unittest discover -s tests -v
```

```powershell
cd C:\path\to\arcgis-mcp\arcgis-addin
dotnet build .\ArcGisMcpAddin.sln
```
