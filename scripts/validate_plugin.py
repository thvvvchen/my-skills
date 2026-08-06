"""Validate the repository's Codex plugin and marketplace manifests."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


PLUGIN_NAME = "my-skills-czf"
PLUGIN_ROOT = Path(__file__).resolve().parents[1] / "plugins" / PLUGIN_NAME
MARKETPLACE_PATH = Path(__file__).resolve().parents[1] / ".agents" / "plugins" / "marketplace.json"
SEMVER_PATTERN = re.compile(
    r"^(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)"
    r"(?:-(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
INSTALL_POLICIES = {"NOT_AVAILABLE", "AVAILABLE", "INSTALLED_BY_DEFAULT"}
AUTH_POLICIES = {"ON_INSTALL", "ON_USE"}
PLUGIN_FIELDS = {
    "id",
    "name",
    "version",
    "description",
    "skills",
    "apps",
    "mcpServers",
    "interface",
    "author",
    "homepage",
    "repository",
    "license",
    "keywords",
}
AUTHOR_FIELDS = {"name", "email", "url"}
INTERFACE_FIELDS = {
    "displayName",
    "shortDescription",
    "longDescription",
    "developerName",
    "category",
    "capabilities",
    "websiteURL",
    "privacyPolicyURL",
    "termsOfServiceURL",
    "brandColor",
    "composerIcon",
    "logo",
    "logoDark",
    "screenshots",
    "defaultPrompt",
    "default_prompt",
}
REQUIRED_INTERFACE_FIELDS = {
    "displayName",
    "shortDescription",
    "longDescription",
    "developerName",
    "category",
    "capabilities",
}


def repository_root() -> Path:
    return Path(__file__).resolve().parents[1]


def path_label(path: Path) -> str:
    root = repository_root().resolve()
    try:
        return str(path.resolve().relative_to(root))
    except ValueError:
        return str(path)


def load_json(path: Path, failures: list[str]) -> Any:
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        failures.append(f"{path_label(path)} does not exist")
    except (json.JSONDecodeError, UnicodeError, OSError) as exc:
        failures.append(f"could not parse {path_label(path)}: {exc}")
    return None


def require_string(value: Any, field: str, failures: list[str], *, non_empty: bool = True) -> bool:
    if not isinstance(value, str) or (non_empty and not value.strip()):
        failures.append(f"{field} must be a non-empty string")
        return False
    return True


def validate_plugin_manifest(manifest: Any, failures: list[str]) -> None:
    if not isinstance(manifest, dict):
        failures.append("plugin manifest must be a JSON object")
        return

    reject_unknown_fields(manifest, PLUGIN_FIELDS, None, failures)

    if manifest.get("name") != PLUGIN_NAME:
        failures.append(f"plugin name must be {PLUGIN_NAME}")
    version = manifest.get("version")
    if not isinstance(version, str) or not SEMVER_PATTERN.fullmatch(version):
        failures.append("plugin version must use semantic versioning")
    require_string(manifest.get("description"), "plugin description", failures)

    author = manifest.get("author")
    if not isinstance(author, dict):
        failures.append("plugin author must be an object")
    else:
        reject_unknown_fields(author, AUTHOR_FIELDS, "author", failures)
        if author.get("name") != "thvvvchen":
            failures.append("plugin author.name must be thvvvchen")
        author_url = author.get("url")
        if require_string(author_url, "plugin author.url", failures):
            parsed_url = urlparse(author_url)
            if parsed_url.scheme != "https" or not parsed_url.netloc:
                failures.append("plugin author.url must be an absolute https:// URL")

    validate_component_path(manifest, "skills", "skills", "directory", failures)
    validate_component_path(manifest, "apps", ".app.json", "file", failures)

    mcp_servers = manifest.get("mcpServers")
    if isinstance(mcp_servers, str):
        validate_component_path(manifest, "mcpServers", ".mcp.json", "file", failures)
    elif mcp_servers is not None and not isinstance(mcp_servers, dict):
        failures.append("plugin mcpServers must be a string or object")

    interface = manifest.get("interface")
    if not isinstance(interface, dict):
        failures.append("plugin interface must be an object")
        return
    reject_unknown_fields(interface, INTERFACE_FIELDS, "interface", failures)
    for field in REQUIRED_INTERFACE_FIELDS:
        if field not in interface:
            failures.append(f"plugin interface missing {field}")
    for field in ("displayName", "shortDescription", "longDescription", "developerName", "category"):
        require_string(interface.get(field), f"plugin interface.{field}", failures)

    capabilities = interface.get("capabilities")
    if (
        not isinstance(capabilities, list)
        or not capabilities
        or any(not isinstance(item, str) or not item.strip() for item in capabilities)
    ):
        failures.append("plugin interface.capabilities must be a non-empty string array")

    if "defaultPrompt" not in interface and "default_prompt" not in interface:
        failures.append("plugin interface missing defaultPrompt or default_prompt")
    prompts = interface.get("defaultPrompt", interface.get("default_prompt"))
    if (
        not isinstance(prompts, list)
        or not 1 <= len(prompts) <= 3
        or any(not isinstance(item, str) or not item.strip() or len(item) > 128 for item in prompts)
    ):
        failures.append("plugin interface.defaultPrompt must contain 1-3 non-empty strings of at most 128 characters")


def reject_unknown_fields(
    payload: dict[str, Any],
    allowed_fields: set[str],
    prefix: str | None,
    failures: list[str],
) -> None:
    for field in sorted(set(payload) - allowed_fields):
        qualified_field = f"{prefix}.{field}" if prefix else field
        failures.append(
            f"plugin.json field `{qualified_field}` is not accepted by plugin validation"
        )


def validate_component_path(
    manifest: dict[str, Any],
    field: str,
    expected: str,
    kind: str,
    failures: list[str],
) -> None:
    raw_path = manifest.get(field)
    if raw_path is None:
        return
    if not isinstance(raw_path, str) or not raw_path.strip():
        failures.append(f"plugin {field} must be a non-empty relative path")
        return

    normalized_path = raw_path.replace("\\", "/")
    candidate = Path(normalized_path)
    if candidate.is_absolute() or any(part == ".." for part in candidate.parts):
        failures.append(f"plugin {field} must stay inside the plugin root")
        return

    normalized_contract = candidate.as_posix().rstrip("/")
    if normalized_contract.startswith("./"):
        normalized_contract = normalized_contract[2:]
    if normalized_contract != expected:
        failures.append(f"plugin {field} must resolve to {expected}")
        return

    plugin_root = PLUGIN_ROOT.resolve()
    resolved_path = (plugin_root / candidate).resolve()
    try:
        resolved_path.relative_to(plugin_root)
    except ValueError:
        failures.append(f"plugin {field} must stay inside the plugin root")
        return

    exists = resolved_path.is_dir() if kind == "directory" else resolved_path.is_file()
    if not exists:
        failures.append(f"plugin {field} path {raw_path} does not exist")


def validate_marketplace(manifest: Any, failures: list[str]) -> None:
    if not isinstance(manifest, dict):
        failures.append("marketplace manifest must be a JSON object")
        return
    if manifest.get("name") != PLUGIN_NAME:
        failures.append(f"marketplace name must be {PLUGIN_NAME}")
    interface = manifest.get("interface")
    if not isinstance(interface, dict) or interface.get("displayName") != "My Skills CZF":
        failures.append("marketplace interface.displayName must be My Skills CZF")

    entries = manifest.get("plugins")
    if not isinstance(entries, list) or len(entries) != 1:
        failures.append("marketplace plugins must contain exactly one entry")
        return
    entry = entries[0]
    if not isinstance(entry, dict) or entry.get("name") != PLUGIN_NAME:
        failures.append(f"marketplace plugin entry name must be {PLUGIN_NAME}")
        return
    source = entry.get("source")
    if not isinstance(source, dict) or source.get("source") != "local" or source.get("path") != "./plugins/my-skills-czf":
        failures.append("marketplace plugin source must be local ./plugins/my-skills-czf")

    policy = entry.get("policy")
    if not isinstance(policy, dict):
        failures.append("marketplace plugin policy must be an object")
    else:
        if policy.get("installation") not in INSTALL_POLICIES:
            failures.append("marketplace installation policy is invalid")
        if policy.get("authentication") not in AUTH_POLICIES:
            failures.append("marketplace authentication policy is invalid")
    if not isinstance(entry.get("category"), str) or not entry.get("category", "").strip():
        failures.append("marketplace plugin category must be a non-empty string")


def validate_paths(failures: list[str]) -> None:
    root = repository_root().resolve()
    plugin_root = PLUGIN_ROOT.resolve()
    if root not in plugin_root.parents:
        failures.append("plugin path must be inside repository")
    if not (plugin_root / ".codex-plugin" / "plugin.json").is_file():
        failures.append("plugin.json does not exist")
    if not (plugin_root / "skills").is_dir():
        failures.append("plugin skills directory does not exist")

    try:
        marketplace_source = (MARKETPLACE_PATH.parent.parent.parent / "plugins" / PLUGIN_NAME).resolve()
        marketplace_source.relative_to(root)
    except ValueError:
        failures.append("marketplace source path must resolve inside repository")


def main() -> int:
    failures: list[str] = []
    plugin_manifest = load_json(PLUGIN_ROOT / ".codex-plugin" / "plugin.json", failures)
    marketplace_manifest = load_json(MARKETPLACE_PATH, failures)
    validate_plugin_manifest(plugin_manifest, failures)
    validate_marketplace(marketplace_manifest, failures)
    validate_paths(failures)
    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1
    print("Validated plugin my-skills-czf and marketplace my-skills-czf.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
