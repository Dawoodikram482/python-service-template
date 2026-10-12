"""FastAPI application factory."""

from fastapi import FastAPI

from service_template import __version__
from service_template.adapters.clock import SystemClock
from service_template.domain.health import HealthStatus
from service_template.services.health import HealthService


def create_app(health_service: HealthService | None = None) -> FastAPI:
    """Build the FastAPI app.

    Args:
        health_service: Service behind ``GET /health``. Tests pass one with a fake clock;
            by default it uses the system clock and the package version.
    """
    service = health_service or HealthService(SystemClock(), __version__)
    app = FastAPI(title="service-template", version=__version__)

    @app.get("/health", tags=["ops"])
    def health() -> HealthStatus:
        """Report that the service is up, with its version and uptime."""
        return service.check()

    return app
