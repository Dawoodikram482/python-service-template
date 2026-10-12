"""Unit tests for the health check use case."""

from datetime import UTC, datetime

from service_template.adapters.clock import SystemClock
from service_template.domain.health import Status
from service_template.services.health import HealthService
from tests.conftest import FakeClock


def test_reports_ok_status_and_version(clock: FakeClock) -> None:
    status = HealthService(clock, "1.2.3").check()

    assert status.status is Status.OK
    assert status.version == "1.2.3"


def test_uptime_counts_from_start(clock: FakeClock) -> None:
    service = HealthService(clock, "1.2.3")
    clock.advance(42.5)

    assert service.check().uptime_seconds == 42.5


def test_uptime_never_negative_if_clock_goes_back(clock: FakeClock) -> None:
    service = HealthService(clock, "1.2.3")
    clock.advance(-10)

    assert service.check().uptime_seconds == 0.0


def test_system_clock_returns_aware_utc_time() -> None:
    now = SystemClock().now()

    assert now.tzinfo is UTC
    assert abs((datetime.now(UTC) - now).total_seconds()) < 5
