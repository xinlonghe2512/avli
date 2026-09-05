#! /usr/bin/env bash

set -e

docker-compose down -v --remove-orphans # Remove possibly previous broken stacks left hanging after an error

if [ $(uname -s) = "Linux" ]; then
    echo "Remove __pycache__ files"
    sudo find . -type d -name __pycache__ -exec rm -r {} \+
fi

docker-compose build
docker-compose up -d
docker-compose exec -T agent bash scripts/tests-start.sh "$@"
