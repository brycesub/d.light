"""Application configuration with validation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PinConfig:
    """GPIO pin mapping for 8-bit dimming control."""

    p1: int = 5
    p2: int = 6
    p4: int = 13
    p8: int = 19
    p16: int = 26
    p32: int = 16
    p64: int = 20
    p128: int = 21

    @property
    def all_pins(self) -> list[int]:
        """Return all pin numbers as a list."""
        return [self.p1, self.p2, self.p4, self.p8, self.p16, self.p32, self.p64, self.p128]


@dataclass(frozen=True)
class DimConfig:
    """Dimming range configuration."""

    dimlow: int = 33
    dimhigh: int = 200

    @property
    def dimrange(self) -> int:
        """Computed dimming range."""
        return self.dimhigh - self.dimlow


@dataclass(frozen=True)
class AlarmConfig:
    """Alarm timing defaults."""

    alarmtime: str = "07:00"
    brightentime: float = 15.0
    snoozetime: float = 5.0


@dataclass(frozen=True)
class WebConfig:
    """Web server configuration."""

    wwwport: int = 8080
    host: str = "0.0.0.0"


@dataclass(frozen=True)
class AppConfig:
    """Top-level application configuration."""

    pins: PinConfig = PinConfig()
    dim: DimConfig = DimConfig()
    alarm: AlarmConfig = AlarmConfig()
    web: WebConfig = WebConfig()
