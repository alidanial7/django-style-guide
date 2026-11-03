.PHONY: smoke choices help

help:
	@echo "Targets:"
	@echo "  make choices  - validate cookiecutter.json ↔ UI choice maps"
	@echo "  make smoke    - generate option matrices + agent-surface asserts (needs cookiecutter, rg)"

choices:
	python3 hooks/test_choice_context.py

smoke:
	./scripts/smoke_generate.sh
