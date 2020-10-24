#!/bin/bash -ex

if [ -z "$CI" ]; then
    cd /vagrant
fi

sudo -Hu vagrant echo "$CODECOV_TOKEN" | sudo tee .cc_token
sudo -Hu vagrant curl https://codecov.io/bash --output codecov.sh
exec sudo -Hu vagrant pipenv run bash codecov.sh -t @.cc_token
