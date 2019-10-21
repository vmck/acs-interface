#!/bin/bash -e

if [[ -d /opt/vmck ]]; then
  echo "✔ vmck already installed"
  exit 0
fi

export NOMAD_ADDR=http://10.66.60.1:4646

(
  set -x
  sudo docker cp cluster:/app/bin/nomad /usr/local/bin/nomad
  cd /opt
  git clone https://github.com/vmck/vmck
  cd /opt/vmck
  nomad job run examples/vmck.nomad
)

echo "✔ vmck installed successfully"
