#! /usr/bin/env bash

set -e
set -x

# Find all pyproject.toml files and run uvx uv-sort on them
find . -name "pyproject.toml" -exec uvx uv-sort {} \;