"""Hardware abstraction layer for GPIO control with mock fallback."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class GPIOInterface(ABC):
    """Abstract interface for GPIO operations."""

    @abstractmethod
    def setup(self, pins: list[int]) -> None:
        """Configure the given pins as outputs."""

    @abstractmethod
    def write(self, pin: int, value: bool) -> None:
        """Write a digital value to a single pin."""

    @abstractmethod
    def cleanup(self) -> None:
        """Release all GPIO resources."""


class RealGPIO(GPIOInterface):
    """Concrete GPIO implementation using RPi.GPIO."""

    def __init__(self) -> None:
        import RPi.GPIO as GPIO

        self._gpio = GPIO
        self._gpio.setmode(GPIO.BCM)
        self._gpio.setwarnings(False)

    def setup(self, pins: list[int]) -> None:
        for pin in pins:
            self._gpio.setup(pin, self._gpio.OUT)

    def write(self, pin: int, value: bool) -> None:
        self._gpio.output(pin, value)

    def cleanup(self) -> None:
        self._gpio.cleanup()


class MockGPIO(GPIOInterface):
    """Mock GPIO implementation for development and testing off-hardware."""

    def __init__(self) -> None:
        self._pins: dict[int, bool] = {}
        logger.warning(
            "Running with MockGPIO — no physical hardware will be controlled. "
            "Install RPi.GPIO on a Raspberry Pi for real operation."
        )

    def setup(self, pins: list[int]) -> None:
        for pin in pins:
            self._pins[pin] = True  # default high (light off)
        logger.debug("MockGPIO setup pins: %s", pins)

    def write(self, pin: int, value: bool) -> None:
        self._pins[pin] = value
        logger.debug("MockGPIO pin %s -> %s", pin, "LOW" if value else "HIGH")

    def cleanup(self) -> None:
        self._pins.clear()
        logger.debug("MockGPIO cleanup")

    def get_state(self) -> dict[int, bool]:
        """Return current pin states for test assertions."""
        return self._pins.copy()


def create_gpio() -> GPIOInterface:
    """Factory that returns RealGPIO on a Pi, MockGPIO otherwise."""
    try:
        import RPi.GPIO  # type: ignore[import-untyped,unused-ignore]  # noqa: F401

        return RealGPIO()
    except (ImportError, RuntimeError):
        logger.info("RPi.GPIO not available; falling back to MockGPIO")
        return MockGPIO()
