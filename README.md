# V2 vmchecker
Rewrite of the [original vmchecker](https://vmchecker.cs.pub.ro/). This repo is
for the student portal. It runs at https://v2.vmchecker.cs.pub.ro/.

[![Build Status](https://jenkins.liquiddemo.org/api/badges/vmck/acs-interface/status.svg)](https://jenkins.liquiddemo.org/vmck/acs-interface)


## Development

Try the Vagrant method first. It requires [VirtualBox][] and [Vagrant][] to be
installed.

[VirtualBox]: https://www.virtualbox.org/
[Vagrant]: https://www.vagrantup.com/downloads.html


### Vagrant

If anything goes wrong, check out [bugs labelled "build"][], and please report
any bugs you encounter, that are not already documented.

[bugs labelled "build"]: https://github.com/vmck/acs-interface/labels/build

Clone the repo and run:

```shell
vagrant up
vagrant ssh
```

This should log you into the Vagrant virtual machine. Then start Django:

```shell
cd /vagrant
pipenv run ./manage.py runserver
```

Django's port is forwarded to http://localhost:8000. A few other useful ports
are forwarded too:

* vmck: http://localhost:10000
* minio: http://localhost:9000
* Nomad: http://localhost:4646
* Consul: http://localhost:8500
* Vault: http://localhost:8200


### Install locally

Install dependencies:
```shell
sudo apt-get update
sudo apt-get install libsasl2-dev python-dev libldap2-dev libssl-dev docker
sudo pip3 install pipenv
pipenv install
```

You need a running [vmck][] instance. Also a Nomad-Consul-Vault cluster is
required - [liquid/cluster][] - to run `vmck`.

[vmck]: https://github.com/vmck/vmck
[liquid-cluster]: https://github.com/liquidinvestigations/cluster

You need to set up some enviromental vars. For that, you can
create the file `.env` at the root of this project  where you
add your variabiles. The following example is enough to start you:

```
#DEBUG=True
MINIO_ACCESS_KEY=1234
MINIO_SECRET_KEY=123456789
VMCK_API_URL=http://www.example.com/v0/
```
Please add it to your `.env` file
Now run:

```shell
pipenv run ./examples/minio.sh
pipenv run ./manage.py migrate
pipenv run ./manage.py loaddata ci/fixtures.json
pipenv run ./manage.py runserver
```

Now the vmck/acs-interface is available at http://localhost:8000 and the minio
blob storage server at http://localhost:9000. You can log in with the user
`admin`, password `admin`. There is a test course and assignment created from
fixtures.

To stop, hit `CTRL-C` in the terminal where you started `runserver`, and
`docker stop storage` to stop the minio server.


## Deploy on cluster

The deployment is orchestrated at https://github.com/vmck/acs-deploy - it's the
living documentation and single instance of how to run this thing in
production.
