#!/usr/bin/env bash
set -e

echo "Running tests..."
uv run pytest -q

echo "Running code formatting checks..."
uv run ruff check .
uv run ruff format --check .

echo "Running type checks..."
uv run mypy .

echo "All checks passed!"
