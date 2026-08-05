#!/usr/bin/env python3
"""Create a portable Claude Code and Codex skill."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def repository_root() -> Path:
    return Path(__file__).resolve().parent.parent


def yaml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def title_from_name(name: str) -> str:
    return " ".join(part.capitalize() for part in name.split("-"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", help="Skill name in lowercase hyphen-case")
    parser.add_argument(
        "--description",
        required=True,
        help="What the skill does and the requests that should trigger it",
    )
    parser.add_argument("--display-name", help="Optional Codex UI display name")
    parser.add_argument("--short-description", help="Optional Codex UI description")
    parser.add_argument("--default-prompt", help="Optional Codex starter prompt")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    name = args.name.strip()
    description = args.description.strip()

    if not NAME_PATTERN.fullmatch(name) or len(name) > 64:
        print("error: name must be 1-64 lowercase letters, digits, or single hyphens", file=sys.stderr)
        return 2
    if not description or len(description) > 1024 or "\n" in description:
        print("error: description must be a single line of 1-1024 characters", file=sys.stderr)
        return 2
    if "<" in description or ">" in description:
        print("error: description cannot contain angle brackets", file=sys.stderr)
        return 2

    skill_dir = repository_root() / "skills" / name
    if skill_dir.exists():
        print(f"error: skill already exists: {skill_dir}", file=sys.stderr)
        return 1

    display_name = (args.display_name or title_from_name(name)).strip()
    short_description = (args.short_description or description).strip()
    if len(short_description) > 64:
        short_description = short_description[:61].rstrip() + "..."
    default_prompt = (
        args.default_prompt or f"Use ${name} to help complete this task."
    ).strip()
    if f"${name}" not in default_prompt:
        print(f"error: default prompt must mention ${name}", file=sys.stderr)
        return 2

    skill_dir.mkdir(parents=True)
    (skill_dir / "agents").mkdir()

    skill_md = f"""---
name: {name}
description: {yaml_string(description)}
---

# {display_name}

## Workflow

1. Replace this line with the first concrete action.
2. Add decision points, constraints, and validation steps.
3. Remove all placeholder text before using the skill.
"""
    openai_yaml = f"""interface:
  display_name: {yaml_string(display_name)}
  short_description: {yaml_string(short_description)}
  default_prompt: {yaml_string(default_prompt)}
"""

    (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8", newline="\n")
    (skill_dir / "agents" / "openai.yaml").write_text(
        openai_yaml, encoding="utf-8", newline="\n"
    )
    print(f"Created {skill_dir}")
    print("Next: replace the TODO workflow, then run scripts/validate_skills.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

