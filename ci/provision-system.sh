#!/bin/bash -e

set -x
sudo apt-get update -qq
sudo apt-get install -qq docker.io git python3-pip libsasl2-dev python-dev libldap2-dev libssl-dev
sudo usermod -aG docker vagrant
sudo usermod -aG docker root
