"""Tests for configuration dataclasses."""

from __future__ import annotations

from config import AlarmConfig, AppConfig, DimConfig, PinConfig, WebConfig


class TestPinConfig:
    def test_default_pins(self) -> None:
        cfg = PinConfig()
        assert cfg.p1 == 5
        assert cfg.p128 == 21

    def test_all_pins_list(self) -> None:
        cfg = PinConfig()
        assert cfg.all_pins == [5, 6, 13, 19, 26, 16, 20, 21]


class TestDimConfig:
    def test_dimrange_computed(self) -> None:
        cfg = DimConfig(dimlow=10, dimhigh=50)
        assert cfg.dimrange == 40

    def test_default_dimrange(self) -> None:
        cfg = DimConfig()
        assert cfg.dimrange == 167


class TestAlarmConfig:
    def test_defaults(self) -> None:
        cfg = AlarmConfig()
        assert cfg.alarmtime == "07:00"
        assert cfg.brightentime == 15.0
        assert cfg.snoozetime == 5.0


class TestWebConfig:
    def test_defaults(self) -> None:
        cfg = WebConfig()
        assert cfg.wwwport == 8080
        assert cfg.host == "0.0.0.0"


class TestAppConfig:
    def test_composed_defaults(self) -> None:
        cfg = AppConfig()
        assert isinstance(cfg.pins, PinConfig)
        assert isinstance(cfg.dim, DimConfig)
        assert isinstance(cfg.alarm, AlarmConfig)
        assert isinstance(cfg.web, WebConfig)
