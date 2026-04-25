"""Shared pytest fixtures."""

from __future__ import annotations

import pytest

from config import AppConfig
from d_light import LightState
from hardware import MockGPIO


@pytest.fixture
def config() -> AppConfig:
    """Default application configuration."""
    return AppConfig()


@pytest.fixture
def mock_gpio() -> MockGPIO:
    """Fresh MockGPIO instance."""
    return MockGPIO()


@pytest.fixture
def state(config: AppConfig) -> LightState:
    """LightState initialized with default config values."""
    return LightState(
        snoozetime=config.alarm.snoozetime,
        brightentime=config.alarm.brightentime,
        alarmset=True,
        alarmtime=config.alarm.alarmtime,
    )
