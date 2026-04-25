"""Tests for LightState thread safety and behavior."""

from __future__ import annotations

import threading

import pytest

from d_light import LightState


class TestLightState:
    def test_default_state(self) -> None:
        state = LightState()
        assert state.on is False
        assert state.dim == 0.0
        assert state.alarmset is True  # default dataclass value
        assert state.alarmtime == "07:00"

    def test_to_dict_snapshot(self) -> None:
        state = LightState(on=True, dim=50.0)
        d = state.to_dict()
        assert d["on"] is True
        assert d["dim"] == 50.0

    def test_update_single_field(self) -> None:
        state = LightState()
        state.update(dim=75.0)
        assert state.dim == 75.0
        assert state.on is False  # unchanged

    def test_update_multiple_fields(self) -> None:
        state = LightState()
        state.update(on=True, dim=100.0, alarmset=True)
        assert state.on is True
        assert state.dim == 100.0
        assert state.alarmset is True

    def test_update_invalid_field_raises(self) -> None:
        state = LightState()
        with pytest.raises(AttributeError):
            state.update(nonexistent=1)

    def test_thread_safety(self) -> None:
        state = LightState()
        errors: list[Exception] = []

        def updater() -> None:
            try:
                for i in range(100):
                    state.update(dim=float(i), on=i % 2 == 0)
                    _ = state.to_dict()
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=updater) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors
        assert isinstance(state.dim, float)
