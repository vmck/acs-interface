#!/bin/bash -ex

cd /opt/acs-interface

echo '======= Setting up env variabiles... ======='
echo "DEBUG=true" >> .env
echo "MINIO_ACCESS_KEY=1234" >> .env
echo "MINIO_SECRET_KEY=123456789" >> .env
echo "MINIO_ADDRESS=10.42.1.1:9000" >> .env
echo "VMCK_API_URL=http://localhost:8000/v0" >> .env

echo '======= Starting minio... ======='
sudo pipenv run env
sudo pipenv run ./examples/minio.sh

echo '======= Run pytest... ======='
sudo touch data/db.sqlite3

sudo pipenv install
sudo pipenv run ./manage.py collectstatic
sudo pipenv run ./manage.py storage_setup
sudo pipenv run ./manage.py migrate
exec pipenv run pytest
