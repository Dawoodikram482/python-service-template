# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Layered package skeleton (`api`, `services`, `domain`, `adapters`) with a `/health` endpoint.
- Tooling: uv, ruff, mypy strict, pytest with an 80% coverage gate, poethepoet tasks.
- pre-commit hooks: ruff, mypy, gitleaks and file hygiene.
- Multi-stage Dockerfile running as a non-root user with a health check.
- GitHub Actions CI on Linux and Windows, plus a Docker build and smoke test.
- `scripts/rename.py` to turn the template into a new service.
