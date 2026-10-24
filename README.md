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

## Deploy on a Raspberry Pi

Runs as an unprivileged `dlight` user via systemd (see `deploy/d-light.service`), using the
distro's `python3-rpi-lgpio` for GPIO and hash-pinned dependencies from `requirements.txt`:

```bash
sudo apt install python3-venv python3-rpi-lgpio
sudo useradd --system --groups gpio --home-dir /opt/d.light --shell /usr/sbin/nologin dlight
sudo git clone https://github.com/brycesub/d.light /opt/d.light
sudo python3 -m venv --system-site-packages /opt/d.light/.venv
sudo /opt/d.light/.venv/bin/pip install --require-hashes -r /opt/d.light/requirements.txt
sudo cp /opt/d.light/deploy/d-light.service /etc/systemd/system/
sudo systemctl enable --now d-light
```

## Run

```bash
d-light
```

The web UI is available at `http://<host>/` (port 80).

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
pip-audit -r requirements.txt  # check pinned deps for known CVEs
ruff check .    # lint
ruff format .   # format
mypy .          # type check
```

To refresh the pinned dependencies, edit the floors in `pyproject.toml` and regenerate:

```bash
uv pip compile pyproject.toml --universal --python-version 3.10 --generate-hashes -o requirements.txt
```
