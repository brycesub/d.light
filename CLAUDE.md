# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Install with Raspberry Pi hardware support
pip install -e ".[pi]"

# Run the application
d-light

# Run all tests (includes coverage reporting, 70% minimum enforced)
pytest

# Run a single test file
pytest tests/test_web.py -v

# Lint
ruff check .

# Format
ruff format .

# Type check
mypy .
```

## Architecture

**d.light** is a Raspberry Pi wake-up light alarm clock. Three daemon threads share a single `LightState` instance:

- **`scheduler()`** — monitors wall time and triggers gradual brightening at `alarmtime - brightentime`. Handles snooze via a `threading.Event` (`esnooze`).
- **`light()`** — reads `state.dim` every 100ms and writes to 8 GPIO pins using binary encoding (bit 0 → pin p1, bit 1 → pin p2, …, bit 7 → pin p128), giving 256 brightness levels. Pins are active-low.
- **`web()`** — returns a configured `Bottle` app serving the REST API and static files from `www/`.

### Key files

| File | Purpose |
|------|---------|
| `d_light.py` | `LightState`, `scheduler()`, `light()`, `web()`, `main()` |
| `config.py` | Frozen dataclasses: `PinConfig`, `DimConfig`, `AlarmConfig`, `WebConfig`, `AppConfig` |
| `hardware.py` | `GPIOInterface` ABC, `RealGPIO`, `MockGPIO`, `create_gpio()` factory |
| `tests/conftest.py` | Shared pytest fixtures (config, mock_gpio, state) |

### Thread safety

`LightState` wraps all field access with an internal `threading.Lock`. Use `state.update(**kwargs)` for atomic multi-field writes and `state.to_dict()` for a consistent snapshot read.

### Hardware abstraction

`create_gpio()` returns `RealGPIO` when `RPi.GPIO` is importable (Raspberry Pi), otherwise `MockGPIO`. Tests always use `MockGPIO`. `MockGPIO.get_state()` exposes pin values for test assertions.

### In-progress migration

`d_light.py` currently uses **Bottle** for the web layer, but `pyproject.toml` lists **FastAPI/uvicorn** as the declared dependencies. The migration from Bottle to FastAPI is not yet complete.
