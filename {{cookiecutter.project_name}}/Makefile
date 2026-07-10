.PHONY: help install up down migrate makemigrations runserver test lint format check shell

PYTHON ?= python
PIP ?= pip
MANAGE := $(PYTHON) manage.py

help:
	@echo "Targets:"
	@echo "  install         Install requirements_dev.txt"
	@echo "  up              Start local Docker infra (start-dev-services.sh)"
	@echo "  down            Stop local Docker infra"
	@echo "  migrate         Apply migrations"
	@echo "  makemigrations  Create migrations"
	@echo "  runserver       Run manage.py devserver"
	@echo "  test            Run pytest"
	@echo "  lint            Run linters"
	@echo "  format          Auto-format (ruff, when enabled)"
	@echo "  check           Django system check"
	@echo "  shell           Django shell_plus / shell"

install:
	$(PIP) install -r requirements_dev.txt
{%- if cookiecutter.use_code_style == "y" %}
	pre-commit install || true
{%- endif %}

up:
	./start-dev-services.sh

down:
	docker compose -f docker-compose.dev.yml down

migrate:
	$(MANAGE) migrate

makemigrations:
	$(MANAGE) makemigrations

runserver:
	$(MANAGE) devserver

check:
	$(MANAGE) check

shell:
	$(MANAGE) shell_plus || $(MANAGE) shell

{%- if cookiecutter.use_testing == "y" %}
test:
	pytest -q
{%- else %}
test:
	@echo "Testing was not enabled at generation time (use_testing=n)."
	@exit 1
{%- endif %}

{%- if cookiecutter.use_code_style == "y" %}
lint:
	ruff check .
	ruff format --check .

format:
	ruff check --fix .
	ruff format .
{%- else %}
lint:
	flake8 .

format:
	@echo "Code style tooling was not enabled (use_code_style=n)."
	@exit 1
{%- endif %}
