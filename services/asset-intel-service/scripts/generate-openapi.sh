#! /usr/bin/env bash

set -e
set -x

cd services/asset-intel-service
FASTAPI_ENV=development uv run python -c "import app.main; import json; print(json.dumps(app.main.app.openapi()))" > ../openapi.json
