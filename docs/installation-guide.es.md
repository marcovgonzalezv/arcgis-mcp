# Guia de instalacion paso a paso

Esta guia explica como instalar `arcgis-mcp` desde cero. Esta dividida en dos recorridos:

- **Recorrido A (usuarios no tecnicos):** instalacion automatica con un solo comando.
- **Recorrido B (usuarios tecnicos):** compilacion manual, entorno de desarrollo, registro del servidor MCP y pruebas.

Elige un recorrido y sigue los pasos en orden.

> Esta guia tambien esta disponible en ingles: `installation-guide.md`.

---

## Camino rapido: distribucion por release (todos los usuarios)

Si descargaste los artefactos del release (`ArcGisMcpAddin.esriAddinX`, el `arcgis_mcp_server-*.whl` y `setup.ps1`), coloca los tres archivos en la misma carpeta y ejecuta:

```powershell
.\setup.ps1
```

`setup.ps1` localiza Python (el conda de ArcGIS Pro o el del sistema), crea un entorno virtual aislado, instala la wheel, registra el Add-In en ArcGIS Pro e imprime la configuracion lista para pegar en tu cliente MCP. No requiere toolchain de compilacion.

Al terminar: abre ArcGIS Pro 3.7, confirma la pestana **ArcGIS MCP** y reinicia tu cliente MCP. Los recorridos siguientes solo se necesitan cuando se compila desde el codigo fuente.

---

## Que hace este proyecto

`arcgis-mcp` conecta ArcGIS Pro 3.7 con un cliente compatible con Model Context Protocol (MCP). Un cliente MCP es un programa que puede llamar a las herramientas de ArcGIS Pro (abrir mapas, contar entidades, exportar layouts, ejecutar geoprocesamiento, etc.) a traves de un puente local seguro.

El sistema tiene tres partes:

1. **Add-In de ArcGIS Pro (C#):** complemento que se carga dentro de ArcGIS Pro y abre un canal de comunicacion local (Named Pipe).
2. **Servidor MCP (Python):** expone las herramientas publicas y conversa con el Add-In.
3. **Cliente MCP:** tu programa o asistente que consume las herramientas.

---

## Requisitos comunes (ambos recorridos)

Antes de empezar necesitas lo siguiente instalado en Windows:

| Requisito | Version | Como verificar |
|---|---|---|
| Windows 10 u 11 (64 bits) | - | Configuracion > Sistema > Acerca de |
| ArcGIS Pro | 3.7 | Ayuda > Acerca de ArcGIS Pro |
| .NET SDK | 10 | `dotnet --version` en PowerShell |
| Python | 3.10 o superior | `python --version` en PowerShell |
| Git (opcional, para clonar) | cualquiera | `git --version` |

Ademas necesitas:

- El codigo del proyecto `arcgis-mcp` descargado en una carpeta, por ejemplo `C:\ruta\a\arcgis-mcp`.
- Un cliente MCP compatible donde quieras usar las herramientas.

> Importante: ArcGIS Pro debe estar cerrado durante la instalacion del Add-In. Se abre despues, al final.

---

## Recorrido A: Instalacion automatica (usuarios no tecnicos)

Este recorrido usa el instalador automatico. Solo necesitas ejecutar un comando y seguir las indicaciones de ArcGIS Pro.

### Paso A1. Abre PowerShell

1. Pulsa la tecla `Windows`.
2. Escribe `PowerShell`.
3. Haz clic en **Windows PowerShell** (no hace falta administrador, salvo que ArcGIS Pro se ejecute como administrador).

### Paso A2. Ve a la carpeta del proyecto

En la ventana de PowerShell escribe `cd` seguido de la ruta de la carpeta y pulsa Enter:

```powershell
cd C:\ruta\a\arcgis-mcp
```

Sustituye `C:\ruta\a\arcgis-mcp` por la ruta real donde descargaste el proyecto.

### Paso A3. Ejecuta el instalador

Ejecuta este comando y pulsa Enter:

```powershell
.\install_addin.ps1
```

El instalador hace tres cosas de forma automatica:

1. Verifica que .NET SDK esta instalado.
2. Compila el Add-In y genera el paquete `ArcGisMcpAddin.esriAddinX`.
3. Copia el paquete a la carpeta de Add-Ins de ArcGIS Pro.

Si todo va bien veras el mensaje:

```text
SUCCESS: Add-In successfully installed!
```

### Paso A4. Instala las dependencias de Python

En la misma ventana de PowerShell, cambia a la carpeta del servidor e instala los paquetes:

```powershell
cd C:\ruta\a\arcgis-mcp\python-server
python -m pip install -r requirements.txt
```

Espera a que termine la instalacion.

### Paso A5. Abre ArcGIS Pro y verifica

1. Abre ArcGIS Pro.
2. Abre o crea un proyecto con al menos un mapa.
3. Ve a **Settings > Add-In Manager**.
4. Confirma que aparece **ArcGIS Pro MCP Server Bridge** en la lista. El autor es Marco Gonzalez Valdiviezo.
5. Abre una vista de mapa.
6. En la cinta superior debe aparecer la pestana **ArcGIS MCP**.
7. Pulsa el boton **Show MCP Status**. Debe indicar que el servidor esta activo.

### Paso A6. Prueba la conexion

Con ArcGIS Pro abierto y un mapa visible, ejecuta en PowerShell:

```powershell
cd C:\ruta\a\arcgis-mcp\python-server
python test_connection.py
```

Resultado esperado:

```text
SUCCESS: Connected to ArcGIS Pro MCP Bridge.
```

Si ves ese mensaje, la instalacion termino. Puedes saltar a la seccion [Registrar el servidor MCP en tu cliente](#registrar-el-servidor-mcp-en-tu-cliente).

---

## Recorrido B: Instalacion tecnica (desarrolladores)

Este recorrido cubre la compilacion manual, la preparacion del entorno de desarrollo, la configuracion del cliente MCP y la ejecucion de las pruebas.

### Paso B1. Verifica las herramientas de desarrollo

Abre PowerShell y confirma las versiones:

```powershell
dotnet --version
python --version
git --version
```

Debe haber .NET 10 SDK, Python 3.10+ y Git. Para compilar el Add-In tambien se necesitan los ensamblados del ArcGIS Pro SDK, referenciados localmente desde `C:\Program Files\ArcGIS\Pro\bin\`.

### Paso B2. (Opcional) Clona el repositorio

Si partiste de Git:

```powershell
cd C:\proyectos
git clone <url-del-repositorio> arcgis-mcp
cd arcgis-mcp
```

Si ya tienes la carpeta del proyecto, omite este paso.

### Paso B3. Crea y activa un entorno virtual de Python

Se recomienda un entorno aislado. Sustituye la ruta por la que prefieras:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Si prefieres conda:

```powershell
conda create -n gis python=3.13
conda activate gis
```

### Paso B4. Instala las dependencias de desarrollo

Estas incluyen las de runtime mas las de prueba (pytest, ruff):

```powershell
cd C:\ruta\a\arcgis-mcp\python-server
python -m pip install -r requirements-dev.txt
```

### Paso B5. Compila el Add-In manualmente

```powershell
cd C:\ruta\a\arcgis-mcp\arcgis-addin
dotnet build .\ArcGisMcpAddin.sln --configuration Debug
```

Salida esperada: `0 Errores`. El paquete se genera en:

```text
arcgis-addin\ArcGisMcpAddin\bin\Debug\win-x64\ArcGisMcpAddin.esriAddinX
```

### Paso B6. Despliega el Add-In

Puedes usar el instalador (`.\install_addin.ps1` desde la raiz del proyecto) o copiar el paquete a mano a:

```text
%USERPROFILE%\Documents\ArcGIS\AddIns\ArcGISPro\ArcGisMcpAddin.esriAddinX
```

Despues cierra y vuelve a abrir ArcGIS Pro para que cargue la nueva DLL.

### Paso B7. Verifica la carga del Add-In

1. Abre ArcGIS Pro 3.7.
2. Abre un proyecto con un mapa.
3. Ve a **Settings > Add-In Manager** y confirma que **ArcGIS Pro MCP Server Bridge** esta listado.
4. Abre la vista de mapa y localiza la pestana **ArcGIS MCP** en la cinta.
5. Pulsa **Show MCP Status** para confirmar que el Named Pipe `\\.\pipe\ArcGisMcpBridge` esta activo.

### Paso B8. Ejecuta la prueba de conexion

```powershell
cd C:\ruta\a\arcgis-mcp\python-server
python test_connection.py
```

Salida esperada:

```text
SUCCESS: Connected to ArcGIS Pro MCP Bridge.
```

### Paso B9. Ejecuta la suite de validacion

Para confirmar que el codigo cumple todos los contratos (linting, formato, pruebas, compilacion):

```powershell
cd C:\ruta\a\arcgis-mcp
.\scripts\validate_release.ps1
```

Ejecuta los controles de Python por separado si lo prefieres:

```powershell
cd C:\ruta\a\arcgis-mcp\python-server
python -m ruff check . --no-cache
python -m ruff format . --check --no-cache
python -m pytest -q
python -m unittest discover -s tests -v
```

### Paso B10. Registrar el servidor MCP en tu cliente

Edita el archivo de configuracion de tu cliente MCP y agrega el servidor (invocacion desde fuente):

```json
{
  "mcpServers": {
    "arcgis-mcp": {
      "command": "python.exe",
      "args": ["-m", "arcgis_mcp"]
    }
  }
}
```

Si `python.exe` no esta en `PATH`, usa la ruta absoluta del ejecutable (por ejemplo, la del entorno virtual). Reinicia el cliente MCP despues de guardar la configuracion.

---

## Registrar el servidor MCP en tu cliente

Esta seccion aplica a ambos recorridos una vez instalado todo.

El servidor MCP se ejecuta con `python -m arcgis_mcp`, o como el comando `arcgis-mcp-server` tras `pip install`. Registralo en tu cliente MCP con la configuracion anterior. Ejemplos de clientes compatibles: aplicaciones de escritorio con soporte MCP, editores de codigo con extension MCP, o cualquier cliente que implemente el protocolo.

Recomendaciones:

- Usa siempre la ruta absoluta del script y del ejecutable Python.
- Si usas un entorno virtual o conda, apunta a su `python.exe` para que encuentre `mcp`, `pywin32` y `pydantic`.
- ArcGIS Pro debe estar abierto y con el Add-In cargado para que las herramientas que necesitan el puente funcionen.

---

## Solucion de problemas

### El Add-In no aparece en ArcGIS Pro

- Cierra ArcGIS Pro por completo y vuelve a abrirlo.
- Verifica que el archivo `ArcGisMcpAddin.esriAddinX` esta en `%USERPROFILE%\Documents\ArcGIS\AddIns\ArcGISPro\`.
- Ejecuta `.\install_addin.ps1` de nuevo desde la raiz del proyecto.

### Error: "dotnet CLI was not found"

Falta el .NET 10 SDK. Descargalo e instalalo desde el sitio oficial de .NET. Cierra y vuelve a abrir PowerShell despues de instalar.

### Error de compilacion del Add-In

- Confirma que ArcGIS Pro 3.7 esta instalado en `C:\Program Files\ArcGIS\Pro`.
- Verifica que existen las DLLs en `C:\Program Files\ArcGIS\Pro\bin` y el archivo `Esri.ProApp.SDK.Desktop.targets`.
- Ejecuta `dotnet build` desde la carpeta `arcgis-addin` y revisa los mensajes de error.

### `python test_connection.py` da CONNECTION TIMEOUT

- Confirma que ArcGIS Pro esta abierto y con un mapa activo.
- Confirma que la pestana **ArcGIS MCP** esta visible en la cinta.
- Si ArcGIS Pro se ejecuta como administrador, ejecuta la prueba como administrador tambien.

### `python test_connection.py` da "Acceso denegado" (Code 5)

El cliente y ArcGIS Pro tienen niveles de permiso distintos. Soluciones:

1. Cierra ArcGIS Pro y vuelve a abrirlo de forma normal (sin administrador).
2. Ejecuta la prueba de conexion sin administrador.
3. Si necesitas administrador en ArcGIS Pro, ejecuta tambien el cliente MCP como administrador.

### Error: No module named 'mcp' (o 'pywin32' o 'pydantic')

Las dependencias de Python no estan instaladas en el entorno activo:

```powershell
cd C:\ruta\a\arcgis-mcp\python-server
python -m pip install -r requirements.txt
```

Si usas un entorno virtual o conda, activalo antes de instalar.

### El cliente MCP no encuentra las herramientas

- Verifica que la ruta del script en la configuracion es absoluta y correcta.
- Confirma que apuntas al `python.exe` del entorno donde instalaste las dependencias.
- Reinicia el cliente MCP despues de cambiar la configuracion.

---

## Modelo de seguridad

- El Add-In acepta comandos por un Named Pipe local y los ejecuta dentro de la sesion activa de ArcGIS Pro.
- Ejecuta ArcGIS Pro y el cliente MCP bajo el mismo usuario de Windows.
- Conecta solo clientes MCP de confianza: las herramientas pueden inspeccionar, editar, exportar, publicar y geoprocesar datos del proyecto activo.
- Consulta `SECURITY.md` para mas detalles.

---

## Resumen rapido

| Paso | Recorrido A | Recorrido B |
|---|---|---|
| Abrir PowerShell | A1 | B1 |
| Compilar Add-In | A3 (automatico) | B5 (manual) |
| Instalar paquetes Python | A4 | B4 |
| Cargar Add-In en ArcGIS Pro | A5 | B7 |
| Probar conexion | A6 | B8 |
| Registrar cliente MCP | final | B10 |
| Validacion completa | opcional | B9 |
