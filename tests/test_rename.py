"""Tests for scripts/rename.py. Removed by the script itself after a rename."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
IGNORE = shutil.ignore_patterns(
    ".git", ".venv", "*_cache", "__pycache__", "htmlcov", ".coverage*", "coverage.xml"
)


@pytest.fixture
def copy_of_repo(tmp_path: Path) -> Path:
    dest = tmp_path / "repo"
    shutil.copytree(REPO, dest, ignore=IGNORE)
    return dest


def run_rename(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603 - fixed arguments, runs our own script
        [sys.executable, str(repo / "scripts" / "rename.py"), *args, "--no-lock"],
        capture_output=True,
        text=True,
        check=False,
    )


def test_rename_moves_package_and_rewrites_names(copy_of_repo: Path) -> None:
    result = run_rename(copy_of_repo, "agent_core", "--description", 'Shared "LLM" gateway')

    assert result.returncode == 0, result.stderr
    assert (copy_of_repo / "src" / "agent_core" / "__init__.py").is_file()
    assert not (copy_of_repo / "src" / "service_template").exists()

    pyproject = (copy_of_repo / "pyproject.toml").read_text(encoding="utf-8")
    assert 'name = "agent-core"' in pyproject
    assert 'description = "Shared \\"LLM\\" gateway"' in pyproject

    old_names = ("service_template", "service-template")
    leftovers = [
        path.relative_to(copy_of_repo)
        for path in copy_of_repo.rglob("*")
        if path.is_file() and any(n in path.read_text(encoding="utf-8", errors="ignore") for n in old_names)
    ]
    assert leftovers == []


def test_rename_removes_template_only_files(copy_of_repo: Path) -> None:
    run_rename(copy_of_repo, "pitwall_ingest")

    assert not (copy_of_repo / "scripts").exists()
    assert not (copy_of_repo / "tests" / "test_rename.py").exists()
    assert '"scripts"' not in (copy_of_repo / "pyproject.toml").read_text(encoding="utf-8")


def test_rename_takes_owner_and_repo_from_origin_remote(copy_of_repo: Path) -> None:
    git = shutil.which("git")
    assert git is not None
    subprocess.run([git, "init", "-q"], cwd=copy_of_repo, check=True)  # noqa: S603
    subprocess.run(  # noqa: S603
        [git, "remote", "add", "origin", "https://github.com/some-owner/pitwall-ingest.git"],
        cwd=copy_of_repo,
        check=True,
    )

    result = run_rename(copy_of_repo, "pitwall_ingest")

    assert result.returncode == 0, result.stderr
    readme = (copy_of_repo / "README.md").read_text(encoding="utf-8")
    assert "github.com/some-owner/pitwall-ingest/actions" in readme
    assert "__GITHUB" + "_OWNER__" not in readme  # split so publishing never fills it in


def test_rename_flags_override_the_remote(copy_of_repo: Path) -> None:
    result = run_rename(copy_of_repo, "agent_core", "--owner", "octo", "--repo-name", "core-lib")

    assert result.returncode == 0, result.stderr
    readme = (copy_of_repo / "README.md").read_text(encoding="utf-8")
    assert "github.com/octo/core-lib/actions" in readme
    assert readme.startswith("# core-lib")


@pytest.mark.parametrize("bad_name", ["Agent-Core", "1agent", "class", "service_template"])
def test_rename_rejects_invalid_names(copy_of_repo: Path, bad_name: str) -> None:
    result = run_rename(copy_of_repo, bad_name)

    assert result.returncode != 0
    assert (copy_of_repo / "src" / "service_template").is_dir()
