# AGENTS.md

## Build / Lint / Test
- **Build**: `docker compose build`
- **Run**: `docker compose up -d`
- **Lint**: `ruff check . --fix`
- **Type‑check**: `mypy app`
- **Run all tests**: `pytest`
- **Run a single test module**: `pytest tests/<module>.py`
- **Run a test with a pattern**: `pytest -k <pattern>`
- **Generate a coverage report**: `pytest --cov=app --cov-report=term-missing`

## Style Guidelines
- **Imports**: `isort` order – stdlib, 3rd party, local modules.
- **Formatting**: `black` with line‑length 88.
- **Naming**: snake_case for functions, vars, modules. CamelCase for classes.
- **Type hints**: use `pydantic.BaseModel` for request/response schemas, otherwise `typing` annotations.
- **Error handling**: raise FastAPI HTTPException for client errors.
- **Logging**: use Python `logging` module, log at INFO level.
- **Docstrings**: short, one‑line for public functions.

## CI / PR
- All PRs run `ruff`, `mypy`, and `pytest`.
- No commits should change the `requirements.txt` unless needed.
- Maintain backward compatibility of the API.
