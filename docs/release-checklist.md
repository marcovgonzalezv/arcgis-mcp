# Checklist de publicacion

Usa esta lista antes de crear una version publica del repositorio.

## Codigo fuente

- El arbol no contiene `bin/`, `obj/`, `__pycache__/`, `.pytest_cache/`, `.vs/` ni paquetes `.esriAddinX` generados.
- No existen rutas locales, nombres de usuario, carpetas personales ni marcas de entorno de desarrollo en archivos publicos.
- `spatial_join` esta expuesto una sola vez como herramienta MCP.
- El contrato publico mantiene 63 herramientas MCP, 2 recursos MCP y 2 plantillas MCP.
- `stage_service_definition` esta expuesto para convertir `.sddraft` a `.sd` antes de publicar.
- El Add-In mantiene 52 comandos internos; `ping` es solo comando IPC interno.
- `CONTRIBUTING.md` y `SECURITY.md` estan actualizados.

## Validacion local

Ejecuta desde la raiz del repositorio:

```powershell
.\scripts\validate_release.ps1
```

O ejecuta las validaciones por separado:

```powershell
python -m pip install -r requirements-dev.txt
python -m ruff check . --no-cache
python -m ruff format . --check --no-cache
python -m pytest -q
python -m unittest discover -s tests -v
```

Ejecuta desde `arcgis-addin/`:

```powershell
dotnet build .\ArcGisMcpAddin.sln
```

Con ArcGIS Pro abierto y el Add-In cargado:

```powershell
python test_connection.py
```

## Publicacion GitHub

- Crear el repositorio Git local solo despues de limpiar artefactos generados.
- Confirmar que `.gitignore`, `.gitattributes` y `.editorconfig` estan incluidos.
- Elegir licencia antes de marcar el proyecto como open source.
- Confirmar `git diff --cached --check` antes del primer commit.
- Activar GitHub Actions y verificar que el workflow `Python checks` termine sin errores.
- Documentar en el primer release la version soportada de ArcGIS Pro, .NET SDK y Python.
