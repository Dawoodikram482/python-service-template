# python-service-template

[![CI](https://github.com/Dawoodikram482/python-service-template/actions/workflows/ci.yml/badge.svg)](https://github.com/Dawoodikram482/python-service-template/actions/workflows/ci.yml)
![Python 3.12](https://img.shields.io/badge/python-3.12-blue)
![mypy strict](https://img.shields.io/badge/mypy-strict-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

The starting point for every Python service in [Pit Wall](https://github.com/Dawoodikram482/agent-avenger),
an AI race strategist for Formula 1. It gives each new repo the same tooling, quality
gates and layout from the first commit.

## What's included

| Area | Tooling |
| --- | --- |
| Dependencies and environments | [uv](https://docs.astral.sh/uv/) with a committed lockfile |
| Lint and format | [ruff](https://docs.astral.sh/ruff/) |
| Types | [mypy](https://mypy.readthedocs.io/) in strict mode |
| Tests | pytest with branch coverage; the build fails below 80% |
| Tasks | [poethepoet](https://poethepoet.natn.io/): the same commands on Windows and Linux |
| Git hooks | pre-commit: ruff, mypy, gitleaks (secret scanning), file hygiene |
| Container | Multi-stage Dockerfile, non-root user, health check |
| CI | GitHub Actions on Linux and Windows, plus a Docker build and smoke test |
| Maintenance | Dependabot for Python packages, Actions and the Docker base image |

## Start a new service from this template

1. On GitHub, click **Use this template → Create a new repository**, or:

   ```bash
   gh repo create my-service --public --template Dawoodikram482/python-service-template --clone
   cd my-service
   ```

2. Rename the package (this also removes the rename script and regenerates `uv.lock`):

   ```bash
   uv run python scripts/rename.py my_service --description "What my service does"
   ```

3. Install the git hooks and check everything passes:

   ```bash
   uv run poe hooks
   uv run poe check
   ```

4. Update this README, then commit.

For a library rather than a service (for example `agent-core`), delete the `api/`
package, `__main__.py`, the `[project.scripts]` entry and the Dockerfile.

## Quickstart

Requires [uv](https://docs.astral.sh/uv/getting-started/installation/). uv installs Python 3.12 itself if needed.

```bash
uv sync              # create .venv with all dependencies
uv run poe check     # lint, type check and tests
uv run poe run       # start the service on http://127.0.0.1:8000
```

Then open <http://127.0.0.1:8000/health> or the API docs at <http://127.0.0.1:8000/docs>.

With Docker:

```bash
docker build -t service-template .
docker run --rm -p 8000:8000 service-template
```

## Tasks

Run `uv run poe` to list them.

| Task | What it does |
| --- | --- |
| `uv run poe check` | Everything CI runs: lint, type check, tests |
| `uv run poe lint` | ruff lint and format check |
| `uv run poe format` | Fix lint issues and format the code |
| `uv run poe typecheck` | mypy --strict on `src`, `tests` and `scripts` |
| `uv run poe test` | pytest with coverage |
| `uv run poe run` | Start the service |
| `uv run poe dev` | Start with auto-reload |
| `uv run poe hooks` | Install the pre-commit hooks |

## Project layout

```text
src/service_template/
├── api/         HTTP routes: turn requests into service calls
├── services/    Use cases: orchestrate domain logic through ports
├── domain/      Business models and ports (interfaces); depends on nothing else
├── adapters/    Implementations of ports: databases, HTTP clients, clocks
└── __main__.py  Entry point: python -m service_template
tests/           Unit and API tests
scripts/         One-off tooling (rename.py)
docs/adr/        Architecture decision records
```

Dependencies point inward: `api → services → domain ← adapters`. Services depend on
ports, not on adapters, so tests swap in fakes (see `FakeClock` in `tests/conftest.py`).

## Configuration

Copy `.env.example` to `.env` and adjust. `.env` is git-ignored.

| Variable | Default | Meaning |
| --- | --- | --- |
| `HOST` | `127.0.0.1` (Docker: `0.0.0.0`) | Address the server binds to |
| `PORT` | `8000` | Port the server listens on |

## Design decisions

- [ADR 1: Record architecture decisions](docs/adr/0001-record-architecture-decisions.md)
- [ADR 2: Use poethepoet as the task runner](docs/adr/0002-poethepoet-task-runner.md)

## License

[MIT](LICENSE)
