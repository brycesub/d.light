"""Tests for the hardware abstraction layer."""

from __future__ import annotations

from config import AppConfig
from hardware import MockGPIO, create_gpio


class TestMockGPIO:
    def test_setup_initializes_pins_high(self, config: AppConfig) -> None:
        gpio = MockGPIO()
        gpio.setup(config.pins.all_pins)
        for pin in config.pins.all_pins:
            assert gpio.get_state()[pin] is True

    def test_write_changes_pin_state(self, config: AppConfig) -> None:
        gpio = MockGPIO()
        gpio.setup(config.pins.all_pins)
        gpio.write(config.pins.p1, False)
        assert gpio.get_state()[config.pins.p1] is False

    def test_cleanup_clears_state(self, config: AppConfig) -> None:
        gpio = MockGPIO()
        gpio.setup(config.pins.all_pins)
        gpio.cleanup()
        assert gpio.get_state() == {}


class TestCreateGPIO:
    def test_returns_mock_when_rpi_gpio_unavailable(self) -> None:
        gpio = create_gpio()
        assert isinstance(gpio, MockGPIO)
