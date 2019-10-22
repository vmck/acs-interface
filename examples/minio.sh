#!/bin/bash

cd "$( dirname "${BASH_SOURCE[0]}" )"/..

docker run --rm \
  --restart always \
  --name storage \
  --detach \
  --volume $(pwd)/data/uploads:/data \
  --env "MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY}" \
  --env "MINIO_SECRET_KEY=${MINIO_SECRET_KEY}" \
  -p 9000:9000 \
  minio/minio server /data
