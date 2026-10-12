"""Shared test fixtures."""

from datetime import UTC, datetime, timedelta

import pytest


class FakeClock:
    """Clock whose time only moves when a test advances it."""

    def __init__(self, start: datetime) -> None:
        self.current = start

    def now(self) -> datetime:
        return self.current

    def advance(self, seconds: float) -> None:
        self.current += timedelta(seconds=seconds)


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock(datetime(2026, 10, 11, 12, 0, tzinfo=UTC))
