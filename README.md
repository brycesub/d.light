# d.light

A Raspberry Pi wake-up light alarm clock with a web interface.

Gradually brightens a multi-LED light over a configurable period before the alarm time. Controllable from any browser on the local network.

## Requirements

- Python 3.10+
- Raspberry Pi with GPIO-connected LEDs (or runs in mock mode on any machine)

## Install

```bash
# Standard install
pip install -e .

# With Raspberry Pi GPIO support
pip install -e ".[pi]"

# With dev tools
pip install -e ".[dev]"
```

## Run

```bash
d-light
```

The web UI is available at `http://<host>:8080/`.

## API

All endpoints return the current state as JSON.

| Endpoint | Effect |
|---|---|
| `GET /stat` | Return current state |
| `GET /light/on` | Turn light on (100%) |
| `GET /light/off` | Turn light off |
| `GET /dim/<0-100>` | Set brightness |
| `GET /alarm/on` | Enable alarm |
| `GET /alarm/off` | Disable alarm |
| `GET /alarmset/<HH:MM>` | Set alarm time |
| `GET /snoozeset/<minutes>` | Set snooze duration |
| `GET /brightenset/<minutes>` | Set brightening duration |
| `GET /snooze` | Snooze active alarm |
| `GET /alarmoff` | Cancel active alarm |

## Development

```bash
pytest          # run tests (70% coverage required)
ruff check .    # lint
ruff format .   # format
mypy .          # type check
```
