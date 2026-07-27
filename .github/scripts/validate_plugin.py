#!/usr/bin/env python3
"""Check that the plugin is well-formed before a release goes out."""

from __future__ import annotations

import json
import re
import sys
from collections.abc import Iterator
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLUGIN_ROOT = ROOT / "plugins" / "willskills"
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
PLUGIN = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


class Invalid(Exception):
    """A failure with a message ready to report."""


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        raise Invalid(f"{rel(path)}: missing") from None
    except json.JSONDecodeError as exc:
        raise Invalid(f"{rel(path)}: invalid JSON, {exc}") from None


def declared_name(path: Path) -> str | None:
    frontmatter = FRONTMATTER.match(path.read_text())
    if not frontmatter:
        return None

    for line in frontmatter.group(1).splitlines():
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip().strip("\"'")
    return None


def check_versions() -> Iterator[str]:
    """Both manifests carry a version, and consumers see both."""
    versions = {}

    for path in (MARKETPLACE, PLUGIN):
        try:
            version = read_json(path).get("version")
        except Invalid as exc:
            yield str(exc)
            continue

        if version is None:
            yield f"{rel(path)}: no version"
        elif not SEMVER.match(version):
            yield f"{rel(path)}: version {version!r} is not semver"
        else:
            versions[rel(path)] = version

    if len(set(versions.values())) > 1:
        yield f"manifests disagree on the version: {versions}"


def check_marketplace_entries() -> Iterator[str]:
    """Every plugin the marketplace advertises resolves to a manifest."""
    try:
        marketplace = read_json(MARKETPLACE)
    except Invalid:
        return  # check_versions already reported it

    for entry in marketplace.get("plugins", []):
        source = entry.get("source", "")
        if not (ROOT / source / ".claude-plugin" / "plugin.json").is_file():
            yield f"marketplace.json: {entry.get('name')!r} has no manifest at {source!r}"


def check_declared_names() -> Iterator[str]:
    """Skills are found by directory and agents by filename, so the two must agree."""
    skills = sorted((PLUGIN_ROOT / "skills").glob("*/SKILL.md"))
    agents = sorted((PLUGIN_ROOT / "agents").glob("*.md"))

    if not skills:
        yield "plugins/willskills/skills: no SKILL.md found"

    expected_names = [(skill, skill.parent.name) for skill in skills]
    expected_names += [(agent, agent.stem) for agent in agents]

    for path, expected in expected_names:
        name = declared_name(path)
        if name is None:
            yield f"{rel(path)}: no name in the frontmatter"
        elif name != expected:
            yield f"{rel(path)}: declares {name!r} but lives in {expected!r}"


CHECKS = (check_versions, check_marketplace_entries, check_declared_names)


def main() -> int:
    errors = [message for check in CHECKS for message in check()]

    if not errors:
        print("Plugin valid.")
        return 0

    print("Plugin validation failed:\n", file=sys.stderr)
    for error in errors:
        print(f"  - {error}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
