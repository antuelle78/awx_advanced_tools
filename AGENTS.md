# AGENTS.md

## Build / Lint / Test
- **Build**: `docker compose build`
- **Run**: `docker compose up -d`
- **Lint**: `ruff check . --fix`
- **Format**: `ruff format .`
- **Type-check**: `mypy --explicit-package-bases --ignore-missing-imports app`
- **Run all tests**: `pytest`
- **Run a single test**: `pytest tests/test_<module>.py -v`
- **Run tests matching pattern**: `pytest -k <pattern>`
- **Coverage**: `pytest --cov=app --cov-report term-missing`

## Style Guidelines
- **Imports**: stdlib → 3rd-party → local (use `isort`)
- **Formatting**: `ruff format` (line-length 88)
- **Naming**: snake_case vars/functions, CamelCase classes, UPPER_CASE constants
- **Type hints**: `pydantic.BaseModel` for schemas; standard typing otherwise
- **Error handling**: `FastAPI.HTTPException` for client errors; custom exceptions for internal logic
- **Logging**: `logging` module, JSON output, INFO level
- **Docstrings**: one-line for public functions
- **Async**: Use async/await for I/O operations

## CI / PR
- All PRs run `ruff`, `mypy`, `pytest`, security scans
- Do not change `requirements.txt` unless needed
- Keep API backwards compatible
- No Cursor or Copilot rules in this repo
