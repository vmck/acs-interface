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

Clone the repo and create an `.env` file inside:

```env
MINIO_ADDRESS=10.66.60.1:9000
MINIO_ACCESS_KEY=1234
MINIO_SECRET_KEY=123456789
VMCK_API_URL=http://10.66.60.1:10000/v0/
DEBUG=True
HOSTNAME=*
ACS_INTERFACE_ADDRESS=http://10.66.60.1:8000
MANAGER_TAG=0.3.2
```

Now run:

```shell
vagrant up
```

If all goes well, it should print `✔ acs-interface installed successfully`.
Next, log you into the Vagrant virtual machine, and start Django:

```shell
vagrant ssh
cd /vagrant
pipenv run ./manage.py runserver 10.66.60.1:8000
```

Django's port is forwarded to http://localhost:8000. A default `admin` user is
created with password `admin`, along with some sample content.

Some more forwarded ports:

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

## Add new homework
1. You need to have access to the [admin page for V2 vmchecker](https://v2.vmchecker.cs.pub.ro/admin).
2. Click on adding a new *Assignment*
  - Select the course (mandatory field);
  - Add a code for the homework. It should respect a pattern, like `course_initials-homework_number`; example `pc-01`;
  - Give a name to the homework;
  - Set a maximum score (the minimum score is 0, if the total score is negative it will be clipped);
  - Add the soft and hard deadlines (mandatory fields);
  - Add a repo URL - when evaluating a homework the repo URL and the below specified branch will be used for testing;
  - Add a branch

The specified repository should contain the **tests** and the **checker script**.

It should also contain a **checker.sh** file (it does some unzip work) and a **config.ini** file (has specified the virtual machine where the homework would be run).

For a complete example on how the repo should look you could check [here](https://github.com/vmck/assignment/tree/pc-00).
