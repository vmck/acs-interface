#!/bin/bash -ex

if [ -z "$CI" ]; then
    cd /vagrant
    SUDO="sudo -Hu vagrant"
else
    cp ./examples/.env .
fi

$SUDO pipenv install --dev --ignore-pipfile
sudo -Hu vagrant mkdir -p data

container=$(docker ps -f name=minio -aq)
if [ -z "$container" ]; then (
    pipenv run examples/minio.sh
) fi

container=$(docker ps -f name=database -aq)
if [ -z "$container" ]; then (
    pipenv run examples/postgres.sh
) fi

sleep 2

$SUDO pipenv run ./manage.py migrate
$SUDO pipenv run ./manage.py storage_setup
$SUDO pipenv run ./manage.py collectstatic --noinput
$SUDO pipenv run ./manage.py loaddata ci/fixtures.json

echo "✔ acs-interface installed successfully"
