#!/bin/bash -ex

sudo apt-get update -yqq
sudo apt-get install -yqq python3-pip libsasl2-dev python-dev \
                        libldap2-dev libssl-dev libffi-dev fortune

if [ -z "$CI" ]; then
    sudo usermod -aG sudo vagrant
    sudo apt-get install -yqq docker.io git
    curl https://pyenv.run | sudo -Hu vagrant bash
    sudo -Hu vagrant /home/vagrant/.pyenv/bin/pyenv install 3.8.10
else
    sudo useradd -m vagrant
    sudo usermod -aG sudo vagrant
    sudo chown -R vagrant .
    sudo chmod -R a+rwx .
fi
sudo usermod -aG docker vagrant
sudo usermod -aG docker root

pip3 install pipenv
