#!/bin/bash -ex

if [ -z "$CI" ]; then
    cd /vagrant
fi

exec sudo -Hu vagrant pipenv run bash <(curl -s https://codecov.io/bash)
