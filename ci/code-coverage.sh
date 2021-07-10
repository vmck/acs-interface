#!/bin/bash -ex

if [ -z "$CI" ]; then
    cd /vagrant
fi

echo "$CODECOV_TOKEN" | sudo tee .cc_token
curl https://codecov.io/bash --output codecov.sh
exec pipenv run bash codecov.sh -t @.cc_token
