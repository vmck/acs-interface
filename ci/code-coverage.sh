#!/bin/bash -ex

cd /vagrant

pipenv run bash <(curl -s https://codecov.io/bash)
