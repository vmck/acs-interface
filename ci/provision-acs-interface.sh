#!/bin/bash -ex

if [ -z "$CI" ]; then
    cd /vagrant
else
    sudo -Hu vagrant cp ./examples/.env .
fi

sudo -EHu vagrant pipenv install --dev --ignore-pipfile
sudo -EHu vagrant mkdir -p data

container=$(docker ps -f name=minio -aq)
if [ -z "$container" ]; then (
    sudo -Hu vagrant pipenv run examples/minio.sh
) fi

container=$(docker ps -f name=database -aq)
if [ -z "$container" ]; then (
    sudo -Hu vagrant pipenv run examples/postgres.sh
) fi

sleep 2

sudo -EHu vagrant pipenv run ./manage.py migrate
sudo -EHu vagrant pipenv run ./manage.py storage_setup
sudo -EHu vagrant pipenv run ./manage.py collectstatic --noinput
sudo -EHu vagrant pipenv run ./manage.py loaddata ci/fixtures.json

echo "✔ acs-interface installed successfully"
