.PHONY: install run debug clean lint lint-strict

PYTHON := python3
MAIN := src/pac-man.py
CONFIG := inputs/config.json

install:
	uv sync

run:
	uv run $(PYTHON) $(MAIN) $(CONFIG)

debug:
	uv run $(PYTHON) -m pdb $(MAIN) $(CONFIG)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache

lint:
	uv run flake8 src/.
	uv run mypy src/.

lint-strict:
	uv run flake8 src/.
	uv run mypy . --warn-return-any--warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs--check-untyped-defs


.PHONY: install run debug clean lint lint-strict
