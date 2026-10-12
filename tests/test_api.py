"""Tests for the HTTP API and the entry point."""

import pytest
import uvicorn
from fastapi.testclient import TestClient

from service_template import __main__ as entrypoint
from service_template import __version__
from service_template.api.app import create_app
from service_template.services.health import HealthService
from tests.conftest import FakeClock


def test_health_endpoint_returns_status(clock: FakeClock) -> None:
    client = TestClient(create_app(HealthService(clock, "9.9.9")))
    clock.advance(3)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "9.9.9", "uptime_seconds": 3.0}


def test_default_app_reports_package_version() -> None:
    response = TestClient(create_app()).get("/health")

    assert response.status_code == 200
    assert response.json()["version"] == __version__


def test_main_uses_host_and_port_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: dict[str, object] = {}

    def fake_run(app: object, host: str, port: int) -> None:
        calls.update(app=app, host=host, port=port)

    monkeypatch.setattr(uvicorn, "run", fake_run)
    monkeypatch.setenv("HOST", "0.0.0.0")  # noqa: S104 - only checks the value is passed through
    monkeypatch.setenv("PORT", "9000")

    entrypoint.main()

    assert calls["host"] == "0.0.0.0"  # noqa: S104
    assert calls["port"] == 9000


def test_main_defaults_to_localhost(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: dict[str, object] = {}
    monkeypatch.setattr(uvicorn, "run", lambda app, host, port: calls.update(host=host, port=port))
    monkeypatch.delenv("HOST", raising=False)
    monkeypatch.delenv("PORT", raising=False)

    entrypoint.main()

    assert calls == {"host": "127.0.0.1", "port": 8000}
