#!/bin/bash -ex

cd /vagrant

echo "MINIO_ADDRESS=10.66.60.1:9000
MINIO_ACCESS_KEY=1234
MINIO_SECRET_KEY=123456789
VMCK_API_URL=http://10.66.60.1:10000/v0/
DEBUG=True
HOSTNAME=*
ACS_INTERFACE_ADDRESS=http://10.66.60.1:8000/
MANAGER_TAG=vagrant-pytest" > .env

exec pipenv run pytest --cov-report=xml --cov=interface --liveserver 10.66.60.1:8000 testsuite
