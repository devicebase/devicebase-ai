# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI agent framework built on top of devicebase, designed to be open-sourced.

## Commands

```bash
# Install dev dependencies
uv sync --extra dev

# Run all tests
pytest

# Run a single test file
pytest tests/test_example.py

# Lint and format check
ruff check .

# Auto-fix lint issues
ruff check --fix .

# Type check
mypy src/

# Run pre-commit hooks
pre-commit run --all-files
```

## Architecture

```
src/devicebase_ai_agent/     # Main package source
tests/                       # pytest tests, mirror src/ structure
pyproject.toml               # Project config (uv, pytest, ruff, mypy)
```

- Source code lives under `src/<package_name>/` (src layout, importable from project root)
- Tests mirror the src structure under `tests/`
- All tooling is configured via `pyproject.toml` (no separate config files)

## Conventions

- Python >= 3.11, type annotations required
- Use `uv` for dependency management (`uv sync`, `uv add`)
- Format with `ruff check --fix`, lint with `ruff check`, type-check with `mypy`
- Tests in `tests/`, naming `test_*.py`
- Coverage target: 80%
