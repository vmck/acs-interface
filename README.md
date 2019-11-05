# interface
UI for Vmchecker
[![Build Status](https://jenkins.liquiddemo.org/api/badges/vmck/acs-interface/status.svg)](https://jenkins.liquiddemo.org/vmck/acs-interface)

## Installation

You need `pipenv` and `docker` installed
```shell
sudo apt update && sudo apt install docker
pip3 install --user pipenv
```

To install dependencies:
```shell
sudo apt-get install libsasl2-dev python-dev libldap2-dev libssl-dev
pipenv install
```

You need a running vmck instance. You may use [vmck/vmck](https://github.com/vmck/vmck)
as a starting ground. Please refer to it on how to set it up.
Also a Nomad-Consul-Vault cluster is required [liquidinvestigations/cluster](https://github.com/liquidinvestigations/cluster) to run both `Vmck` and `ACS-Interface` along with the user submissions.

## Run

### Locally

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
./runinterface
```

Now the vmck/acs-interface is available at `localhost:8100` and the minio
blob storage server at `localhost:9000`. You can log in with the user `admin`,
password `admin`. There is a test course and assignment created from fixtures.

To stop `CTRL-C` in the terminal where you started to stop `vmck/acs-interface`
and `docker stop storage` to stop the minio server.

### Deploy on cluster

You must have the following `KV` pairs in your `Vault`:

#### For minio in `kv/minio`
    * access_key
    * secret_key

#### If you plan on using a LDAP add the following in `kv/ldap`
    * server_address
    * server_port
    * bind_dn
    * bind_password
    * user_tree
    * user_filter

#### To deploy it on the cluster:

```shell
export NOMAD_URL="http://${nomad_address}:${nomad_port}"
./deploy/cluster.py
```
