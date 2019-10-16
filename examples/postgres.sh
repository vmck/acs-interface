#!/bin/bash

cd "$( dirname "${BASH_SOURCE[0]}" )"/..

docker run --rm -p 5432:5432 --name database --detach \
  --volume $(pwd)/data/database/postgres/data:/var/lib/postgresql/data \
  --env "POSTGRES_DB=interface" \
  --env "POSTGRES_USER=${POSTGRES_USER}" \
  --env "POSTGRES_PASSWORD=${POSTGRES_PASSWORD}" \
  postgres:12.0-alpine
