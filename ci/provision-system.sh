#!/bin/bash -e

set -x
apt-get update -qq
apt-get install -qq docker.io git python3-pip libsasl2-dev python-dev libldap2-dev libssl-dev
usermod -aG docker vagrant
usermod -aG docker root
