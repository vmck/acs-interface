#!/bin/bash -ex

cd /vagrant

exec pipenv run codecov -t
