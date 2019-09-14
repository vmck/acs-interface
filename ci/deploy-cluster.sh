#!/bin/bash -ex

echo "Waiting for Docker..."
until docker version; do sleep 1; done

echo "Waiting for cluster autovault..."
docker exec cluster ./cluster.py wait
echo "Cluster provision done."
echo "Starting VMCK..."
docker exec cluster /bin/bash -c "\
cd /opt && \
git clone https://github.com/vmck/vmck.git &&\
cd vmck/examples &&\
./cluster.py && \
../ci/test-alive-on-cluster.sh"
echo "VMCK is up!"
