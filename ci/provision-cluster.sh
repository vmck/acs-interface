#!/bin/bash -ex

if [[ -d /opt/cluster ]]; then
    echo "✔ Cluster already installed"
    exit 0
fi

(
    cd /opt
    git clone https://github.com/vmck/cluster
    cd /opt/cluster
    cp examples/cluster.ini ./
    sed -i '/nomad_meta/a vmck_worker = true' cluster.ini
    sed -i '/^run_jobs =.*/c\run_jobs = dnsmasq' cluster.ini
    sudo chown -R vagrant:vagrant .
    sudo -u vagrant bin/docker.sh --rm --pull
    docker exec cluster ./cluster.py wait
)

echo "✔ Cluster installed successfully"
