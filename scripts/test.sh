#! /usr/bin/env sh

set -e
set -x

docker compose build
docker compose down -v --remove-orphans # Remove possibly previous broken stacks left hanging after an error
docker compose up -d
docker compose exec -T agent bash scripts/tests-start.sh "$@"
docker compose down -v --remove-orphans
