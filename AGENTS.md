# Agents (cookiecutter template)

This repo is a **Cookiecutter** template. Generated app code lives under `{{cookiecutter.project_name}}/`.

## Do

- Keep `cookiecutter.json` ↔ `hooks/interactive_prompts.py` `CHOICE_OPTIONS` in sync (`python hooks/test_choice_context.py`).
- Validate incompatible options in `hooks/pre_gen_project.py`.
- Delete unused generated files in `hooks/post_gen_project.py` (auth mode, Celery, WS, CI, rules, docs).
- Prefer Jinja conditionals in templates; post_gen for whole-file removal.
- Generated agent surface: slim `AGENTS.md` + `.cursor/rules/*.mdc` (feature rules removed when option is off).

## Don't

- Invent options without prompts, `pre_gen` checks, and README row.
- Leave Celery/WS/testing docs or `.cursor/rules/*` when the feature is disabled.
- Bulk-edit generated `docs/style-guide/` unless changing a convention (keep pages concise).
- `git commit` / `git push` unless the user asks.

## Read when needed

| Task | Open |
|------|------|
| Prompts / UI | `hooks/interactive_prompts.py`, `hooks/pre_prompt.py` |
| Validation / cleanup | `hooks/pre_gen_project.py`, `hooks/post_gen_project.py` |
| Variables | `cookiecutter.json` |
| Generated Django app | `{{cookiecutter.project_name}}/` (+ its `AGENTS.md`) |
| Template CI / smoke | `.github/workflows/ci.yml`, `make smoke` |
| Template version | `VERSION` |
