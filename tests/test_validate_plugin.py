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
        files: dict[str, str] | None = None,
    ) -> list[str]:
        with tempfile.TemporaryDirectory() as temp_dir:
            plugin_root = Path(temp_dir)
            if create_skills:
                (plugin_root / "skills").mkdir()
            for relative_path, contents in (files or {}).items():
                path = plugin_root / relative_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(contents, encoding="utf-8")

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

    def test_rejects_missing_skills_field(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest.pop("skills")

        failures = self.validate_in_temporary_plugin(manifest)

        self.assertTrue(any("skills" in failure and "required" in failure for failure in failures), failures)

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
            files={
                ".app.json": json.dumps({"apps": {"example": {"id": "example"}}}),
                ".mcp.json": json.dumps({"mcpServers": {"example": {"type": "http"}}}),
            },
        )

        self.assertEqual([], failures)

    def test_rejects_missing_interface_asset_files(self) -> None:
        for field in ("composerIcon", "logo", "logoDark"):
            with self.subTest(field=field):
                manifest = copy.deepcopy(self.manifest)
                manifest["interface"][field] = f"./assets/{field}.png"

                failures = self.validate_in_temporary_plugin(manifest)

                self.assertTrue(any(field in failure and "missing" in failure for failure in failures), failures)

    def test_rejects_non_array_screenshots(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["interface"]["screenshots"] = "./assets/screenshot.png"

        failures = self.validate_in_temporary_plugin(manifest)

        self.assertTrue(any("screenshots" in failure and "array" in failure for failure in failures), failures)

    def test_rejects_missing_screenshot_file(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["interface"]["screenshots"] = ["./assets/screenshot.png"]

        failures = self.validate_in_temporary_plugin(manifest)

        self.assertTrue(any("screenshots[0]" in failure and "missing" in failure for failure in failures), failures)

    def test_accepts_existing_interface_assets(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["interface"].update(
            {
                "composerIcon": "./assets/composer.png",
                "logo": "./assets/logo.png",
                "logoDark": "./assets/logo-dark.png",
                "screenshots": ["./assets/screenshot.png"],
            }
        )

        failures = self.validate_in_temporary_plugin(
            manifest,
            files={
                "assets/composer.png": "image",
                "assets/logo.png": "image",
                "assets/logo-dark.png": "image",
                "assets/screenshot.png": "image",
            },
        )

        self.assertEqual([], failures)

    def test_rejects_invalid_app_manifests(self) -> None:
        cases = {
            "invalid JSON": ("{", "valid JSON"),
            "non-object root": ("[]", "JSON object"),
            "unknown field": (json.dumps({"apps": {}, "extra": True}), "extra"),
            "missing apps": ("{}", "apps"),
            "non-object apps": (json.dumps({"apps": []}), "must be an object"),
            "non-object app": (json.dumps({"apps": {"example": []}}), "example"),
            "missing app id": (json.dumps({"apps": {"example": {}}}), "id"),
            "empty category": (
                json.dumps({"apps": {"example": {"id": "example", "category": ""}}}),
                "category",
            ),
        }
        for label, (contents, fragment) in cases.items():
            with self.subTest(label=label):
                manifest = copy.deepcopy(self.manifest)
                manifest["apps"] = "./.app.json"

                failures = self.validate_in_temporary_plugin(
                    manifest,
                    files={".app.json": contents},
                )

                self.assertTrue(any(fragment in failure for failure in failures), failures)

    def test_rejects_invalid_mcp_companion_manifests(self) -> None:
        cases = {
            "invalid JSON": ("{", "valid JSON"),
            "non-object root": ("[]", "JSON object"),
            "unknown field": (json.dumps({"mcpServers": {}, "extra": True}), "extra"),
            "missing servers": ("{}", "mcpServers"),
            "non-object servers": (json.dumps({"mcpServers": []}), "must be an object"),
            "empty server name": (json.dumps({"mcpServers": {"": {}}}), "non-empty"),
            "non-object server": (json.dumps({"mcpServers": {"example": []}}), "example"),
        }
        for label, (contents, fragment) in cases.items():
            with self.subTest(label=label):
                manifest = copy.deepcopy(self.manifest)
                manifest["mcpServers"] = "./.mcp.json"

                failures = self.validate_in_temporary_plugin(
                    manifest,
                    files={".mcp.json": contents},
                )

                self.assertTrue(any(fragment in failure for failure in failures), failures)

    def test_rejects_invalid_inline_mcp_servers(self) -> None:
        for servers in ({"": {}}, {"example": []}):
            with self.subTest(servers=servers):
                manifest = copy.deepcopy(self.manifest)
                manifest["mcpServers"] = servers

                failures = self.validate_in_temporary_plugin(manifest)

                self.assertTrue(any("mcpServers" in failure for failure in failures), failures)

    def test_rejects_invalid_interface_urls(self) -> None:
        for field in ("websiteURL", "privacyPolicyURL", "termsOfServiceURL"):
            with self.subTest(field=field):
                manifest = copy.deepcopy(self.manifest)
                manifest["interface"][field] = "http://example.com"

                failures = self.validate_in_temporary_plugin(manifest)

                self.assertTrue(any(field in failure and "https://" in failure for failure in failures), failures)

    def test_rejects_invalid_brand_color(self) -> None:
        manifest = copy.deepcopy(self.manifest)
        manifest["interface"]["brandColor"] = "blue"

        failures = self.validate_in_temporary_plugin(manifest)

        self.assertTrue(any("brandColor" in failure and "#RRGGBB" in failure for failure in failures), failures)

    def test_current_manifest_is_valid(self) -> None:
        failures: list[str] = []

        validate_plugin.validate_plugin_manifest(self.manifest, failures)

        self.assertEqual([], failures)


if __name__ == "__main__":
    unittest.main()
