#!/bin/bash

cd "$( dirname "${BASH_SOURCE[0]}" )"/..

docker run --rm -p 9000:9000 --name storage --detach \
  --volume $(pwd)/data/uploads:/data \
  --env "MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY}" \
  --env "MINIO_SECRET_KEY=${MINIO_SECRET_KEY}" \
  minio/minio server /data
