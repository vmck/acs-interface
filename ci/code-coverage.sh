#!/bin/bash -ex

cd /vagrant

exec pipenv run codecov --token=$CODECOV_TOKEN
