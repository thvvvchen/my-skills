"""Regression tests for the repository's Codex plugin validator."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import validate_plugin


class ValidatePluginManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        manifest_path = validate_plugin.PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
        self.manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    def validate_in_temporary_plugin(
        self,
        manifest: dict[str, object],
        *,
        create_skills: bool = True,
        files: tuple[str, ...] = (),
    ) -> list[str]:
        with tempfile.TemporaryDirectory() as temp_dir:
            plugin_root = Path(temp_dir)
            if create_skills:
                (plugin_root / "skills").mkdir()
            for relative_path in files:
                path = plugin_root / relative_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("{}\n", encoding="utf-8")

            failures: list[str] = []
            with patch.object(validate_plugin, "PLUGIN_ROOT", plugin_root):
                validate_plugin.validate_plugin_manifest(manifest, failures)
            return failures

    def test_rejects_unknown_top_level_hooks_field(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["hooks"] = "./hooks.json"

        failures = self.validate_in_temporary_plugin(manifest)

        self.assertTrue(any("`hooks`" in failure for failure in failures), failures)

    def test_rejects_unknown_author_field(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["author"]["company"] = "Example"

        failures = self.validate_in_temporary_plugin(manifest)

        self.assertTrue(any("author.company" in failure for failure in failures), failures)

    def test_rejects_unknown_interface_field(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["interface"]["subtitle"] = "Example"

        failures = self.validate_in_temporary_plugin(manifest)

        self.assertTrue(any("interface.subtitle" in failure for failure in failures), failures)

    def test_rejects_missing_apps_companion_file(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["apps"] = "./.app.json"

        failures = self.validate_in_temporary_plugin(manifest)

        self.assertTrue(any("apps" in failure and "does not exist" in failure for failure in failures), failures)

    def test_rejects_missing_mcp_companion_file(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["mcpServers"] = "./.mcp.json"

        failures = self.validate_in_temporary_plugin(manifest)

        self.assertTrue(any("mcpServers" in failure and "does not exist" in failure for failure in failures), failures)

    def test_rejects_skills_path_outside_plugin_root(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["skills"] = "../skills"

        failures = self.validate_in_temporary_plugin(manifest)

        self.assertTrue(any("skills" in failure for failure in failures), failures)

    def test_rejects_missing_skills_directory(self) -> None:
        manifest = copy.deepcopy(self.manifest)

        failures = self.validate_in_temporary_plugin(manifest, create_skills=False)

        self.assertTrue(any("skills" in failure and "does not exist" in failure for failure in failures), failures)

    def test_accepts_inline_mcp_servers_object(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["mcpServers"] = {"example": {"type": "http", "url": "https://example.com/mcp"}}

        failures = self.validate_in_temporary_plugin(manifest)

        self.assertEqual([], failures)

    def test_accepts_default_prompt_alias(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        prompts = manifest["interface"].pop("defaultPrompt")
        manifest["interface"]["default_prompt"] = prompts

        failures = self.validate_in_temporary_plugin(manifest)

        self.assertEqual([], failures)

    def test_rejects_invalid_mcp_servers_type(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["mcpServers"] = ["./.mcp.json"]

        failures = self.validate_in_temporary_plugin(manifest)

        self.assertTrue(any("mcpServers" in failure and "string or object" in failure for failure in failures), failures)

    def test_accepts_existing_apps_and_mcp_companion_files(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["apps"] = "./.app.json"
        manifest["mcpServers"] = "./.mcp.json"

        failures = self.validate_in_temporary_plugin(
            manifest,
            files=(".app.json", ".mcp.json"),
        )

        self.assertEqual([], failures)

    def test_current_manifest_is_valid(self) -> None:
        failures: list[str] = []

        validate_plugin.validate_plugin_manifest(self.manifest, failures)

        self.assertEqual([], failures)


if __name__ == "__main__":
    unittest.main()
