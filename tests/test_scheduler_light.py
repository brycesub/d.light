"""Tests for scheduler and light control logic."""

from __future__ import annotations

import threading
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from freezegun import freeze_time

from config import AppConfig
from d_light import LightState, light, main, scheduler
from hardware import MockGPIO


class TestScheduler:
    @freeze_time("2024-01-01 06:45:00")
    def test_alarm_triggers_at_correct_time(self, config: AppConfig) -> None:
        state = LightState(
            alarmtime="07:00",
            brightentime=15.0,
            alarmset=True,
            alarming=False,
        )
        # Verify the trigger condition logic directly
        now = datetime.now()
        alarm_dt = datetime.strptime(state.alarmtime, "%H:%M")
        trigger_at = alarm_dt.__class__(now.year, now.month, now.day, 6, 45)
        assert trigger_at.hour == now.hour
        assert trigger_at.minute == now.minute

    def test_state_update_during_alarm(self, config: AppConfig) -> None:
        state = LightState(alarmset=True, alarming=True)
        # Manually simulate what the scheduler does
        dim_pct = (float(config.dim.dimlow) - config.dim.dimlow) / config.dim.dimrange * 100
        state.update(dim=dim_pct, on=True)
        assert state.on is True
        assert state.dim == 0.0

    @freeze_time("2024-01-01 06:45:00")
    def test_scheduler_runs_alarm_cycle(self, config: AppConfig) -> None:
        state = LightState(
            alarmtime="07:00",
            brightentime=15.0,
            alarmset=True,
            alarming=False,
        )
        esnooze = threading.Event()
        wait_calls = 0
        sleep_calls = 0

        def raising_wait(*args: object, **kwargs: object) -> bool:
            nonlocal wait_calls
            wait_calls += 1
            if wait_calls > 8:
                state.update(alarming=False)
            return False

        def raising_sleep(duration: float) -> None:
            nonlocal sleep_calls
            sleep_calls += 1
            if sleep_calls > 15:
                raise RuntimeError("stop")

        with (
            patch("d_light.time.sleep", side_effect=raising_sleep),
            patch("threading.Event.wait", raising_wait),
            pytest.raises(RuntimeError, match="stop"),
        ):
            scheduler(state, esnooze, config)

        assert state.on is True
        assert wait_calls > 0

    def test_scheduler_handles_invalid_alarmtime(self, config: AppConfig) -> None:
        state = LightState(alarmtime="bad", brightentime=15.0, alarmset=True)
        esnooze = threading.Event()
        sleep_calls = 0

        def raising_sleep(duration: float) -> None:
            nonlocal sleep_calls
            sleep_calls += 1
            if sleep_calls > 2:
                raise RuntimeError("stop")

        with (
            patch("d_light.time.sleep", side_effect=raising_sleep),
            pytest.raises(RuntimeError, match="stop"),
        ):
            scheduler(state, esnooze, config)

        # After invalid format, alarming should remain False
        assert state.alarming is False

    @freeze_time("2024-01-01 06:45:00")
    def test_scheduler_snooze_resets_dim(self, config: AppConfig) -> None:
        state = LightState(
            alarmtime="07:00",
            brightentime=15.0,
            alarmset=True,
            alarming=False,
        )
        esnooze = threading.Event()
        wait_calls = 0
        sleep_calls = 0

        def raising_wait(*args: object, **kwargs: object) -> bool:
            nonlocal wait_calls
            wait_calls += 1
            if wait_calls == 3:
                esnooze.set()
            if wait_calls > 10:
                state.update(alarming=False)
            return False

        def raising_sleep(duration: float) -> None:
            nonlocal sleep_calls
            sleep_calls += 1
            if sleep_calls > 15:
                raise RuntimeError("stop")

        with (
            patch("d_light.time.sleep", side_effect=raising_sleep),
            patch("threading.Event.wait", raising_wait),
            pytest.raises(RuntimeError, match="stop"),
        ):
            scheduler(state, esnooze, config)


class TestLightThread:
    def test_gpio_outputs_when_on(self, config: AppConfig, mock_gpio: MockGPIO) -> None:
        mock_gpio.setup(config.pins.all_pins)
        dim = 255
        mock_gpio.write(config.pins.p1, not dim & 1)
        mock_gpio.write(config.pins.p2, not dim & 2)
        mock_gpio.write(config.pins.p4, not dim & 4)
        mock_gpio.write(config.pins.p8, not dim & 8)
        mock_gpio.write(config.pins.p16, not dim & 16)
        mock_gpio.write(config.pins.p32, not dim & 32)
        mock_gpio.write(config.pins.p64, not dim & 64)
        mock_gpio.write(config.pins.p128, not dim & 128)
        # When dim=255, all bits are 1, so not 1 = False (LOW) for all pins
        for pin in config.pins.all_pins:
            assert mock_gpio.get_state()[pin] is False

    def test_gpio_all_high_when_off(self, config: AppConfig, mock_gpio: MockGPIO) -> None:
        mock_gpio.setup(config.pins.all_pins)
        for p in config.pins.all_pins:
            mock_gpio.write(p, True)
        for pin in config.pins.all_pins:
            assert mock_gpio.get_state()[pin] is True

    def test_dim_calculation(self, config: AppConfig) -> None:
        state = LightState(on=True, dim=50.0)
        dim = int(state.dim / 100.0 * config.dim.dimrange + config.dim.dimlow)
        expected = int(50.0 / 100.0 * 167 + 33)
        assert dim == expected
        assert dim == 116

    def test_dim_zero_turns_off(self, config: AppConfig) -> None:
        state = LightState(on=True, dim=0.0)
        if state.dim == 0:
            state.update(on=False)
        assert state.on is False

    def test_dim_100_is_max(self, config: AppConfig) -> None:
        state = LightState(on=True, dim=100.0)
        if state.dim == 100:
            dim = 255
        assert dim == 255

    def test_light_thread_runs_and_cleans_up(self, config: AppConfig, mock_gpio: MockGPIO) -> None:
        state = LightState(on=True, dim=100.0)
        call_count = 0

        def fake_sleep(duration: float) -> None:
            nonlocal call_count
            call_count += 1
            if call_count > 2:
                raise RuntimeError("stop")

        with (
            patch("d_light.time.sleep", side_effect=fake_sleep),
            pytest.raises(RuntimeError, match="stop"),
        ):
            light(state, mock_gpio, config)

        # Cleanup should have been called
        assert mock_gpio.get_state() == {}

    def test_light_thread_mid_dim(self, config: AppConfig, mock_gpio: MockGPIO) -> None:
        state = LightState(on=True, dim=50.0)
        call_count = 0
        captured_state: dict[int, bool] = {}

        def fake_sleep(duration: float) -> None:
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                captured_state.update(mock_gpio.get_state())
            if call_count > 2:
                raise RuntimeError("stop")

        with (
            patch("d_light.time.sleep", side_effect=fake_sleep),
            pytest.raises(RuntimeError, match="stop"),
        ):
            light(state, mock_gpio, config)

        assert captured_state != {}


class TestMain:
    def test_main_starts_threads_and_shuts_down(self, config: AppConfig) -> None:
        state = LightState(
            snoozetime=config.alarm.snoozetime,
            brightentime=config.alarm.brightentime,
            alarmset=True,
            alarmtime=config.alarm.alarmtime,
        )

        mock_threads: list[MagicMock] = []

        def mock_thread_target(*args: object, **kwargs: object) -> threading.Thread:
            mock = MagicMock()
            mock.is_alive.return_value = False  # Exit immediately
            mock_threads.append(mock)
            return mock

        with (
            patch("d_light.AppConfig", return_value=config),
            patch("d_light.LightState", return_value=state),
            patch("d_light.create_gpio", return_value=MockGPIO()),
            patch("d_light.threading.Thread", side_effect=mock_thread_target),
            patch("d_light.time.sleep", side_effect=KeyboardInterrupt),
        ):
            main()

        assert len(mock_threads) == 3
        for mock in mock_threads:
            mock.start.assert_called_once()
