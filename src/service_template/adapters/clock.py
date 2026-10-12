"""Clock adapter backed by the system time."""

from datetime import UTC, datetime


class SystemClock:
    """Implements :class:`~service_template.domain.ports.Clock` with the system clock."""

    def now(self) -> datetime:
        """Return the current time in UTC."""
        return datetime.now(UTC)
