.PHONY: install install-dev lint format test test-all build clean

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt
	pip install -e . --no-deps
	pre-commit install

lint:
	ruff check .
	black --check .

format:
	ruff check --fix .
	black .

test:
	pytest -m "not integration" --cov --cov-report=term-missing

test-all:
	pytest --cov --cov-report=term-missing

build:
	python -m build

clean:
	rm -rf build dist *.egg-info .pytest_cache .ruff_cache .coverage htmlcov
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
