#!/bin/bash -ex

if [[ -d /opt/vmck ]]; then
    echo "✔ vmck already installed"
    exit 0
fi

(
    export NOMAD_ADDR=http://10.66.60.1:4646
    sudo docker cp cluster:/app/bin/nomad /usr/local/bin/nomad
    pushd "$(pwd)"
    cd /opt
    git clone https://github.com/vmck/vmck
    popd
    nomad job run ./ci/vmck.nomad
)

echo "✔ vmck installed successfully"
