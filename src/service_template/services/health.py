"""Health check use case."""

from service_template.domain.health import HealthStatus, Status
from service_template.domain.ports import Clock


class HealthService:
    """Reports the service's status, version and uptime."""

    def __init__(self, clock: Clock, version: str) -> None:
        """Create the service and record its start time.

        Args:
            clock: Source of the current time.
            version: Version string reported by the health check.
        """
        self._clock = clock
        self._version = version
        self._started_at = clock.now()

    def check(self) -> HealthStatus:
        """Return the current health status."""
        uptime = (self._clock.now() - self._started_at).total_seconds()
        return HealthStatus(status=Status.OK, version=self._version, uptime_seconds=max(uptime, 0.0))
