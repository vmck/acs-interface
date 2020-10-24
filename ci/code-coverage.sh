#!/bin/bash -ex

if [ -z "$CI" ]; then
    cd /vagrant
fi

curl https://codecov.io/bash --output codecov.sh
exec sudo -Hu vagrant pipenv run bash codecov.sh
