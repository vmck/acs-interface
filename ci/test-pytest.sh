#!/bin/bash -ex

cd /opt/acs-interface

echo 'Setting up env variabiles...'
echo "DEBUG=true" >> .env
echo "MINIO_ACCESS_KEY=1234" >> .env
echo "MINIO_SECRET_KEY=123456789" >> .env
echo "MINIO_ADDRESS=localhost:9000" >> .env
echo "VMCK_API_URL=http://localhost:8000/v0" >> .env

echo 'Starting minio...'
./examples/minio.sh

echo 'Run pytest...'
sudo pipenv install
exec pipenv run pytest
