#!/bin/bash -e

sudo apt-get update -qq
sudo apt-get -qq install python3-pip libsasl2-dev python-dev libldap2-dev libssl-dev fortune
sudo pip3 install pipenv


cd /vagrant
pipenv install --ignore-pipfile 2> /dev/null
mkdir -p data

container=$(docker ps -f name=minio -aq)
if [ -z $container ]; then (
  pipenv run examples/minio.sh
) fi

pipenv run ./manage.py migrate
pipenv run ./manage.py storage_setup
pipenv run ./manage.py collectstatic
pipenv run ./manage.py loaddata ci/fixtures.json

echo "✔ acs-interface installed successfully"
