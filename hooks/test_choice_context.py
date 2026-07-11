#!/usr/bin/env python3
"""Validate that UI/extra_context choice values match cookiecutter.json lists."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from interactive_prompts import CHOICE_OPTIONS, validate_choice_answers  # noqa: E402


def load_cookiecutter_choices() -> dict[str, list[str]]:
    data = json.loads((ROOT / "cookiecutter.json").read_text())
    return {
        key: value
        for key, value in data.items()
        if isinstance(value, list) and not key.startswith("_")
    }


def assert_choice_maps_match() -> None:
    from_json = load_cookiecutter_choices()
    json_keys = set(from_json)
    code_keys = set(CHOICE_OPTIONS)
    if json_keys != code_keys:
        raise AssertionError(
            "CHOICE_OPTIONS keys drift from cookiecutter.json lists:\n"
            f"  only in json: {sorted(json_keys - code_keys)}\n"
            f"  only in code: {sorted(code_keys - json_keys)}"
        )
    for key in sorted(json_keys):
        json_opts = tuple(from_json[key])
        code_opts = CHOICE_OPTIONS[key]
        # Order in cookiecutter.json matters for --no-input defaults; require same members.
        if set(json_opts) != set(code_opts):
            raise AssertionError(
                f"{key}: cookiecutter.json={json_opts} vs CHOICE_OPTIONS={code_opts}"
            )


def base_answers(**overrides: str) -> dict[str, str]:
    answers = {
        "project_name": "ChoiceMatrix",
        "project_slug": "choice_matrix",
        "first_name": "a",
        "last_name": "b",
        "license": "MIT",
        "postgres_user": "user",
        "postgres_password": "password",
        "postgres_version": "17.10",
        "use_jwt": "y",
        "use_sentry": "n",
        "use_vscode": "n",
        "use_pgadmin": "n",
        "use_redis": "n",
        "use_rabbitmq": "n",
        "use_celery": "n",
        "celery_broker": "redis",
        "use_asgi": "n",
        "use_websockets": "n",
        "reverse_proxy": "none",
        "use_code_style": "y",
        "use_testing": "y",
        "use_ci": "n",
        "ci_provider": "github",
        "precommit_base": "y",
        "precommit_pyupgrade": "y",
        "precommit_ruff": "y",
        "precommit_pydoclint": "y",
        "precommit_translation_lint": "y",
    }
    answers.update(overrides)
    return answers


def edge_case_answer_sets() -> list[tuple[str, dict[str, str]]]:
    """Scenarios that previously (or easily could) pass invalid choice values."""
    return [
        ("ci_off", base_answers(use_ci="n", ci_provider="github")),
        ("ci_gitlab", base_answers(use_ci="y", ci_provider="gitlab")),
        ("celery_off", base_answers(use_celery="n", celery_broker="redis")),
        (
            "celery_rabbit",
            base_answers(
                use_celery="y",
                use_rabbitmq="y",
                celery_broker="rabbitmq",
            ),
        ),
        (
            "code_style_off",
            base_answers(
                use_code_style="n",
                precommit_base="n",
                precommit_pyupgrade="n",
                precommit_ruff="n",
                precommit_pydoclint="n",
                precommit_translation_lint="n",
            ),
        ),
        ("proxy_none", base_answers(reverse_proxy="none")),
        ("proxy_nginx", base_answers(reverse_proxy="nginx")),
        ("proxy_traefik", base_answers(reverse_proxy="traefik")),
        ("license_none", base_answers(license="None")),
        ("session_auth", base_answers(use_jwt="n")),
        (
            "websockets",
            base_answers(
                use_asgi="y",
                use_redis="y",
                use_websockets="y",
            ),
        ),
    ]


def assert_rejects_invalid() -> None:
    try:
        validate_choice_answers(base_answers(ci_provider="none"))
    except ValueError as exc:
        if "ci_provider" not in str(exc):
            raise AssertionError(f"expected ci_provider error, got: {exc}") from exc
    else:
        raise AssertionError("ci_provider=none should be rejected")

    try:
        validate_choice_answers(base_answers(celery_broker="amqp"))
    except ValueError as exc:
        if "celery_broker" not in str(exc):
            raise AssertionError(f"expected celery_broker error, got: {exc}") from exc
    else:
        raise AssertionError("celery_broker=amqp should be rejected")


def main() -> int:
    assert_choice_maps_match()
    assert_rejects_invalid()

    for name, answers in edge_case_answer_sets():
        validate_choice_answers(answers)
        print(f"  OK  {name}")

    # Also exercise cookiecutter's overwrite validation for each scenario.
    from cookiecutter.generate import apply_overwrites_to_context

    choices = load_cookiecutter_choices()
    for name, answers in edge_case_answer_sets():
        context = {key: list(value) for key, value in choices.items()}
        # Seed non-choice defaults cookiecutter expects as strings.
        context.update(
            {
                "project_name": answers["project_name"],
                "project_slug": answers["project_slug"],
                "first_name": answers["first_name"],
                "last_name": answers["last_name"],
                "postgres_user": answers["postgres_user"],
                "postgres_password": answers["postgres_password"],
            }
        )
        apply_overwrites_to_context(context, answers)
        print(f"  OK  cookiecutter-overwrite:{name}")

    print("All choice-context scenarios passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
