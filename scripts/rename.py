"""Turn this template into a new service in one step.

Usage:
    python scripts/rename.py <package_name> [--description TEXT] [--repo-name NAME] [--owner NAME] [--no-lock]

Example:
    python scripts/rename.py agent_core --description "Shared LLM gateway and agent contract"

What it does:
    - renames the package directory ``src/service_template`` to ``src/<package_name>``,
    - replaces the template's names in every text file:
      ``service_template`` -> ``<package_name>``, ``service-template`` -> ``<package-name>``,
      and the template's ``<owner>/<repo>`` in GitHub links -> this repo's,
    - sets the project description in ``pyproject.toml`` when ``--description`` is given,
    - removes itself, its test and the then-empty ``scripts/`` folder,
    - regenerates ``uv.lock`` (unless ``--no-lock``).

The GitHub owner and repo name are read from the ``origin`` git remote, so nothing is
hardcoded. Without a remote, the repo name defaults to the package name with dashes and
the owner is left unchanged; ``--repo-name`` and ``--owner`` override both.
"""

from __future__ import annotations

import argparse
import keyword
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

OLD_PACKAGE = "service" + "_template"  # split so a repo-wide search for leftovers stays clean
OLD_DIST = "service" + "-template"
OLD_REPO = "python-" + OLD_DIST
OLD_TITLE = "Service" + " template"
OWNER_PLACEHOLDER = "__GITHUB" + "_OWNER__"

SKIP_DIRS = {
    ".git",
    ".venv",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    "__pycache__",
    "htmlcov",
    "node_modules",
}
TEMPLATE_ONLY_FILES = ("scripts/rename.py", "tests/test_rename.py")
PACKAGE_NAME = re.compile(r"^[a-z][a-z0-9_]*$")
GITHUB_REMOTE = re.compile(r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?/?$")
TEMPLATE_LINK = re.compile(r"github\.com/(?P<owner>[A-Za-z0-9_-]+)/" + re.escape(OLD_REPO))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Rename the template package.")
    parser.add_argument("package", help="new Python package name in snake_case, e.g. agent_core")
    parser.add_argument("--description", help="one-line project description for pyproject.toml")
    parser.add_argument("--repo-name", help="GitHub repo name (default: from the origin remote)")
    parser.add_argument("--owner", help="GitHub user or organisation (default: from the origin remote)")
    parser.add_argument("--no-lock", action="store_true", help="do not run 'uv lock' afterwards")
    return parser.parse_args(argv)


def validate_package_name(name: str) -> None:
    """Exit with an error if ``name`` is not a valid, new package name."""
    if not PACKAGE_NAME.fullmatch(name) or keyword.iskeyword(name):
        sys.exit(f"error: '{name}' is not a valid package name (use snake_case, e.g. agent_core)")
    if name == OLD_PACKAGE:
        sys.exit("error: choose a name different from the template's")


def origin_remote() -> tuple[str, str] | None:
    """Return ``(owner, repo)`` from the ``origin`` remote, or None if there is none."""
    try:
        url = subprocess.run(
            ["git", "remote", "get-url", "origin"],  # noqa: S607 - git resolved from PATH on purpose
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None
    match = GITHUB_REMOTE.search(url)
    return (match["owner"], match["repo"]) if match else None


def template_owner() -> str:
    """Return the GitHub owner the template's links point at (or the unfilled placeholder)."""
    readme = ROOT / "README.md"
    match = TEMPLATE_LINK.search(readme.read_text(encoding="utf-8")) if readme.is_file() else None
    return match["owner"] if match else OWNER_PLACEHOLDER


def text_files(root: Path) -> list[Path]:
    """Return every UTF-8 text file in the repo, skipping caches and virtual environments."""
    files = []
    for path in root.rglob("*"):
        if not path.is_file() or any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        try:
            path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        files.append(path)
    return files


def title_from(package: str) -> str:
    """Human-readable title from a package name: ``agent_core`` -> ``Agent core``."""
    return package.replace("_", " ").capitalize()


def build_replacements(package: str, repo: str, old_owner: str, owner: str) -> list[tuple[str, str]]:
    """Ordered (old, new) pairs: the most specific first, so shorter names don't clobber longer ones."""
    pairs = [
        (f"{old_owner}/{OLD_REPO}", f"{owner}/{repo}"),
        (OLD_REPO, repo),
        (OLD_DIST, package.replace("_", "-")),
        (OLD_PACKAGE, package),
        (OLD_TITLE, title_from(package)),
    ]
    if owner != old_owner:
        pairs.append((f"github.com/{old_owner}/", f"github.com/{owner}/"))
    return pairs


def rewrite(path: Path, replacements: list[tuple[str, str]]) -> bool:
    """Apply the replacements to one file. Return True if the file changed."""
    original = path.read_text(encoding="utf-8")
    updated = original
    for old, new in replacements:
        updated = updated.replace(old, new)
    if updated == original:
        return False
    path.write_text(updated, encoding="utf-8", newline="\n")
    return True


def set_description(pyproject: Path, description: str) -> None:
    """Replace the ``description = "..."`` line in pyproject.toml."""
    text = pyproject.read_text(encoding="utf-8")
    escaped = description.replace("\\", "\\\\").replace('"', '\\"')
    text = re.sub(r'(?m)^description = ".*"$', lambda _: f'description = "{escaped}"', text, count=1)
    pyproject.write_text(text, encoding="utf-8", newline="\n")


def remove_scripts_dir_if_empty() -> None:
    """Delete an empty ``scripts/`` folder and drop it from the ruff and mypy paths."""
    scripts = ROOT / "scripts"
    leftover = [p for p in scripts.iterdir() if p.name != "__pycache__"] if scripts.is_dir() else []
    if leftover:
        return
    shutil.rmtree(scripts, ignore_errors=True)
    pyproject = ROOT / "pyproject.toml"
    text = pyproject.read_text(encoding="utf-8").replace(', "scripts"]', "]")
    pyproject.write_text(text, encoding="utf-8", newline="\n")


def main(argv: list[str] | None = None) -> None:
    """Run the rename."""
    args = parse_args(argv)
    package: str = args.package
    validate_package_name(package)

    old_dir = ROOT / "src" / OLD_PACKAGE
    if not old_dir.is_dir():
        sys.exit(f"error: {old_dir} not found; was the template already renamed?")

    remote = origin_remote()
    old_owner = template_owner()
    owner: str = args.owner or (remote[0] if remote else old_owner)
    repo: str = args.repo_name or (remote[1] if remote else package.replace("_", "-"))
    replacements = build_replacements(package, repo, old_owner, owner)

    for file in TEMPLATE_ONLY_FILES:
        (ROOT / file).unlink(missing_ok=True)
    remove_scripts_dir_if_empty()

    changed = [p for p in text_files(ROOT) if rewrite(p, replacements)]
    shutil.move(old_dir, ROOT / "src" / package)
    if args.description:
        set_description(ROOT / "pyproject.toml", args.description)

    print(f"Renamed to package '{package}', repo '{owner}/{repo}'; updated {len(changed)} files.")

    if not args.no_lock:
        if shutil.which("uv") is None:
            print("uv not found: run 'uv lock' yourself.")
        else:
            subprocess.run(["uv", "lock"], cwd=ROOT, check=True)  # noqa: S607 - uv resolved from PATH on purpose

    print("Next: review the diff, update README.md, then commit.")


if __name__ == "__main__":
    main()
