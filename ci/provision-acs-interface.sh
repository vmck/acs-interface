#!/bin/bash -e

apt-get update -qq
apt-get -qq install python3-pip libsasl2-dev python-dev libldap2-dev libssl-dev fortune
pip3 install pipenv


cd /vagrant
sudo -Hu vagrant pipenv install --ignore-pipfile 2> /dev/null
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

sudo -Hu vagrant pipenv run ./manage.py migrate
sudo -Hu vagrant pipenv run ./manage.py storage_setup
sudo -Hu vagrant pipenv run ./manage.py collectstatic --noinput
sudo -Hu vagrant pipenv run ./manage.py loaddata ci/fixtures.json

echo "✔ acs-interface installed successfully"
