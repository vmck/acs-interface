#!/bin/bash -ex

if [ -z "$CI" ]; then
    cd /vagrant
else
    sudo -Hu vagrant cp ./examples/.env .
fi

which python
sudo which python
sudo -Hu vagrant which python
pipenv run which python

echo $PATH
sudo bash -c 'echo $PATH'
sudo -EHu vagrant bash -c 'echo $PATH'
pipenv run echo $PATH

sudo -Hu vagrant pipenv install --dev --ignore-pipfile
sudo -Hu vagrant mkdir -p data

container=$(docker ps -f name=minio -aq)
if [ -z "$container" ]; then (
    sudo -Hu vagrant pipenv run examples/minio.sh
) fi

container=$(docker ps -f name=database -aq)
if [ -z "$container" ]; then (
    sudo -Hu vagrant pipenv run examples/postgres.sh
) fi

sleep 2

sudo -Hu vagrant pipenv run ./manage.py migrate
sudo -Hu vagrant pipenv run ./manage.py storage_setup
sudo -Hu vagrant pipenv run ./manage.py collectstatic --noinput
sudo -Hu vagrant pipenv run ./manage.py loaddata ci/fixtures.json

echo "✔ acs-interface installed successfully"
