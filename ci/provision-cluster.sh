#!/bin/bash -e

if [[ -d /opt/cluster ]]; then
  echo "✔ Cluster already installed"
  exit 0
fi

(
  set -x
  cd /opt
  sudo chown $(whoami) .
  git clone https://github.com/liquidinvestigations/cluster
  cd /opt/cluster
  git checkout example-no-default-jobs
  cp examples/cluster.ini ./
  sed -i '/nomad_meta/a vmck_worker = true' cluster.ini
  bin/docker.sh --rm --pull
  docker exec cluster ./cluster.py wait
)

echo "✔ Cluster installed successfully"
