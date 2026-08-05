#!/usr/bin/env python3
"""Validate every skill in this repository without third-party packages."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER_PATTERN = re.compile(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", re.DOTALL)


def repository_root() -> Path:
    return Path(__file__).resolve().parent.parent


def parse_scalar(value: str) -> str:
    value = value.strip()
    if value.startswith('"'):
        parsed = json.loads(value)
        if not isinstance(parsed, str):
            raise ValueError("frontmatter values must be strings")
        return parsed
    if not value or value[0] in "'[{&*!|>":
        raise ValueError("use a plain string or a JSON-compatible quoted string")
    return value


def validate_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        return ["missing SKILL.md"]

    content = skill_file.read_text(encoding="utf-8")
    match = FRONTMATTER_PATTERN.match(content)
    if not match:
        return ["invalid or missing YAML frontmatter"]

    fields: dict[str, str] = {}
    for line_number, raw_line in enumerate(match.group(1).splitlines(), start=2):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if raw_line.startswith((" ", "\t")) or ":" not in raw_line:
            errors.append(f"line {line_number}: only flat key/value frontmatter is supported")
            continue
        key, value = raw_line.split(":", 1)
        key = key.strip()
        if key in fields:
            errors.append(f"line {line_number}: duplicate field '{key}'")
            continue
        try:
            fields[key] = parse_scalar(value)
        except (ValueError, json.JSONDecodeError) as exc:
            errors.append(f"line {line_number}: invalid '{key}' value: {exc}")

    unexpected = sorted(set(fields) - {"name", "description"})
    if unexpected:
        errors.append(f"unexpected frontmatter fields: {', '.join(unexpected)}")

    name = fields.get("name", "").strip()
    description = fields.get("description", "").strip()
    if not name:
        errors.append("missing name")
    elif not NAME_PATTERN.fullmatch(name) or len(name) > 64:
        errors.append("name must be 1-64 lowercase letters, digits, or single hyphens")
    elif name != skill_dir.name:
        errors.append(f"name '{name}' must match folder '{skill_dir.name}'")

    if not description:
        errors.append("missing description")
    elif len(description) > 1024:
        errors.append("description exceeds 1024 characters")
    elif "<" in description or ">" in description:
        errors.append("description cannot contain angle brackets")

    if "TODO" in content or "Replace this line" in content:
        errors.append("placeholder text remains in SKILL.md")

    return errors


def main() -> int:
    skills_root = repository_root() / "skills"
    skill_dirs = sorted(
        path for path in skills_root.iterdir() if path.is_dir() and not path.name.startswith(".")
    )
    if not skill_dirs:
        print("No skills found; repository structure is valid.")
        return 0

    failure_count = 0
    for skill_dir in skill_dirs:
        errors = validate_skill(skill_dir)
        if errors:
            failure_count += 1
            print(f"FAIL {skill_dir.name}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"PASS {skill_dir.name}")

    if failure_count:
        print(f"Validation failed for {failure_count} skill(s).")
        return 1
    print(f"Validated {len(skill_dirs)} skill(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

