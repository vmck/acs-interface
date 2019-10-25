#!/bin/bash -e

sudo apt-get update -qq
sudo apt-get -qq install python3-pip libsasl2-dev python-dev libldap2-dev libssl-dev
sudo pip3 install pipenv


cd /vagrant
pipenv install --ignore-pipfile 2> /dev/null
mkdir -p data

container=$(docker ps -f name=minio -aq)
if [ -z $container ]; then (
  pipenv run examples/minio.sh
) fi

pipenv run python manage.py migrate
pipenv run python manage.py storage_setup

echo "✔ acs-interface installed successfully"
