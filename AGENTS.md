# Repository Instructions

This repository stores reusable AI agent skills.

## Authoring rules

- Keep every installable skill under `skills/<skill-name>/`.
- Name skills with lowercase letters, digits, and hyphens only.
- Give each skill a `SKILL.md` with only `name` and `description` in YAML frontmatter.
- Put triggering conditions in `description`, because agents see it before loading the body.
- Keep `SKILL.md` concise and imperative. Move detailed knowledge to `references/`.
- Put deterministic or repeatedly used automation in `scripts/` and test it.
- Put output templates and media in `assets/`.
- Do not add README or changelog files inside an individual skill.
- Never commit credentials, tokens, cookies, private keys, or production secrets.

## Workflow

1. Run `python scripts/new_skill.py <name> --description "..."`.
2. Replace the generated TODO instructions with the real workflow.
3. Add only the resource directories the skill needs.
4. Run `python scripts/validate_skills.py`.
5. Test the skill with realistic requests before relying on it.

