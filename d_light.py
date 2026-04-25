"""d.light - A Raspberry Pi Wake-up Light Alarm clock with Web Interface."""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from config import AppConfig
from hardware import GPIOInterface, MockGPIO, create_gpio

logger = logging.getLogger(__name__)

WWW_ROOT = Path(__file__).resolve().parent / "www"


@dataclass
class LightState:
    """Thread-safe mutable state shared across subsystems."""

    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)
    on: bool = False
    dim: float = 0.0
    snoozetime: float = 5.0
    brightentime: float = 15.0
    alarmset: bool = True
    alarmtime: str = "07:00"
    alarming: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Return a snapshot of current state."""
        with self._lock:
            return {
                "on": self.on,
                "dim": self.dim,
                "snoozetime": self.snoozetime,
                "brightentime": self.brightentime,
                "alarmset": self.alarmset,
                "alarmtime": self.alarmtime,
                "alarming": self.alarming,
            }

    def update(self, **kwargs: Any) -> None:
        """Atomically update one or more state fields."""
        with self._lock:
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
                else:
                    raise AttributeError(f"LightState has no attribute '{key}'")


def scheduler(state: LightState, esnooze: threading.Event, config: AppConfig) -> None:
    """Background thread that triggers the alarm and manages brightening."""
    dim_cfg = config.dim
    while True:
        now = datetime.now()
        try:
            alarm_dt = datetime.strptime(state.alarmtime, "%H:%M")
        except ValueError:
            logger.error("Invalid alarmtime format: %s", state.alarmtime)
            time.sleep(60)
            continue

        trigger_at = alarm_dt - timedelta(minutes=int(state.brightentime))
        if (
            trigger_at.hour == now.hour
            and trigger_at.minute == now.minute
            and now.second <= 2
            and state.alarmset
        ):
            state.update(alarming=True)
            i = dim_cfg.dimlow
            while state.alarming and state.alarmset:
                if esnooze.is_set():
                    i = dim_cfg.dimlow
                    esnooze.clear()
                    if state.alarming:
                        state.update(dim=0.0, on=False)
                        esnooze.wait(timeout=state.snoozetime * 60)
                    if not state.alarming:
                        esnooze.clear()
                        break
                dim_pct = (float(i) - dim_cfg.dimlow) / dim_cfg.dimrange * 100
                state.update(dim=dim_pct, on=True)
                esnooze.wait(timeout=state.brightentime * 60.0 / float(dim_cfg.dimrange))
                if i < dim_cfg.dimhigh:
                    i += 1
        time.sleep(1)


def light(state: LightState, gpio: GPIOInterface, config: AppConfig) -> None:
    """Background thread that drives GPIO outputs based on state."""
    pins = config.pins
    gpio.setup(pins.all_pins)

    try:
        while True:
            if state.on:
                if state.dim == 0:
                    dim = 0
                    state.update(on=False)
                elif state.dim == 100:
                    dim = 255
                else:
                    dim = int(state.dim / 100.0 * config.dim.dimrange + config.dim.dimlow)

                gpio.write(pins.p1, not dim & 1)
                gpio.write(pins.p2, not dim & 2)
                gpio.write(pins.p4, not dim & 4)
                gpio.write(pins.p8, not dim & 8)
                gpio.write(pins.p16, not dim & 16)
                gpio.write(pins.p32, not dim & 32)
                gpio.write(pins.p64, not dim & 64)
                gpio.write(pins.p128, not dim & 128)
            else:
                for p in pins.all_pins:
                    gpio.write(p, True)
            time.sleep(0.1)
    except Exception:
        logger.exception("Light thread encountered an error")
        raise
    finally:
        gpio.cleanup()


def web(state: LightState, esnooze: threading.Event, config: AppConfig) -> FastAPI:
    """FastAPI web application serving the UI and REST API."""
    app = FastAPI()

    @app.get("/")
    def docroot() -> FileResponse:
        """Serve the main index.html file."""
        return FileResponse(WWW_ROOT / "index.html")

    @app.get("/light/{sw}")
    def light_endpoint(sw: str) -> dict[str, Any]:
        if sw == "on":
            state.update(dim=100.0, on=True)
            return state.to_dict()
        if sw == "off":
            state.update(alarming=False, dim=0.0, on=False)
            return state.to_dict()
        raise HTTPException(status_code=400, detail="Invalid light setting.")

    @app.get("/alarm/{sw}")
    def alarm_endpoint(sw: str) -> dict[str, Any]:
        if sw == "on":
            state.update(alarmset=True)
            return state.to_dict()
        if sw == "off":
            if state.alarming:
                state.update(alarming=False, dim=0)
                esnooze.set()
            state.update(alarmset=False)
            return state.to_dict()
        raise HTTPException(status_code=400, detail="Invalid alarm setting.")

    @app.get("/alarmset/{t}")
    def alarmset_endpoint(t: str) -> dict[str, Any]:
        try:
            datetime.strptime(t, "%H:%M")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid time format.") from None
        state.update(alarmtime=t)
        return state.to_dict()

    @app.get("/snoozeset/{t}")
    def snoozeset_endpoint(t: int) -> dict[str, Any]:
        state.update(snoozetime=float(t))
        return state.to_dict()

    @app.get("/brightenset/{t}")
    def brightenset_endpoint(t: int) -> dict[str, Any]:
        state.update(brightentime=float(t))
        return state.to_dict()

    @app.get("/dim/{dimval}")
    def dim_endpoint(dimval: int) -> dict[str, Any]:
        state.update(on=True, dim=float(dimval))
        return state.to_dict()

    @app.get("/snooze")
    def snooze_endpoint() -> dict[str, Any]:
        esnooze.set()
        return state.to_dict()

    @app.get("/alarmoff")
    def alarmoff_endpoint() -> dict[str, Any]:
        state.update(alarming=False)
        esnooze.set()
        state.update(dim=100, on=True)
        return state.to_dict()

    @app.get("/stat")
    def stat_endpoint() -> dict[str, Any]:
        return state.to_dict()

    app.mount("/", StaticFiles(directory=str(WWW_ROOT)), name="static")

    return app


def main() -> None:
    """Application entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    config = AppConfig()
    state = LightState(
        snoozetime=config.alarm.snoozetime,
        brightentime=config.alarm.brightentime,
        alarmset=True,
        alarmtime=config.alarm.alarmtime,
    )
    esnooze = threading.Event()
    gpio = create_gpio()
    app = web(state, esnooze, config)

    threads: list[threading.Thread] = [
        threading.Thread(target=light, args=(state, gpio, config), name="light", daemon=True),
        threading.Thread(
            target=uvicorn.run,
            kwargs={"app": app, "host": config.web.host, "port": config.web.wwwport},
            name="web",
            daemon=True,
        ),
        threading.Thread(
            target=scheduler, args=(state, esnooze, config), name="scheduler", daemon=True
        ),
    ]

    for t in threads:
        t.start()

    try:
        while all(t.is_alive() for t in threads):
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down d.light...")
    finally:
        if isinstance(gpio, MockGPIO):
            gpio.cleanup()


if __name__ == "__main__":
    main()
