#!/bin/bash

cd "$( dirname "${BASH_SOURCE[0]}" )"/..

docker run --rm -p 5432:5432 --name database --detach \
  --env "POSTGRES_DB=${POSTGRES_DB}" \
  --env "POSTGRES_USER=${POSTGRES_USER}" \
  --env "POSTGRES_PASSWORD=${POSTGRES_PASSWORD}" \
  postgres:12.0-alpine
