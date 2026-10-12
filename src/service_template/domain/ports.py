"""Ports: interfaces the domain needs from the outside world.

Adapters implement these, so services can be tested with fakes and
external systems can be swapped without touching business logic.
"""

from datetime import datetime
from typing import Protocol


class Clock(Protocol):
    """Source of the current time."""

    def now(self) -> datetime:
        """Return the current time as a timezone-aware datetime."""
        ...
