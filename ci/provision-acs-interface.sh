#!/bin/bash -e

sudo apt-get -qq install python3-pip
sudo pip3 install pipenv

cd /vagrant
pipenv install

echo "✔ acs-interface installed successfully"
