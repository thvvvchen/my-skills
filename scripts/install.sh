#!/usr/bin/env bash
set -euo pipefail

agent="all"
mode="auto"
force="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --agent) agent="${2:-}"; shift 2 ;;
    --mode) mode="${2:-}"; shift 2 ;;
    --force) force="true"; shift ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done

if [[ ! "$agent" =~ ^(all|claude|codex|cursor|kimi|trae)$ ]]; then
  echo "--agent must be all, claude, codex, cursor, kimi, or trae" >&2
  exit 2
fi
if [[ ! "$mode" =~ ^(auto|link|copy)$ ]]; then
  echo "--mode must be auto, link, or copy" >&2
  exit 2
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"
skills_root="$repo_root/plugins/my-skills-czf/skills"
targets=()
[[ "$agent" == "all" || "$agent" == "claude" ]] && targets+=("claude|$HOME/.claude/skills|link")
[[ "$agent" == "all" || "$agent" == "codex" ]] && targets+=("codex|$HOME/.codex/skills|link")
[[ "$agent" == "all" || "$agent" == "cursor" ]] && targets+=("cursor|$HOME/.cursor/skills|copy")
[[ "$agent" == "all" || "$agent" == "kimi" ]] && targets+=("kimi|$HOME/.kimi/skills|link")
[[ "$agent" == "all" || "$agent" == "trae" ]] && targets+=("trae|$HOME/.trae/skills|link")

found="false"
for skill_dir in "$skills_root"/*; do
  [[ -d "$skill_dir" && -f "$skill_dir/SKILL.md" ]] || continue
  found="true"
  skill_name="$(basename "$skill_dir")"
  for target in "${targets[@]}"; do
    IFS='|' read -r target_agent target_root default_mode <<< "$target"
    effective_mode="$mode"
    [[ "$effective_mode" == "auto" ]] && effective_mode="$default_mode"
    if [[ "$target_agent" == "cursor" && "$effective_mode" == "link" ]]; then
      echo "Cursor does not reliably discover linked skills; using copy mode." >&2
      effective_mode="copy"
    fi
    mkdir -p "$target_root"
    destination="$target_root/$skill_name"
    if [[ -e "$destination" || -L "$destination" ]]; then
      if [[ "$force" != "true" ]]; then
        echo "Destination exists: $destination. Re-run with --force." >&2
        exit 1
      fi
      rm -rf -- "$destination"
    fi
    if [[ "$effective_mode" == "link" ]]; then
      ln -s "$skill_dir" "$destination"
    else
      cp -R "$skill_dir" "$destination"
    fi
    echo "Installed $skill_name -> $destination ($effective_mode)"
  done
done

if [[ "$found" != "true" ]]; then
  echo "No skills found. Create one with scripts/new_skill.py first."
fi
