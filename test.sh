#!/usr/bin/env bash
set -eo pipefail

COLOR_GREEN=$(tput setaf 2)
COLOR_NC=$(tput sgr0) # No Color

#echo "Starting black"
#uv run black .
#echo "OK"

echo "Starting ruff"
uv run ruff check --select I --fix
uv run ruff check --fix
echo "OK"

echo "Starting mypy (dmypy)"
uv run dmypy run -- .
echo "OK"

echo "Starting pytest with coverage"
uv run coverage run -m pytest
uv run coverage report -m
uv run coverage html
echo "OK"

echo "${COLOR_GREEN}All tests passed successfully!${COLOR_NC}"
