#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

ROOT = Path(__file__).resolve().parent.parent


def run(
    *args: str,
    check: bool = False,
    capture_output: bool = False,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=ROOT,
        check=check,
        text=True,
        capture_output=capture_output,
    )


def extract_packages(data: Any) -> set[str]:
    """Extract vulnerable package names from uv audit JSON."""

    packages: set[str] = set()

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            # Common package-name representations.
            for key in ("package", "package_name", "name"):
                package = value.get(key)

                if isinstance(package, str):
                    # Only treat it as a package when this object looks
                    # vulnerability-related.
                    if any(
                        key in value
                        for key in (
                            "id",
                            "advisory",
                            "vulnerability",
                            "severity",
                            "aliases",
                            "affected",
                        )
                    ):
                        packages.add(package)

            for child in value.values():
                visit(child)

        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(data)

    return packages


def main() -> int:
    print("=== Vulnerability Audit ===")

    with NamedTemporaryFile(
        mode="w+",
        suffix=".json",
        delete=False,
    ) as tmp:
        audit_file = Path(tmp.name)

    try:
        audit = run(
            "uv",
            "audit",
            "--no-dev",
            "--output-format",
            "json",
            capture_output=True,
        )

        audit_file.write_text(audit.stdout)

        # Always show the JSON output.
        if audit.stdout:
            print(audit.stdout, end="")

        if audit.stderr:
            print(audit.stderr, file=sys.stderr, end="")

        try:
            data = json.loads(audit.stdout)
        except json.JSONDecodeError:
            print(
                "\nERROR: uv audit did not return valid JSON.",
                file=sys.stderr,
            )
            return audit.returncode

        packages = extract_packages(data)

        if not packages:
            print("\n=== Dependency Paths ===")
            print("No vulnerable packages found.")
            return audit.returncode

        print("\n=== Dependency Paths ===")

        for package in sorted(packages):
            print(f"\n--- {package} ---")

            tree = run(
                "uv",
                "tree",
                "--invert",
                "--no-dev",
                "--package",
                package,
            )

            if tree.returncode != 0:
                print(
                    f"WARNING: failed to inspect dependency tree for {package}",
                    file=sys.stderr,
                )

        # Preserve uv audit's exit status.
        return audit.returncode

    finally:
        audit_file.unlink(missing_ok=True)


if __name__ == "__main__":
    sys.exit(main())
