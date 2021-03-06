#!/bin/bash

cd "$( dirname "${BASH_SOURCE[0]}" )"/.. || exit 1

docker run \
  -p ${POSTGRES_PORT}:5432 \
  --name database \
  --detach \
  --restart always \
  --env "POSTGRES_DB=${POSTGRES_DB}" \
  --env "POSTGRES_USER=${POSTGRES_USER}" \
  --env "POSTGRES_PASSWORD=${POSTGRES_PASSWORD}" \
  postgres:12.0-alpine
