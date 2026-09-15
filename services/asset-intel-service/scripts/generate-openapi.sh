#! /usr/bin/env bash

set -e
set -x

cd services/asset-intel-service
FASTAPI_ENV=development uv run python -c "import src.main; import json; print(json.dumps(src.main.src.openapi()))" > ../openapi.json
