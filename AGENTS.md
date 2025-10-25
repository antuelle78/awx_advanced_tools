# AGENTS.md

## Build / Lint / Test
- **Build**: `docker compose build`
- **Run**: `docker compose up -d`
- **Lint**: `ruff check . --fix`
- **Type-check**: `mypy --explicit-package-bases --ignore-missing-imports app`
- **Run all tests**: `pytest`
- **Run a single test module**: `pytest tests/test_<module>.py -v`
- **Run a test with a pattern**: `pytest -k <pattern>`
- **Generate a coverage report**: `pytest --cov=app --cov-report=term-missing`

## Style Guidelines
- **Imports**: stdlib, 3rd party, local modules (use `isort`).
- **Formatting**: `black` with line-length 88.
- **Naming**: snake_case for functions/vars/modules, CamelCase for classes, UPPER_CASE for constants.
- **Type hints**: `pydantic.BaseModel` for schemas, `typing` annotations elsewhere.
- **Error handling**: raise `FastAPI.HTTPException` for client errors; use custom exceptions for internal logic.
- **Logging**: Python `logging` module, JSON format, INFO level.
- **Docstrings**: short, one-line for public functions.
- **General**: Follow these guidelines strictly for all code changes.

## CI / PR
- All PRs run `ruff`, `mypy`, and `pytest`.
- No commits should change `requirements.txt` unless needed.
- Maintain backward compatibility of the API.
