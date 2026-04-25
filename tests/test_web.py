"""Tests for FastAPI web API endpoints."""

from __future__ import annotations

import threading

import pytest
from fastapi.testclient import TestClient

from config import AppConfig
from d_light import LightState, web


@pytest.fixture
def test_app(state: LightState, config: AppConfig) -> TestClient:
    """Create a FastAPI TestClient wrapping the FastAPI app."""
    esnooze = threading.Event()
    app = web(state, esnooze, config)
    return TestClient(app)


class TestDocRoot:
    def test_serves_index_html(self, test_app: TestClient) -> None:
        resp = test_app.get("/")
        assert resp.status_code == 200
        assert "d.light" in resp.text


class TestLightEndpoint:
    def test_turn_on(self, test_app: TestClient, state: LightState) -> None:
        resp = test_app.get("/light/on")
        assert resp.status_code == 200
        assert resp.json()["on"] is True
        assert resp.json()["dim"] == 100.0
        assert state.on is True

    def test_turn_off(self, test_app: TestClient, state: LightState) -> None:
        state.update(on=True, dim=50.0)
        resp = test_app.get("/light/off")
        assert resp.status_code == 200
        assert resp.json()["on"] is False
        assert resp.json()["dim"] == 0.0
        assert state.alarming is False

    def test_invalid_setting(self, test_app: TestClient) -> None:
        resp = test_app.get("/light/invalid")
        assert resp.status_code == 400


class TestAlarmEndpoint:
    def test_enable(self, test_app: TestClient, state: LightState) -> None:
        state.update(alarmset=False)
        resp = test_app.get("/alarm/on")
        assert resp.json()["alarmset"] is True

    def test_disable(self, test_app: TestClient, state: LightState) -> None:
        state.update(alarmset=True, alarming=True)
        resp = test_app.get("/alarm/off")
        assert resp.json()["alarmset"] is False
        assert state.alarming is False

    def test_invalid_setting(self, test_app: TestClient) -> None:
        resp = test_app.get("/alarm/invalid")
        assert resp.status_code == 400


class TestAlarmSetEndpoint:
    def test_valid_time(self, test_app: TestClient, state: LightState) -> None:
        resp = test_app.get("/alarmset/08:30")
        assert resp.json()["alarmtime"] == "08:30"

    def test_invalid_time(self, test_app: TestClient) -> None:
        resp = test_app.get("/alarmset/25:00")
        assert resp.status_code == 400


class TestSnoozeSetEndpoint:
    def test_set_snooze(self, test_app: TestClient, state: LightState) -> None:
        resp = test_app.get("/snoozeset/10")
        assert resp.json()["snoozetime"] == 10.0


class TestBrightenSetEndpoint:
    def test_set_brighten(self, test_app: TestClient, state: LightState) -> None:
        resp = test_app.get("/brightenset/20")
        assert resp.json()["brightentime"] == 20.0


class TestDimEndpoint:
    def test_set_dim(self, test_app: TestClient, state: LightState) -> None:
        resp = test_app.get("/dim/42")
        assert resp.json()["dim"] == 42.0
        assert resp.json()["on"] is True


class TestSnoozeEndpoint:
    def test_snooze_sets_event(self, test_app: TestClient, state: LightState) -> None:
        resp = test_app.get("/snooze")
        assert resp.status_code == 200


class TestAlarmOffEndpoint:
    def test_alarmoff(self, test_app: TestClient, state: LightState) -> None:
        state.update(alarming=True)
        resp = test_app.get("/alarmoff")
        assert resp.json()["alarming"] is False
        assert resp.json()["on"] is True
        assert resp.json()["dim"] == 100


class TestStatEndpoint:
    def test_stat_returns_state(self, test_app: TestClient) -> None:
        resp = test_app.get("/stat")
        assert "on" in resp.json()
        assert "dim" in resp.json()
        assert "alarmtime" in resp.json()


class TestStaticFiles:
    def test_serves_css(self, test_app: TestClient) -> None:
        resp = test_app.get("/css/style.css")
        assert resp.status_code == 200
        assert "text/css" in resp.headers["content-type"]
