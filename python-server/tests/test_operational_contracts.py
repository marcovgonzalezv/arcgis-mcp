import io
import ast
import importlib
import pathlib
import re
import sys
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTHON_SERVER = PROJECT_ROOT / "python-server"

sys.path.insert(0, str(PYTHON_SERVER))

test_connection = importlib.import_module("test_connection")


class FailingClient:
    def send_command(self, command, timeout_ms=5000):
        raise TimeoutError("pipe unavailable")


class AccessDeniedClient:
    def send_command(self, command, timeout_ms=5000):
        raise OSError(
            "Windows IPC error communicating with ArcGIS Pro: Acceso denegado. (Code 5)"
        )


class OperationalContractsTest(unittest.TestCase):
    def test_mcp_tool_registry_matches_public_contract(self):
        server = PYTHON_SERVER / "arcgis_mcp_server.py"
        tree = ast.parse(server.read_text(encoding="utf-8"))

        tools = []
        resources = []
        prompts = []
        for node in tree.body:
            if not isinstance(node, ast.FunctionDef):
                continue
            decorators = [ast.unparse(item) for item in node.decorator_list]
            if any(item.startswith("mcp.tool") for item in decorators):
                tools.append(node.name)
            if any(item.startswith("mcp.resource") for item in decorators):
                resources.append(node.name)
            if any(item.startswith("mcp.prompt") for item in decorators):
                prompts.append(node.name)

        self.assertEqual(63, len(tools))
        self.assertEqual(2, len(resources))
        self.assertEqual(2, len(prompts))
        self.assertIn("spatial_join", tools)

    def test_addin_command_registry_matches_handler_cases(self):
        core = (
            PROJECT_ROOT
            / "arcgis-addin"
            / "ArcGisMcpAddin"
            / "Commands"
            / "CoreCommands.cs"
        ).read_text(encoding="utf-8")
        handler = (
            PROJECT_ROOT / "arcgis-addin" / "ArcGisMcpAddin" / "CommandHandler.cs"
        ).read_text(encoding="utf-8")

        command_block = re.search(
            r"CommandNames\s*\{.*?new List<string>\s*\{(?P<body>.*?)\};",
            core,
            re.S,
        )
        tool_block = re.search(
            r"ToolNames\s*\{.*?Concat\(new\[\]\s*\{(?P<body>.*?)\}\)",
            core,
            re.S,
        )
        self.assertIsNotNone(command_block)
        self.assertIsNotNone(tool_block)

        addin_commands = set(re.findall(r'"([a-z_]+)"', command_block.group("body")))
        python_wrappers = set(re.findall(r'"([a-z_]+)"', tool_block.group("body")))
        handler_cases = set(re.findall(r'case "([a-z_]+)":', handler))
        public_tools = (addin_commands - {"ping"}) | python_wrappers

        self.assertEqual(52, len(addin_commands))
        self.assertEqual(addin_commands, handler_cases)
        self.assertIn("ping", addin_commands)
        self.assertIn("spatial_join", python_wrappers)
        self.assertNotIn("spatial_join", addin_commands)
        self.assertIn("stage_service_definition", addin_commands)
        self.assertEqual(63, len(public_tools))

    def test_public_files_do_not_contain_local_paths_or_ai_branding(self):
        blocked_terms = [
            "C:" + "\\" + "Users" + "\\" + "mar" + "co",
            "One" + "Drive",
            "Docu" + "mentos",
            "Co" + "dex",
            "2026" + "-05" + "-30",
            "Chat" + "GPT",
            "Clau" + "de",
            "Co" + "pilot",
            "Anti" + "gravity",
            "inteligencia " + "artificial",
            "artificial " + "intelligence",
            "ai " + "agents",
            "ai " + "assistants",
        ]
        blocked = re.compile(
            "|".join(re.escape(term) for term in blocked_terms),
            re.IGNORECASE,
        )
        checked_suffixes = {
            ".cs",
            ".csproj",
            ".daml",
            ".md",
            ".py",
            ".ps1",
            ".json",
            ".ini",
        }
        offenders = []
        for path in PROJECT_ROOT.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in checked_suffixes:
                continue
            if any(
                part in {"bin", "obj", "__pycache__", ".git"} for part in path.parts
            ):
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if blocked.search(text):
                offenders.append(str(path.relative_to(PROJECT_ROOT)))

        self.assertEqual([], offenders)

    def test_github_actions_uses_development_requirements(self):
        workflow = (PROJECT_ROOT / ".github" / "workflows" / "python-ci.yml").read_text(
            encoding="utf-8"
        )
        dev_requirements = (PYTHON_SERVER / "requirements-dev.txt").read_text(
            encoding="utf-8"
        )

        self.assertIn("requirements-dev.txt", workflow)
        self.assertIn("python -m pytest -q", workflow)
        self.assertIn("python -m unittest discover -s tests -v", workflow)
        self.assertIn("git diff --check", workflow)
        self.assertIn("-r requirements.txt", dev_requirements)
        self.assertIn("pytest", dev_requirements)
        self.assertIn("ruff", dev_requirements)

    def test_public_docs_match_tool_and_command_counts(self):
        docs = "\n".join(
            [
                (PROJECT_ROOT / "README.md").read_text(encoding="utf-8"),
                (PROJECT_ROOT / "docs" / "release-checklist.md").read_text(
                    encoding="utf-8"
                ),
            ]
        )

        self.assertNotIn("62 herramientas", docs)
        self.assertNotIn("51 comandos", docs)
        self.assertIn("63 herramientas MCP", docs)
        self.assertIn("52 comandos", docs)

    def test_release_script_runs_core_validation_steps(self):
        source = (PROJECT_ROOT / "scripts" / "validate_release.ps1").read_text(
            encoding="utf-8"
        )

        required_snippets = [
            'Invoke-Native "python" @("-m", "ruff", "check", ".", "--no-cache")',
            'Invoke-Native "python" @("-m", "ruff", "format", ".", "--check", "--no-cache")',
            'Invoke-Native "python" @("-m", "pytest", "-q")',
            'Invoke-Native "python" @("-m", "unittest", "discover", "-s", "tests", "-v")',
            'Invoke-Native "python" @("-m", "compileall", "-q", $PythonServer)',
            'Invoke-Native "dotnet" @("format", $SolutionFile, "--verify-no-changes"',
            'Invoke-Native "dotnet" @("build", $SolutionFile)',
            'Invoke-Native "git" @("diff", "--check")',
            'Invoke-Native "git" @("diff", "--cached", "--check")',
            "Generated artifact scan",
        ]

        for snippet in required_snippets:
            self.assertIn(snippet, source)

    def test_python_modules_do_not_keep_unused_imports(self):
        allowed_reexport_modules = {
            PYTHON_SERVER / "tools" / "__init__.py",
            PYTHON_SERVER / "prompts" / "__init__.py",
            PYTHON_SERVER / "resources" / "__init__.py",
        }
        offenders = []

        for path in PYTHON_SERVER.rglob("*.py"):
            if path in allowed_reexport_modules:
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            imports = {}
            used_names = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports[alias.asname or alias.name.split(".")[0]] = node.lineno
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        if alias.name != "*":
                            imports[alias.asname or alias.name] = node.lineno
                elif isinstance(node, ast.Name):
                    used_names.add(node.id)

            for name, line in imports.items():
                if name not in used_names:
                    rel_path = path.relative_to(PROJECT_ROOT)
                    offenders.append(f"{rel_path}:{line}:{name}")

        self.assertEqual([], sorted(offenders))

    def test_timeout_report_is_cp1252_safe(self):
        buffer = io.BytesIO()
        stream = io.TextIOWrapper(buffer, encoding="cp1252", errors="strict")

        try:
            with patch.object(
                test_connection, "ArcGisPipeClient", return_value=FailingClient()
            ):
                with redirect_stdout(stream):
                    self.assertFalse(test_connection.test_connection())
            stream.flush()
        finally:
            stream.detach()

    def test_access_denied_report_explains_permission_mismatch(self):
        stream = io.StringIO()

        with patch.object(
            test_connection, "ArcGisPipeClient", return_value=AccessDeniedClient()
        ):
            with redirect_stdout(stream):
                self.assertFalse(test_connection.test_connection())

        output = stream.getvalue()
        self.assertIn("Access denied troubleshooting", output)
        self.assertIn("same permission level", output)

    def test_python_client_keeps_named_pipe_in_byte_mode(self):
        source = (PYTHON_SERVER / "pipe_client.py").read_text(encoding="utf-8")

        self.assertNotIn("PIPE_READMODE_MESSAGE", source)

    def test_pipe_server_does_not_query_unsupported_length(self):
        source = (
            PROJECT_ROOT / "arcgis-addin" / "ArcGisMcpAddin" / "PipeServer.cs"
        ).read_text(encoding="utf-8")

        self.assertNotIn("pipeStream.Length", source)
        self.assertIn("ReadExactlyAsync", source)

    def test_addin_does_not_use_silent_catches(self):
        offenders = []
        for path in (PROJECT_ROOT / "arcgis-addin").rglob("*.cs"):
            source = path.read_text(encoding="utf-8")
            if re.search(r"catch\s*\{\s*\}", source):
                offenders.append(str(path.relative_to(PROJECT_ROOT)))

        self.assertEqual([], offenders)

    def test_python_client_does_not_silence_cleanup_errors(self):
        source = (PYTHON_SERVER / "pipe_client.py").read_text(encoding="utf-8")

        self.assertNotRegex(source, r"except\s*:")
        self.assertNotRegex(source, r"except\s+Exception\s*:\s*pass")
        self.assertIn("warnings.warn", source)

    def test_map_status_does_not_emit_non_finite_json_numbers(self):
        source = (
            PROJECT_ROOT
            / "arcgis-addin"
            / "ArcGisMcpAddin"
            / "Commands"
            / "MapCommands.cs"
        ).read_text(encoding="utf-8")

        self.assertIn("SafeDouble", source)
        self.assertIn("double.IsFinite", source)
        self.assertNotIn("x = activeView.Camera.X", source)

    def test_addin_project_targets_local_arcgis_sdk_layout(self):
        project = (
            PROJECT_ROOT / "arcgis-addin" / "ArcGisMcpAddin" / "ArcGisMcpAddin.csproj"
        )
        source = project.read_text(encoding="utf-8")

        self.assertIn("<TargetFramework>net10.0-windows</TargetFramework>", source)
        self.assertIn(r"bin\Extensions\Core\ArcGIS.Desktop.Core.dll", source)
        self.assertIn(r"bin\Extensions\Mapping\ArcGIS.Desktop.Mapping.dll", source)
        self.assertIn(
            r"bin\Extensions\Geoprocessing\ArcGIS.Desktop.GeoProcessing.dll",
            source,
        )
        self.assertIn(r"bin\Extensions\Layout\ArcGIS.Desktop.Layouts.dll", source)

    def test_addin_manifest_version_matches_reported_version(self):
        core = (
            PROJECT_ROOT
            / "arcgis-addin"
            / "ArcGisMcpAddin"
            / "Commands"
            / "CoreCommands.cs"
        ).read_text(encoding="utf-8")
        daml = (
            PROJECT_ROOT / "arcgis-addin" / "ArcGisMcpAddin" / "Config.daml"
        ).read_text(encoding="utf-8")

        addin_version = re.search(r'AddinVersion = "([^"]+)"', core)
        manifest_version = re.search(r'version="([^"]+)"', daml)

        self.assertIsNotNone(addin_version)
        self.assertIsNotNone(manifest_version)
        self.assertEqual(addin_version.group(1), manifest_version.group(1))

    def test_installer_uses_runtime_specific_build_output(self):
        source = (PROJECT_ROOT / "install_addin.ps1").read_text(encoding="utf-8")

        self.assertIn(r"ArcGisMcpAddin\bin\Debug\win-x64", source)
        self.assertIn("Build output directory was not found", source)
        self.assertIn("BuildPackagePath", source)
        self.assertIn("MSBuild Add-In package was not found", source)
        self.assertIn("ArcGisMcpAddin.esriAddinX", source)
        self.assertNotIn("Compress-Archive", source)
        self.assertIn("FallbackDocumentsFolder", source)


if __name__ == "__main__":
    unittest.main()
