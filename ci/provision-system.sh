#!/bin/bash -ex

sudo apt-get update -yqq
sudo apt-get install -yqq python3-pip libsasl2-dev python-dev \
                        libldap2-dev libssl-dev libffi-dev fortune

if [ -z "$CI" ]; then
    sudo apt-get install -yqq docker.io git
    sudo -Hu vagrant curl https://pyenv.run | bash
    /home/vagrant/.pyenv/bin/pyenv install 3.7.10
else
    sudo useradd -m vagrant
    sudo usermod -aG sudo vagrant
    sudo chown -R vagrant:vagrant .
fi
sudo usermod -aG docker vagrant
sudo usermod -aG docker root

sudo pip3 install pipenv
