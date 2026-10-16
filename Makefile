.PHONY: install audit test lint size-check

install:
	pip install -e ".[dev]"

audit: lint test size-check
	ruff check .
	mypy ironwise
	bandit -r ironwise
	pip-audit

test:
	pytest

lint:
	ruff check .

size-check:
	python scripts/check_build_size.py
