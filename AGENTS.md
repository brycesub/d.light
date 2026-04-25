# Repository Guidelines

## Project Structure & Module Organization

This Python 3.10+ FastAPI app controls a Raspberry Pi wake-up light. Core code lives at the repository root: `d_light.py` contains app state, scheduler, light loop, web app, and entry point; `config.py` defines frozen configuration dataclasses; `hardware.py` contains GPIO abstractions and mock hardware. Static frontend files are served directly from `www/`. Tests live in `tests/`, with shared fixtures in `tests/conftest.py`.

## Build, Test, and Development Commands

- `pip install -e ".[dev]"` installs the package plus pytest, coverage, ruff, mypy, freezegun, and httpx.
- `pip install -e ".[pi]"` installs Raspberry Pi GPIO support when running on Pi hardware.
- `d-light` starts the web server; the UI is available at `http://<host>:8080/`.
- `pytest` runs the full test suite with coverage enforcement.
- `pytest tests/test_web.py -v` runs one test module with verbose output.
- `ruff check .` lints Python code; `ruff format .` formats it.
- `mypy .` runs strict type checking.

## Coding Style & Naming Conventions

Use Python 3.10-compatible syntax and keep lines at or below 100 characters. Ruff is the formatter and linter. Prefer typed functions and dataclasses consistent with the existing code. Use `snake_case` for functions, variables, and modules; `PascalCase` for classes; and descriptive pytest fixture names. Frontend code should remain vanilla JavaScript and Bootstrap CSS without adding a build step.

## Testing Guidelines

Pytest discovers `tests/test_*.py`, `Test*` classes, and `test_*` functions. Coverage is configured for `d_light`, `hardware`, and `config`, with a 70% minimum. Use `MockGPIO` and existing fixtures for hardware-facing tests; avoid requiring Raspberry Pi hardware in CI or local development. Add focused tests for scheduler timing, state transitions, API endpoints, and configuration validation.

## Commit & Pull Request Guidelines

Recent commits use short, direct messages such as `replace Bottle with FastAPI` and `upgrade to Bootstrap 5.3.8, drop jQuery`. Follow that style: concise, imperative, and scoped to the change. Pull requests should describe the behavior change, list test commands run, link related issues when applicable, and include screenshots or browser notes for UI changes under `www/`.

## Security & Configuration Tips

Do not commit local virtual environments, coverage output, caches, or machine-specific settings. Keep hardware access behind `hardware.py` so tests and non-Pi machines continue to use `MockGPIO`. Treat the web UI as local-network software; avoid exposing it publicly without adding authentication and transport security.
