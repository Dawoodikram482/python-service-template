"""Health status of the service."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Status(StrEnum):
    """Overall state reported by the health check."""

    OK = "ok"


class HealthStatus(BaseModel):
    """Snapshot of the service's health, returned by ``GET /health``."""

    model_config = ConfigDict(frozen=True)

    status: Status
    version: str
    uptime_seconds: float = Field(ge=0)
