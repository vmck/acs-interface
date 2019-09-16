#!/bin/bash -ex

cd /opt
git clone https://github.com/vmck/vmck.git
cd vmck
git checkout api-update

echo "SECRET_KEY=TODO:ChangeME!!!" >> .env
echo "HOSTNAME=*" >> .env
echo "SSH_USERNAME=vagrant" >> .env
echo "CONSUL_URL=http://10.42.1.1:8500" >> .env
echo "NOMAD_URL=http://10.42.1.1:4646" >> .env
echo "VMCK_URL=http://localhost:8000" >> .env
echo "BACKEND=qemu" >> .env
echo "QEMU_CPU_MHZ=3000" >> .env
echo "QEMU_IMAGE_PATH_PREFIX=http://10.42.1.1:10001" >> .env

mkdir data
touch data/db.sqlite3

sudo pipenv install
sudo nohup pipenv run ./runvmck
