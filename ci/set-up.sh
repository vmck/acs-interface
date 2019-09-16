#!/bin/bash -ex

docker run --detach --restart always \
  --name vmck \
  --volume /opt/volumes/vmck/data:/opt/vmck/data \
  --env SECRET_KEY=TODO:ChangeME!!! \
  --env HOSTNAME=* \
  --env CONSUL_URL=http://10.42.1.1:8500 \
  --env NOMAD_URL=http://10.42.1.1:4646 \
  --env DEBUG=true \
  --env BACKEND=qemu \
  --env QEMU_IMAGE_PATH_PREFIX=http://10.42.1.1:10001\
  --env QEMU_CPU_MHZ=1000 \
  --publish 127.0.0.1:8000:8000 \
  vmck/vmck:api-update
