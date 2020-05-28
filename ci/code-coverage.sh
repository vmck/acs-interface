#!/bin/bash -ex

cd /vagrant

exec pipenv run bash <(curl -s https://codecov.io/bash)
